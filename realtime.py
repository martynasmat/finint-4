from alpaca.data import Quote
from alpaca.data.live import StockDataStream

class RealtimeData:
    def __init__(
            self,
            api_key: str,
            api_secret: str,
            ticker: str,
    ):
        if not ticker:
            print("No ticker provided")
            return

        if not api_key or not api_secret:
            print("A valid Alpaca API key and secret are required")
            return

        self.stream = StockDataStream(
            api_key,
            api_secret,
        )
        self.ticker = ticker
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
        self.stream.subscribe_quotes(self.quote_handler, self.ticker)
        self.stream.run()
