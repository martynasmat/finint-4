from alpaca.common import APIError
from alpaca.data import Quote
from alpaca.data.live import StockDataStream
from alpaca.trading import TradingClient
from alpaca.trading.enums import AssetClass
from requests.exceptions import RequestException


class RealtimeData:
    def __init__(
            self,
            api_key: str,
            api_secret: str,
            ticker: str,
            trading_client: TradingClient = None,
            *,
            quiet: bool = False,
    ):
        self.stream = StockDataStream(
            api_key,
            api_secret,
        )
        self.ticker = ticker
        self.client = trading_client or TradingClient(api_key, api_secret, paper=True)
        self.quiet = quiet
        self.asset_data = None
        self.error = None

        self.ask = None
        self.bid = None
        self.mid = None
        self.latest_quote = None

    async def quote_handler(self, data: Quote):
        # Update ask, bid and midpoint prices on every new quote
        self.ask = data.ask_price
        self.bid = data.bid_price
        self.mid = (data.ask_price + data.bid_price) / 2
        self.latest_quote = (self.bid, self.ask, self.mid)
        if not self.quiet:
            print(self.ask, self.bid, round(self.mid, 2))

    def run(self):
        try:
            self.asset_data = self.client.get_asset(self.ticker)
            if self.asset_data.asset_class != AssetClass.US_EQUITY:
                self.error = f"{self.ticker} is not a US stock ticker."
                if not self.quiet:
                    print(self.error)
                return
            self.stream.subscribe_quotes(self.quote_handler, self.ticker)
            self.stream.run()
        except (APIError, RequestException) as error:
            if isinstance(error, APIError) and error.status_code == 404:
                self.error = f"Ticker {self.ticker} was not found on Alpaca."
            else:
                self.error = "Could not load real-time data from Alpaca."
            if not self.quiet:
                print(error)

    def stop(self):
        self.stream.stop()
