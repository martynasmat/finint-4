from alpaca.data import StockHistoricalDataClient, StockBarsRequest, TimeFrame
import datetime as dt


class HistoricalData:
    def __init__(
            self,
            api_key: str,
            api_secret: str,
            tickers: str | list[str],
            start: datetime.date,
            end: datetime.date,
            bar_data: bool = False,
            bar_timeframe: TimeFrame = TimeFrame.Hour,
    ):
        if not tickers:
            print("No ticker(s) provided")
            return

        if not api_key or not api_secret:
            print("A valid Alpaca API key and secret are required")
            return

        if not start or not end:
            print("A valid start and end date are required")
            return

        self.client = StockHistoricalDataClient(
            api_key,
            api_secret,
        )
