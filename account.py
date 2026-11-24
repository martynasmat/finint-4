from alpaca.trading.client import TradingClient


class Account:
    def __init__(
            self,
            api_key: str,
            api_secret: str,
    ):
        self.trading_client = TradingClient(
            api_key,
            api_secret,
            paper=True,
        )
        self.account = self.trading_client.get_account()

    def get_equity(self):
        return self.account.equity

    def get_cash(self):
        return self.account.cash

    def refresh(self):
        self.account = self.trading_client.get_account()
