import enum


class OrderType(enum.Enum):
    MARKET = "1"
    LIMIT = "2"
    STOP_MARKET = "3"
    STOP_LIMIT = "4"


class OrderSide(enum.Enum):
    BUY = "1"
    SELL = "2"


class TimeInForce(enum.Enum):
    GOOD_TILL_CANCELLED = "GTC"
