import enum

class OrderType(enum.Enum):
    MARKET = "market"
    LIMIT = "limit"

class OrderSide(enum.Enum):
    BUY = "buy"
    SELL = "sell"