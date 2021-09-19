import enum


class OrderType(enum.Enum):
    MARKET = enum.auto()
    LIMIT = enum.auto()


class OrderSide(enum.Enum):
    BUY = enum.auto()
    SELL = enum.auto()


class TimeInForce(enum.Enum):
    GOOD_TILL_CANCELLED = enum.auto()
    IMMEDIATE_OR_CANCELLED = enum.auto()