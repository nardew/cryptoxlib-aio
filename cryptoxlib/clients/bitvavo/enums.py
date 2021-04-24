import enum


class OrderType(enum.Enum):
    MARKET = "market"
    LIMIT = "limit"


class OrderSide(enum.Enum):
    BUY = "buy"
    SELL = "sell"


class TimeInForce(enum.Enum):
    GOOD_TILL_CANCELLED = "GTC"
    IMMEDIATE_OR_CANCELLED = "IOC"
    FILL_OR_KILL = "FOK"


class SelfTradePrevention(enum.Enum):
    DECREMENT_AND_CANCEL = "decrementAndCancel"
    CANCEL_OLDEST = "cancelOldest"
    CANCEL_NEWEST = "cancelNewest"
    CANCEL_BOTH = "cancelBoth"


class CandlestickInterval(enum.Enum):
    I_1MIN = '1m'
    I_5MIN = '5m'
    I_15MIN = '15m'
    I_30MIN = '30m'
    I_1H = '1h'
    I_2H = '2h'
    I_4H = '4h'
    I_6H = '6h'
    I_8H = '8h'
    I_12H = '12h'
    I_1D = '1d'
