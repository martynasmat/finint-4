import uuid
from unittest import case

import dotenv
import os
import argparse

from alpaca.data import TimeFrame
from alpaca.trading import OrderType, OrderSide, TimeInForce

import realtime
import historical
import orders
import datetime
import account
from validation import *


def handle_realtime(
        symbol: str,
):
    client = realtime.RealtimeData(
        API_KEY,
        API_SECRET,
        symbol,
    )
    client.run()


def handle_historical(
        symbol: str,
        start: datetime.datetime,
        end: datetime.datetime,
        bars: bool,
        timeframe: TimeFrame,
):
    if ',' in symbol:
        symbol = symbol.split(',')

    client = historical.HistoricalData(
        API_KEY,
        API_SECRET,
        symbol,
        start,
        end,
        bars,
        timeframe,
    )
    print("Fetching historical data...")
    client.fetch()
    print("Saving historical data...")
    filename = client.save()
    print(f"Saved to {filename}") if filename else None


def handle_place_order(
        symbol: str,
        ord_type: OrderType,
        qty: int,
        ord_side: OrderSide,
        time_in_force: TimeInForce,
        limit_price: float,
        client: orders.OrderClient,
):
    print(f"Placing {ord_type.value.upper()} {ord_side.value.upper()} order for {qty} {symbol} "
          f"{('@ ' + str(limit_price)) if ord_type == OrderType.LIMIT else ''}"
          f" (time-in-force: {time_in_force.value.upper()})")
    client.place_order(
        symbol,
        ord_type,
        qty,
        ord_side,
        time_in_force,
        limit_price,
    )


if __name__ == "__main__":
    dotenv.load_dotenv()
    API_KEY = os.getenv("ALPACA_API_KEY")
    API_SECRET = os.getenv("ALPACA_SECRET")

    orders_client = orders.OrderClient(
        API_KEY,
        API_SECRET,
    )
    acc_client = account.Account(
        API_KEY,
        API_SECRET,
    )

    parser = argparse.ArgumentParser("4 namų darbas")
    subparsers = parser.add_subparsers(dest="option", help="realtime/historical/place_order/get_orders/cancel_order/account")

    realtime_parser = subparsers.add_parser("realtime")
    realtime_parser.add_argument("symbol", type=str, help="stock ticker")

    historical_parser = subparsers.add_parser("historical")
    historical_parser.add_argument("symbol", type=str, help="stock ticker(s) (comma-separated if multiple)")
    historical_parser.add_argument("start", type=valid_date, help="start date (YYYY-MM-DD)")
    historical_parser.add_argument("end", type=valid_date, help="end date (YYYY-MM-DD)")
    historical_parser.add_argument("bars", type=str, choices=("true", "false"), help="bars or last trade price (true/false)", default=False)
    historical_parser.add_argument("timeframe", type=valid_timeframe, help="aggregation (minute, hour, day)", nargs='?')

    place_order_parser = subparsers.add_parser("place_order")
    place_order_parser.add_argument("symbol", type=str, help="stock ticker")
    place_order_parser.add_argument("type", type=valid_type, help="type (market/limit)")
    place_order_parser.add_argument("qty", type=int, help="quantity")
    place_order_parser.add_argument("side", type=valid_side, help="side (buy/sell)")
    place_order_parser.add_argument("time_in_force", type=valid_time_in_force, help="time in force (day/gtc)")
    place_order_parser.add_argument("limit_price", type=float, help="limit price", nargs='?')

    get_orders_parser = subparsers.add_parser("get_orders")
    get_orders_parser.add_argument("status", type=valid_status, help="status (open/closed/all)", nargs='?')

    cancel_order_parser = subparsers.add_parser("cancel_order")
    cancel_order_parser.add_argument("order_id", type=valid_uuid, help="order ID")

    account_parser = subparsers.add_parser("account")

    args = parser.parse_args()
    match args.option:
        case "realtime":
            handle_realtime(
                args.symbol,
            )
        case "historical":
            handle_historical(
                args.symbol,
                args.start,
                args.end,
                args.bars.lower() == "true",
                args.timeframe,
            )
        case "place_order":
            if args.type == OrderType.LIMIT and args.limit_price is None:
                place_order_parser.error("limit_price is required for limit orders")

            handle_place_order(
                args.symbol,
                args.type,
                args.qty,
                args.side,
                args.time_in_force,
                args.limit_price,
                orders_client,
            )
        case "get_orders":
            orders_client.get_orders(args.status)
        case "cancel_order":
            orders_client.cancel_order(args.order_id)
        case "account":
            print(acc_client.get_account_info())
