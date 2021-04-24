import enum


class OrderSide(enum.Enum):
    BUY = "1"
    SELL = "2"


class OrderState(enum.Enum):
    PENDING = "0"
    COMPLETE = "1"


class CandlestickInterval(enum.Enum):
    I_1MIN = '1min'
    I_5MIN = '5min'
    I_15MIN = '15min'
    I_30MIN = '30min'
    I_1H = '1hour'
    I_2H = '2hour'
    I_4H = '4hour'
    I_12H = '12hour'
    I_1D = '1day'
    I_1W = '1week'
    I_1MONTH = '1month'