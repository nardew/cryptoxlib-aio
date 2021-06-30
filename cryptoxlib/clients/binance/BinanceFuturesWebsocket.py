import logging
from typing import List

from cryptoxlib.WebsocketMgr import Subscription, CallbacksType, Websocket
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.binance.exceptions import BinanceException
from cryptoxlib.clients.binance.functions import map_ws_pair, extract_ws_symbol
from cryptoxlib.clients.binance.BinanceCommonWebsocket import BinanceCommonWebsocket, BinanceSubscription
from cryptoxlib.clients.binance import enums
from cryptoxlib.clients.binance.types import PairSymbolType

LOG = logging.getLogger(__name__)


class BinanceFuturesWebsocket(BinanceCommonWebsocket):
    def __init__(self, subscriptions: List[Subscription], binance_client, api_key: str = None, sec_key: str = None,
                 websocket_uri: str = None, builtin_ping_interval: float = None, periodic_timeout_sec: int = None,
                 ssl_context = None) -> None:
        super().__init__(subscriptions = subscriptions, binance_client = binance_client, api_key = api_key,
                         sec_key = sec_key,
                         websocket_uri = websocket_uri,
                         builtin_ping_interval = builtin_ping_interval,
                         periodic_timeout_sec = periodic_timeout_sec,
                         ssl_context = ssl_context)

    def is_authenticated(self) -> bool:
        for subscription in self.subscriptions:
            if subscription.is_authenticated():
                return True

        return False

    async def _process_periodic(self, websocket: Websocket) -> None:
        if self.is_authenticated() is True:
            LOG.info(f"[{self.id}] Refreshing listen key.")
            await self.binance_client.keep_alive_listen_key()


class BinanceUSDSMFuturesWebsocket(BinanceFuturesWebsocket):
    WEBSOCKET_URI = "wss://fstream.binance.com/"
    BULTIN_PING_INTERVAL_SEC = 30
    LISTEN_KEY_REFRESH_INTERVAL_SEC = 1800

    def __init__(self, subscriptions: List[Subscription], binance_client, api_key: str = None, sec_key: str = None,
                 ssl_context = None) -> None:
        super().__init__(subscriptions = subscriptions, binance_client = binance_client, api_key = api_key,
                         sec_key = sec_key, websocket_uri = BinanceUSDSMFuturesWebsocket.WEBSOCKET_URI,
                         builtin_ping_interval = BinanceUSDSMFuturesWebsocket.BULTIN_PING_INTERVAL_SEC,
                         periodic_timeout_sec = BinanceUSDSMFuturesWebsocket.LISTEN_KEY_REFRESH_INTERVAL_SEC,
                         ssl_context = ssl_context)


class BinanceUSDSMFuturesTestnetWebsocket(BinanceFuturesWebsocket):
    WEBSOCKET_URI = "wss://stream.binancefuture.com/"

    def __init__(self, subscriptions: List[Subscription], binance_client, api_key: str = None, sec_key: str = None,
                 ssl_context = None) -> None:
        super().__init__(subscriptions = subscriptions, binance_client = binance_client, api_key = api_key,
                         sec_key = sec_key, websocket_uri = BinanceUSDSMFuturesTestnetWebsocket.WEBSOCKET_URI,
                         ssl_context = ssl_context)


class BinanceCOINMFuturesWebsocket(BinanceFuturesWebsocket):
    WEBSOCKET_URI = "https://dstream.binance.com/"
    BULTIN_PING_INTERVAL_SEC = 30
    LISTEN_KEY_REFRESH_INTERVAL_SEC = 1800

    def __init__(self, subscriptions: List[Subscription], binance_client, api_key: str = None, sec_key: str = None,
                 ssl_context = None) -> None:
        super().__init__(subscriptions = subscriptions, binance_client = binance_client, api_key = api_key,
                         sec_key = sec_key, websocket_uri = BinanceCOINMFuturesWebsocket.WEBSOCKET_URI,
                         builtin_ping_interval = BinanceCOINMFuturesWebsocket.BULTIN_PING_INTERVAL_SEC,
                         periodic_timeout_sec = BinanceCOINMFuturesWebsocket.LISTEN_KEY_REFRESH_INTERVAL_SEC,
                         ssl_context = ssl_context)


class BinanceCOINMFuturesTestnetWebsocket(BinanceFuturesWebsocket):
    WEBSOCKET_URI = "wss://dstream.binancefuture.com/"

    def __init__(self, subscriptions: List[Subscription], binance_client, api_key: str = None, sec_key: str = None,
                 ssl_context = None) -> None:
        super().__init__(subscriptions = subscriptions, binance_client = binance_client, api_key = api_key,
                         sec_key = sec_key, websocket_uri = BinanceCOINMFuturesTestnetWebsocket.WEBSOCKET_URI,
                         ssl_context = ssl_context)


class AggregateTradeSubscription(BinanceSubscription):
    def __init__(self, symbol: PairSymbolType, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.symbol = extract_ws_symbol(symbol)

    def get_channel_name(self):
        return f"{self.symbol}@aggTrade"


class IndexPriceSubscription(BinanceSubscription):
    def __init__(self, pair: Pair, frequency1sec: bool = False, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.pair = pair
        self.frequency1sec = frequency1sec

    def get_channel_name(self):
        return map_ws_pair(self.pair) + "@indexPrice" + ("@1s" if self.frequency1sec else "")


class MarkPriceSubscription(BinanceSubscription):
    def __init__(self, symbol: PairSymbolType, frequency1sec: bool = False, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.symbol = extract_ws_symbol(symbol)
        self.frequency1sec = frequency1sec

    def get_channel_name(self):
        return f"{self.symbol}@markPrice" + ("@1s" if self.frequency1sec else "")


class MarkPriceAllSubscription(BinanceSubscription):
    def __init__(self, frequency1sec: bool = False, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.frequency1sec = frequency1sec

    def get_channel_name(self):
        return "!markPrice@arr" + ("@1s" if self.frequency1sec else "")


class CandlestickSubscription(BinanceSubscription):
    def __init__(self, symbol: PairSymbolType, interval: enums.Interval, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.interval = interval
        self.symbol = extract_ws_symbol(symbol)

    def get_channel_name(self):
        return f"{self.symbol}@kline_{self.interval.value}"


class ContContractCandlestickSubscription(BinanceSubscription):
    def __init__(self, pair: Pair, interval: enums.Interval, contract_type: enums.ContractType, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        if contract_type not in [enums.ContractType.PERPETUAL, enums.ContractType.CURRENT_QUARTER, enums.ContractType.NEXT_QUARTER]:
            raise BinanceException(f"Level [{contract_type.value}] must be one of {enums.ContractType.PERPETUAL.value}, "
                                   f"{enums.ContractType.CURRENT_QUARTER.value} or {enums.ContractType.NEXT_QUARTER.value}.")

        self.pair = pair
        self.interval = interval
        self.contract_type = contract_type

    def get_channel_name(self):
        return f"{map_ws_pair(self.pair)}_{self.contract_type.value.lower()}@continuousKline_{self.interval.value}"


class IndexPriceCandlestickSubscription(BinanceSubscription):
    def __init__(self, pair: Pair, interval: enums.Interval, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.pair = pair
        self.interval = interval

    def get_channel_name(self):
        return f"{map_ws_pair(self.pair)}@indexPriceKline_{self.interval.value}"


class MarkPriceCandlestickSubscription(BinanceSubscription):
    def __init__(self, symbol: str, interval: enums.Interval, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.symbol = symbol
        self.interval = interval

    def get_channel_name(self):
        return f"{self.symbol}@markPriceKline_{self.interval.value}"


class AllMarketMiniTickersSubscription(BinanceSubscription):
    def __init__(self, callbacks: CallbacksType = None):
        super().__init__(callbacks)

    def get_channel_name(self):
        return "!miniTicker@arr"


class MiniTickerSubscription(BinanceSubscription):
    def __init__(self, symbol: PairSymbolType, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.symbol = extract_ws_symbol(symbol)

    def get_channel_name(self):
        return f"{self.symbol}@miniTicker"


class AllMarketTickersSubscription(BinanceSubscription):
    def __init__(self, callbacks: CallbacksType = None):
        super().__init__(callbacks)

    def get_channel_name(self):
        return "!ticker@arr"


class TickerSubscription(BinanceSubscription):
    def __init__(self, symbol: PairSymbolType, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.symbol = extract_ws_symbol(symbol)

    def get_channel_name(self):
        return f"{self.symbol}@ticker"


class OrderBookTickerSubscription(BinanceSubscription):
    def __init__(self, callbacks: CallbacksType = None):
        super().__init__(callbacks)

    def get_channel_name(self):
        return "!bookTicker"


class OrderBookSymbolTickerSubscription(BinanceSubscription):
    def __init__(self, symbol: PairSymbolType, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.symbol = extract_ws_symbol(symbol)

    def get_channel_name(self):
        return f"{self.symbol}@bookTicker"


class LiquidationOrdersSubscription(BinanceSubscription):
    def __init__(self, symbol: PairSymbolType, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.symbol = extract_ws_symbol(symbol)

    def get_channel_name(self):
        return f"{self.symbol}@forceOrder"


class AllMarketLiquidationOrdersSubscription(BinanceSubscription):
    def __init__(self, callbacks: CallbacksType = None):
        super().__init__(callbacks)

    def get_channel_name(self):
        return "!forceOrder@arr"


class DepthSubscription(BinanceSubscription):
    DEFAULT_FREQUENCY = 250
    DEFAULT_LEVEL = 0

    def __init__(self, symbol: PairSymbolType, level: int = DEFAULT_LEVEL, frequency: int = DEFAULT_FREQUENCY,
                 callbacks: CallbacksType = None):
        super().__init__(callbacks)

        if level not in [0, 5, 10, 20]:
            raise BinanceException(f"Level [{level}] must be one of 0, 5, 10 or 20.")

        if frequency not in [100, 250, 500]:
            raise BinanceException(f"Frequency [{frequency}] must be one of 100, 250 or 500.")

        self.symbol = extract_ws_symbol(symbol)
        self.level = level
        self.frequency = frequency

    def get_channel_name(self):
        if self.level == DepthSubscription.DEFAULT_LEVEL:
            level_str = ""
        else:
            level_str = f"{self.level}"

        if self.frequency == DepthSubscription.DEFAULT_FREQUENCY:
            frequency_str = ""
        else:
            frequency_str = f"@{self.frequency}ms"

        return f"{self.symbol}@depth{level_str}{frequency_str}"


class BlvtSubscription(BinanceSubscription):
    def __init__(self, pair: Pair, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.pair = pair

    def get_channel_name(self):
        return f"{map_ws_pair(self.pair).upper()}@tokenNav"


class BlvtCandlestickSubscription(BinanceSubscription):
    def __init__(self, pair: Pair, interval: enums.Interval, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.pair = pair
        self.interval = interval

    def get_channel_name(self):
        return f"{map_ws_pair(self.pair).upper()}@nav_Kline_{self.interval.value}"


class CompositeIndexSubscription(BinanceSubscription):
    def __init__(self, pair: Pair, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.pair = pair

    def get_channel_name(self):
        return f"{map_ws_pair(self.pair)}@compositeIndex"


class AccountSubscription(BinanceSubscription):
    def __init__(self, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.listen_key = None

    async def initialize(self, **kwargs):
        binance_client = kwargs['binance_client']
        listen_key_response = await binance_client.get_listen_key()
        self.listen_key = listen_key_response["response"]["listenKey"]
        LOG.debug(f'Listen key: {self.listen_key}')

    def get_channel_name(self):
        return self.listen_key

    def is_authenticated(self) -> bool:
        return True