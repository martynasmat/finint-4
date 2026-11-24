import dotenv
import os
from alpaca.trading.client import TradingClient
from alpaca.data import TimeFrame
import datetime as dt

from historical import HistoricalData
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
        "qwd",
        trading_client,
    )
    realtime_data.run()

    historical_data = HistoricalData(
        os.getenv("ALPACA_API_KEY"),
        os.getenv("ALPACA_SECRET"),
        ["AAPL", "MSFT"],
        trading_client,
        start=dt.datetime(2023, 1, 1),
        end=dt.datetime(2023, 1, 10),
        bar_data=False,
        bar_timeframe=TimeFrame.Day,
    )
    historical_data.fetch()
    historical_data.save()

if __name__ == "__main__":
    main()