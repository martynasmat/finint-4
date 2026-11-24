from alpaca.common import APIError
from alpaca.data import Quote
from alpaca.data.live import StockDataStream
from alpaca.trading import TradingClient

class RealtimeData:
    def __init__(
            self,
            api_key: str,
            api_secret: str,
            ticker: str,
    ):
        self.stream = StockDataStream(
            api_key,
            api_secret,
        )
        self.ticker = ticker
        self.client = TradingClient(api_key, api_secret, paper=True)
        self.asset_data = None

        self.ask = None
        self.bid = None
        self.mid = None

    async def quote_handler(self, data: Quote):
        # Update ask, bid and midpoint prices on every new quote
        self.ask = data.ask_price
        self.bid = data.bid_price
        self.mid = (data.ask_price + data.bid_price) / 2
        print(self.ask, self.bid, round(self.mid, 2))

    def run(self):
        try:
            asset_data = self.client.get_asset(self.ticker)
            self.asset_data = asset_data
            print(f"Company information: {self.asset_data.name}")
            print(f"Tradable: {self.asset_data.tradable}")
            self.stream.subscribe_quotes(self.quote_handler, self.ticker)
            self.stream.run()
        except APIError as e:
            print(e)
            return
