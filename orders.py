from alpaca.broker import MarketOrderRequest, LimitOrderRequest
from alpaca.common import APIError
from alpaca.trading import TradingClient, TimeInForce, OrderType, OrderSide, GetOrdersRequest
from enum import StrEnum


class OrderClient:
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

    def place_order(
            self,
            symbol: str,
            ord_type: OrderType,
            qty: int,
            ord_side: OrderSide,
            time_in_force: TimeInForce,
            limit_price: float,
    ):
        if ord_type == OrderType.MARKET:
            req = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=ord_side,
                time_in_force=time_in_force,
                type=OrderType.MARKET,
            )
        elif ord_type == OrderType.LIMIT:
            req = LimitOrderRequest(
                symbol=symbol,
                qty=qty,
                side=ord_side,
                limit_price=limit_price,
                time_in_force=time_in_force,
            )

        try:
            res = self.trading_client.submit_order(req)
            lookup = self.trading_client.get_order_by_id(res.id)
            if lookup is not None and lookup.status in ("accepted", "filled", "new"):
                print('Order accepted')
            else:
                print('Order rejected')
        except APIError as e:
            print(e)

    def cancel_order(self, ord_id: str):
        print(f"Cancelling order {ord_id}")
        self.trading_client.cancel_order_by_id(ord_id)
        lookup = self.trading_client.get_order_by_id(ord_id)
        if lookup.status == "canceled":
            print("Order canceled")
        elif lookup.status == "pending_cancel":
            print("Order pending cancellation")
        else:
            print("Failed to cancel order")

    def get_orders(self, status: str = None):
        orders = self.trading_client.get_orders(GetOrdersRequest(status=status))
        for order in orders:
            print(f"""ID: {order.id}
Symbol: {order.symbol}
Type: {order.type.value.upper()}
Side: {order.side.value.upper()}{('\nLimit price: ' + order.limit_price) if order.type == OrderType.LIMIT else ''}
Qty: {order.qty}
Filled: {order.filled_qty}
Status: {order.status.value.upper()}
Created At: {order.created_at}\n""")
