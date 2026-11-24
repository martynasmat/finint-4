import dotenv
import os
from alpaca.trading.client import TradingClient

def main():
    dotenv.load_dotenv()
    trading_client = TradingClient(
        os.getenv("ALPACA_API_KEY"),
        os.getenv("ALPACA_SECRET"),
        paper=True,
    )
    account = trading_client.get_account()
    print(account.equity)
    print(account.cash)

if __name__ == "__main__":
    main()