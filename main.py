import dotenv
import os
from alpaca.trading.client import TradingClient
from realtime import RealtimeData

async def quote_data_handler(data):
    print(data)

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

    realtime_data = RealtimeData(
        os.getenv("ALPACA_API_KEY"),
        os.getenv("ALPACA_SECRET"),
        "",
    )
    realtime_data.run()

if __name__ == "__main__":
    main()