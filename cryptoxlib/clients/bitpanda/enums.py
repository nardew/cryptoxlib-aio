import enum


class OrderType(enum.Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LIMIT = "STOP"


class OrderSide(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class TimeInForce(enum.Enum):
    GOOD_TILL_CANCELLED = "GOOD_TILL_CANCELLED"
    IMMEDIATE_OR_CANCELLED = "IMMEDIATE_OR_CANCELLED"


class TimeUnit(enum.Enum):
    MINUTES = "MINUTES"
    HOURS = "HOURS"
    DAYS = "DAYS"
    WEEKS = "WEEKS"
    MONTHS = "MONTHS"
