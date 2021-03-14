import enum


class OrderSide(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(enum.Enum):
    LIMIT = 'LIMIT'
    MARKET = 'MARKET'
    STOP_LOSS = 'STOP_LOSS'
    STOP_LOSS_LIMIT = 'STOP_LOSS_LIMIT'
    TAKE_PROFIT = 'TAKE_PROFIT'
    TAKE_PROFIT_LIMIT = 'TAKE_PROFIT_LIMIT'
    LIMIT_MAKER = 'LIMIT_MAKER'


class DepthLimit(enum.Enum):
    L_5 = '5'
    L_10 = '10'
    L_20 = '20'
    L_50 = '50'
    L_100 = '100'
    L_500 = '500'
    L_1000 = '1000'
    L_5000 = '5000'


class CandelstickInterval(enum.Enum):
    I_1MIN = '1m'
    I_3MIN = '3m'
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
    I_3D = '3d'
    I_1W = '1w'
    I_1MONTH = '1M'


class OrderResponseType(enum.Enum):
    ACT = "ACK"
    RESULT = "RESULT"
    FULL = "FULL"


class TimeInForce(enum.Enum):
    GOOD_TILL_CANCELLED = "GTC"
    IMMEDIATE_OR_CANCELLED = "IOC"
    FILL_OR_KILL = "FOK"


class APICluster(enum.Enum):
    CLUSTER_DEFAULT = "api"
    CLUSTER_1 = "api1"
    CLUSTER_2 = "api2"
    CLUSTER_3 = "api3"