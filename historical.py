from alpaca.data import StockHistoricalDataClient, StockBarsRequest

class HistoricalData:
    def __init__(
            self,
            api_key: str,
            api_secret: str,
            tickers: str | list[str],
    ):
        if not tickers:
            print("No ticker(s) provided")
            return

        if not api_key or not api_secret:
            print("A valid Alpaca API key and secret are required")
            return

        self.client = StockHistoricalDataClient(
            api_key,
            api_secret,
        )
