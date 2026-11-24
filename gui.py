import curses
from datetime import datetime, timedelta, timezone
from pathlib import Path
from textwrap import wrap
from threading import Thread
import dotenv
from alpaca.trading.client import TradingClient
from requests.exceptions import RequestException

from account import Account
from historical import HistoricalData
from realtime import RealtimeData
import os


MAIN_OPTIONS = (
    "Get real-time data",
    "Get historical data",
    "Place order",
    "Your orders",
)
ORDER_OPTIONS = ("Market order", "Limit order")
ENTER_KEYS = (10, 13, curses.KEY_ENTER)


def poll_account(acc: Account, bal: dict):
    while True:
        acc.update()
        bal["equity"], bal["cash"] = acc.equity, acc.cash
        sleep(10)


def draw_screen(screen, title, lines, footer, bal):
    screen.erase()
    height, width = screen.getmaxyx()
    if width > 1:
        screen.addnstr(0, 0, title, width - 1, curses.A_BOLD)
        for row, line in enumerate(lines, start=2):
            if row >= height - 2:
                break
            screen.addnstr(row, 0, line, width - 1)
        if height >= 3:
            equity = bal["equity"] or "unavailable"
            cash = bal["cash"] or "unavailable"
            screen.addnstr(height - 2, 0, f"Equity: {equity} | Cash: {cash}", width - 1)
        if height >= 2:
            screen.addnstr(height - 1, 0, footer, width - 1)
    screen.refresh()


def show_menu(screen, title, options, footer, bal):
    lines = [f"{number}. {option}" for number, option in enumerate(options, start=1)]
    while True:
        draw_screen(screen, title, lines, footer, bal)
        key = screen.getch()
        if key == 27:
            return None

        index = key - ord("1")
        if 0 <= index < len(options):
            return options[index]


def prompt_ticker(screen, bal, multiple=False):
    title = "Get historical data" if multiple else "Get real-time data"
    label = "Stock tickers (comma-separated)" if multiple else "Stock ticker"
    separators = ".-, " if multiple else ".-"
    ticker = ""
    while True:
        draw_screen(
            screen,
            title,
            [f"{label}: {ticker}"],
            "[Enter] - View data  [Esc] - Back",
            bal
        )
        key = screen.getch()
        if key == 27:
            return None
        if key in ENTER_KEYS and ticker.strip(" ,"):
            return ticker
        if key in (8, 127, curses.KEY_BACKSPACE):
            ticker = ticker[:-1]
        elif 32 <= key <= 126:
            character = chr(key)
            if character.isalnum() or character in separators:
                ticker += character.upper()


def asset_lines(asset):
    return [
        f"Company: {asset.name}",
        f"Listing exchange: {asset.exchange.value}",
        f"Status: {asset.status.value} | Tradable: {'Yes' if asset.tradable else 'No'}",
    ]


def show_realtime(screen, bal, key, secret):
    while True:
        ticker = prompt_ticker(screen, bal)
        if ticker is None:
            return

        realtime = RealtimeData(key, secret, ticker, quiet=True)
        worker = Thread(target=realtime.run, daemon=True)
        worker.start()
        while True:
            lines = []
            asset = realtime.asset_data
            if asset is not None:
                lines.extend([*asset_lines(asset), ""])

            error = realtime.error
            quote = realtime.latest_quote
            footer = "[Esc] - Back to main menu"
            if error:
                lines.append(error)
                footer = f"[Enter] - Try again  {footer}"
            elif not worker.is_alive():
                lines.append("Quote stream ended.")
            elif asset is None:
                lines.append("Looking up ticker...")
            elif quote is None:
                lines.append("Waiting for quote...")
            else:
                bid, ask, mid = quote
                lines.append(f"Bid: {bid:.2f} | Ask: {ask:.2f} | Mid: {mid:.2f}")

            draw_screen(screen, f"Real-time data: {ticker}", lines, footer, bal)
            pressed = screen.getch()
            if pressed == 27:
                return
            if error and pressed in ENTER_KEYS:
                break


def fetch_history(historical, result):
    try:
        historical.fetch()
        if historical.data is None:
            missing = next((ticker for ticker in historical.tickers if ticker not in historical.asset_data), None)
            result["error"] = (
                f"Could not look up ticker {missing}." if missing else "Could not fetch historical data."
            )
            return
        if historical.data.df.empty:
            result["error"] = "No historical data for this request."
            return

        filename = historical.save()
    except RequestException:
        result["error"] = "Could not fetch historical data."
        return
    except OSError:
        result["error"] = "Could not save to CSV."
        return

    result["path"] = filename


def show_historical(screen, bal, key, secret):
    trading_client = TradingClient(key, secret, paper=True)
    title = "Historical data (1h OHLC, last 30 days)"
    while True:
        entered = prompt_ticker(screen, bal, multiple=True)
        if entered is None:
            return
        tickers = [ticker.strip() for ticker in entered.split(",")]
        tickers = list(dict.fromkeys(ticker for ticker in tickers if ticker))
        end = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        historical = HistoricalData(
            key,
            secret,
            tickers,
            trading_client,
            end - timedelta(days=30),
            end,
            bar_data=True,
        )
        result = {}
        Thread(target=fetch_history, args=(historical, result), daemon=True).start()

        offset = 0
        error_shown = False
        while True:
            height, width = screen.getmaxyx()
            error = result.get("error")
            path = result.get("path")
            footer = "[Esc] - Back to main menu"
            if error:
                if not error_shown:
                    screen.clearok(True)
                    error_shown = True
                status = [error]
                footer = f"[Enter] - Try again  {footer}"
            elif path is not None:
                path_lines = wrap(str(path), width=max(1, width - 1), drop_whitespace=False)
                status = ["Saved CSV:", *path_lines]
            else:
                status = ["Loading..."]

            assets = []
            for ticker, asset in historical.asset_data.copy().items():
                assets.extend([ticker, *asset_lines(asset), ""])
            visible_rows = max(0, height - 5 - len(status))
            last_offset = max(0, len(assets) - visible_rows)
            offset = min(offset, last_offset)
            if last_offset and visible_rows:
                footer = f"{footer}  [Up/Down] - Scroll"

            draw_screen(screen, title, [*status, "", *assets[offset:offset + visible_rows]], footer, bal)
            pressed = screen.getch()
            if pressed == 27:
                return
            if error and pressed in ENTER_KEYS:
                break
            if pressed == curses.KEY_DOWN:
                offset = min(offset + 1, last_offset)
            elif pressed == curses.KEY_UP:
                offset = max(0, offset - 1)


def show_order_menu(screen, bal):
    while True:
        choice = show_menu(
            screen, "Place order", ORDER_OPTIONS, "[Esc] - Back to main menu", bal
        )
        if choice is None:
            return


def main(screen, bal, key, secret):
    screen.timeout(250)
    while True:
        choice = show_menu(screen, "4 namų darbas", MAIN_OPTIONS, "[Esc] - Exit", bal)
        if choice is None:
            return
        if choice == "Get real-time data":
            show_realtime(screen, bal, key, secret)
        elif choice == "Get historical data":
            show_historical(screen, bal, key, secret)
        elif choice == "Place order":
            show_order_menu(screen, bal)


if __name__ == "__main__":
    dotenv.load_dotenv()
    api_key = os.getenv("ALPACA_API_KEY")
    api_secret = os.getenv("ALPACA_SECRET")
    account = Account(api_key, api_secret)
    balances = {"equity": account.get_equity(), "cash": account.get_cash()}

    Thread(target=poll_account, args=(account, balances), daemon=True).start()

    curses.wrapper(main, balances, api_key, api_secret)
