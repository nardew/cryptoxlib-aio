import enum


class OrderSide(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(enum.Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    OCO = "OCO"


class TransactionType(enum.Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    TRIGGER = "TRIGGER"


class TimeInForce(enum.Enum):
    GOOD_TILL_CANCELLED = "GTC"
    IMMEDIATE_OR_CANCELLED = "IOC"
    TIME_5MIN = "FIVEMIN"
    TIME_1HOUR = "HOUR"
    TIME_12HOUR = "TWELVEHOUR"
    TIME_1DAY = "DAY"
    TIME_1WEEK = "WEEK"
    TIME_1MONTH = "MONTH"
