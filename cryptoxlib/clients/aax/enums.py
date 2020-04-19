import enum


class OrderSide(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(enum.Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP-LIMIT"


class TimeInForce(enum.Enum):
    GOOD_TILL_CANCELLED = "GTC"
    IMMEDIATE_OR_CANCELLED = "IOC"
    FILL_OR_KILL = "FOK"