from alpaca.common import APIError
from alpaca.data import StockHistoricalDataClient, StockTradesRequest, StockBarsRequest, TimeFrame, BaseBarsRequest
import datetime as dt
import os

from alpaca.trading import TradingClient


class HistoricalData:
    def __init__(
            self,
            api_key: str,
            api_secret: str,
            tickers: str | list[str],
            trading_client: TradingClient,
            start: dt.datetime,
            end: dt.datetime,
            bar_data: bool = False,
            bar_timeframe: TimeFrame = TimeFrame.Hour,
    ):
        if not tickers:
            print("No ticker(s) provided")
            return

        self.client = StockHistoricalDataClient(
            api_key,
            api_secret,
        )
        self.trading_client = trading_client

        # Normalize tickers because it can be a string or a list of strings
        self.tickers = [tickers] if isinstance(tickers, str) else tickers
        self.asset_data = dict()
        self.start = start
        self.end = end
        self.bar_data = bar_data
        self.bar_timeframe = bar_timeframe

        self.data = None
        self.save_path = "data/"

    def fetch(self):
        try:
            for ticker in self.tickers:
                self.asset_data[ticker] = self.trading_client.get_asset(ticker)

            if self.bar_data:
                req = StockBarsRequest(
                    symbol_or_symbols = self.tickers,
                    timeframe = self.bar_timeframe,
                    start = self.start,
                    end = self.end,
                )

                self.data = self.client.get_stock_bars(req)
            else:
                req = StockTradesRequest(
                    symbol_or_symbols=self.tickers,
                    start=self.start,
                    end=self.end,
                )

                self.data = self.client.get_stock_trades(req)
        except APIError as e:
            print(e)
            return

    def save(self):
        os.makedirs(self.save_path, exist_ok=True)
        if self.data is not None:
            self.data.df.to_csv(
                self.save_path +
                '_'.join(self.tickers) +
                '_' + self.start.strftime("%Y-%m-%d") +
                '_' + self.end.strftime("%Y-%m-%d") +
                '_' + self.bar_timeframe.value +
                ".csv"
            )
        else:
            print("No data to save")
            return
