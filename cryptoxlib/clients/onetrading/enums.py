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
    FILL_OR_KILL = "FILL_OR_KILL"
    GOOD_TILL_TIME = "GOOD_TILL_TIME"


class TimeUnit(enum.Enum):
    MINUTES = "MINUTES"
    HOURS = "HOURS"
    DAYS = "DAYS"
    WEEKS = "WEEKS"
    MONTHS = "MONTHS"


class PricePointsMode(enum.Enum):
    SPLIT = 'SPLIT'
    INLINE = 'INLINE'
    OMIT = 'OMIT'
