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
    STOP = 'STOP'
    STOP_MARKET = 'STOP_MARKET'
    TAKE_PROFIT_MARKET = 'TAKE_PROFIT_MARKET'
    TRAILING_STOP_MARKET = 'TRAILING_STOP_MARKET'


class PositionSide(enum.Enum):
    BOTH = 'BOTH'
    LONG = 'LONG'
    SHORT = 'SHORT'


class WorkingType(enum.Enum):
    MARK_PRICE = 'MARK_PRICE'
    CONTRACT_PRICE = 'CONTRACT_PRICE'


class MarginType(enum.Enum):
    ISOLATED = 'ISOLATED'
    CROSSED = 'CROSSED'


class IncomeType(enum.Enum):
    TRANSFER = "TRANSFER"
    WELCOME_BONUS = "WELCOME_BONUS"
    REALIZED_PNL = "REALIZED_PNL"
    FUNDING_FEE = "FUNDING_FEE"
    COMMISSION = "COMMISSION"
    INSURANCE_CLEAR = "INSURANCE_CLEAR"


class AutoCloseType(enum.Enum):
    LIQUIDATION = 'LIQUIDATION'
    ADL = 'ADL'


class DepthLimit(enum.Enum):
    L_5 = '5'
    L_10 = '10'
    L_20 = '20'
    L_50 = '50'
    L_100 = '100'
    L_500 = '500'
    L_1000 = '1000'
    L_5000 = '5000'


class Interval(enum.Enum):
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


class ContractType(enum.Enum):
    PERPETUAL = 'PERPETUAL'
    CURRENT_MONTH = 'CURRENT_MONTH'
    NEXT_MONTH = 'NEXT_MONTH'
    CURRENT_QUARTER = 'CURRENT_QUARTER'
    NEXT_QUARTER = 'NEXT_QUARTER'


class OrderResponseType(enum.Enum):
    ACT = "ACK"
    RESULT = "RESULT"
    FULL = "FULL"


class TimeInForce(enum.Enum):
    GOOD_TILL_CANCELLED = "GTC"
    IMMEDIATE_OR_CANCELLED = "IOC"
    FILL_OR_KILL = "FOK"
    GOOD_TILL_CROSSING = 'GTX'


class APICluster(enum.Enum):
    CLUSTER_DEFAULT = "api"
    CLUSTER_1 = "api1"
    CLUSTER_2 = "api2"
    CLUSTER_3 = "api3"


class CrossMarginTransferType(enum.Enum):
    TO_CROSS_MARGIN_ACCOUNT = 1
    TO_MAIN_ACCOUNT = 2


class SideEffectType(enum.Enum):
    NO_SIDE_EFFECT = "NO_SIDE_EFFECT"
    MARGIN_BUY = "MARGIN_BUY"
    AUTO_REPAY = "AUTO_REPAY"


class TransferType(enum.Enum):
    ROLL_IN = "ROLL_IN"
    ROLL_OUT = "ROLL_OUT"


class AccountType(enum.Enum):
    ISOLATED_MARGIN = "ISOLATED_MARGIN"
    SPOT = "SPOT"


class LiquidityRemovalType(enum.Enum):
    SINGLE = "SINGLE"
    COMBINATION = "COMBINATION"


class LiquidityOperationType(enum.Enum):
    ADD = "ADD"
    REMOVE = "REMOVE"

class SwapStatusType(enum.Enum):
    PENDING = 0
    SUCCESS = 1
    FAILED = 2