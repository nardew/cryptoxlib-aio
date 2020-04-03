import enum


class OrderType(enum.Enum):
    LIMIT = 2


class OrderSide(enum.Enum):
    BUY = 1
    SELL = 2