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

    def refresh(self):
        self.account = self.trading_client.get_account()

    def get_account_info(self):
        self.refresh()
        return f"""Equity: {self.account.equity}
Cash: {self.account.cash}
Created: {self.account.created_at}"""
