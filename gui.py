import curses
from threading import Thread
import dotenv

from account import Account
from realtime import RealtimeData
import os


MAIN_OPTIONS = (
    "Get real-time data",
    "Get historical data",
    "Place order",
    "Your orders",
)
ORDER_OPTIONS = ("Market order", "Limit order")


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


def prompt_ticker(screen, bal):
    ticker = ""
    while True:
        draw_screen(
            screen,
            "Get real-time data",
            [f"Stock ticker: {ticker}"],
            "[Enter] - View data  [Esc] - Back",
            bal
        )
        key = screen.getch()
        if key == 27:
            return None
        if key in (10, 13, curses.KEY_ENTER) and ticker:
            return ticker
        if key in (8, 127, curses.KEY_BACKSPACE):
            ticker = ticker[:-1]
        elif 32 <= key <= 126:
            character = chr(key)
            if character.isalnum() or character in ".-":
                ticker += character.upper()


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
                lines.extend([
                    f"Company: {asset.name}",
                    f"Listing exchange: {asset.exchange.value}",
                    f"Status: {asset.status.value} | Tradable: {'Yes' if asset.tradable else 'No'}",
                    "",
                ])

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
            if error and pressed in (10, 13, curses.KEY_ENTER):
                break


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
