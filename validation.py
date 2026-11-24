import datetime
from alpaca.data import TimeFrame
from alpaca.trading import OrderType, OrderSide, TimeInForce

def valid_uuid(s: str) -> str:
    try:
        return str(uuid.UUID(s))
    except ValueError:
        raise argparse.ArgumentTypeError(f"not a valid UUID: {s!r}")


def valid_date(s: str) -> datetime.datetime:
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f"not a valid date: {s!r}")


def valid_timeframe(s: str) -> TimeFrame:
    match s:
        case "minute":
            return TimeFrame.Minute
        case "hour":
            return TimeFrame.Hour
        case "day":
            return TimeFrame.Day

    raise argparse.ArgumentTypeError(f"not a valid timeframe: {s!r}")


def valid_type(s: str) -> OrderType:
    match s:
        case "market":
            return OrderType.MARKET
        case "limit":
            return OrderType.LIMIT
    raise argparse.ArgumentTypeError(f"not a valid type: {s!r}")


def valid_side(s: str) -> OrderSide:
    match s:
        case "buy":
            return OrderSide.BUY
        case "sell":
            return OrderSide.SELL
    raise argparse.ArgumentTypeError(f"not a valid side: {s!r}")


def valid_time_in_force(s: str) -> TimeInForce:
    match s:
        case "day":
            return TimeInForce.DAY
        case "gtc":
            return TimeInForce.GTC
    raise argparse.ArgumentTypeError(f"not a valid time in force: {s!r}")

def valid_status(s: str) -> str | None:
    match s:
        case "open":
            return "open"
        case "closed":
            return "closed"
        case "all":
            return "all"
    return None