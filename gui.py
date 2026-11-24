import curses
from threading import Thread
import dotenv

from account import Account
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


def show_menu(screen, title, options, footer, bal):
    lines = [f"{number}. {option}" for number, option in enumerate(options, start=1)]

    while True:
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

        key = screen.getch()
        if key == 27:
            return None

        index = key - ord("1")
        if 0 <= index < len(options):
            return options[index]


def show_order_menu(screen, bal):
    while True:
        choice = show_menu(
            screen, "Place order", ORDER_OPTIONS, "[Esc] - Back to main menu", bal
        )
        if choice is None:
            return


def main(screen, bal):
    screen.timeout(250)
    while True:
        choice = show_menu(screen, "4 namų darbas", MAIN_OPTIONS, "[Esc] - Exit", bal)
        if choice is None:
            return
        if choice == "Place order":
            show_order_menu(screen, bal)


if __name__ == "__main__":
    dotenv.load_dotenv()
    account = Account(os.getenv("ALPACA_API_KEY"), os.getenv("ALPACA_SECRET"))
    balances = {"equity": account.get_equity(), "cash": account.get_cash()}

    Thread(target=poll_account, args=(account, balances), daemon=True).start()

    curses.wrapper(main, balances)
