import json
import logging
from typing import List

from cryptoxlib.WebsocketMgr import Subscription, CallbacksType
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.binance.exceptions import BinanceException
from cryptoxlib.clients.binance.functions import map_ws_pair
from cryptoxlib.clients.binance.BinanceCommonWebsocket import BinanceCommonWebsocket, BinanceSubscription
from cryptoxlib.clients.binance import enums

LOG = logging.getLogger(__name__)


class BinanceUSDSMFuturesWebsocket(BinanceCommonWebsocket):
    WEBSOCKET_URI = "wss://fstream.binance.com/"

    def __init__(self, subscriptions: List[Subscription], binance_client, api_key: str = None, sec_key: str = None,
                 ssl_context = None) -> None:
        super().__init__(subscriptions = subscriptions, binance_client = binance_client, api_key = api_key,
                         sec_key = sec_key, websocket_uri = BinanceUSDSMFuturesWebsocket.WEBSOCKET_URI,
                         ssl_context = ssl_context)


class BinanceUSDSMFuturesTestnetWebsocket(BinanceCommonWebsocket):
    WEBSOCKET_URI = "wss://stream.binancefuture.com/"

    def __init__(self, subscriptions: List[Subscription], binance_client, api_key: str = None, sec_key: str = None,
                 ssl_context = None) -> None:
        super().__init__(subscriptions = subscriptions, binance_client = binance_client, api_key = api_key,
                         sec_key = sec_key, websocket_uri = BinanceUSDSMFuturesTestnetWebsocket.WEBSOCKET_URI,
                         ssl_context = ssl_context)


class BinanceCOINMFuturesWebsocket(BinanceCommonWebsocket):
    WEBSOCKET_URI = "https://dapi.binance.com/"

    def __init__(self, subscriptions: List[Subscription], binance_client, api_key: str = None, sec_key: str = None,
                 ssl_context = None) -> None:
        super().__init__(subscriptions = subscriptions, binance_client = binance_client, api_key = api_key,
                         sec_key = sec_key, websocket_uri = BinanceUSDSMFuturesWebsocket.WEBSOCKET_URI,
                         ssl_context = ssl_context)


class BinanceCOINMFuturesTestnetWebsocket(BinanceCommonWebsocket):
    WEBSOCKET_URI = "wss://dstream.binancefuture.com/"

    def __init__(self, subscriptions: List[Subscription], binance_client, api_key: str = None, sec_key: str = None,
                 ssl_context = None) -> None:
        super().__init__(subscriptions = subscriptions, binance_client = binance_client, api_key = api_key,
                         sec_key = sec_key, websocket_uri = BinanceUSDSMFuturesTestnetWebsocket.WEBSOCKET_URI,
                         ssl_context = ssl_context)


class AggregateTradeSubscription(BinanceSubscription):
    def __init__(self, pair: Pair, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.pair = pair

    def get_channel_name(self):
        return map_ws_pair(self.pair) + "@aggTrade"


class MarkPriceSubscription(BinanceSubscription):
    def __init__(self, pair: Pair, frequency1sec: bool = False, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.pair = pair
        self.frequency1sec = frequency1sec

    def get_channel_name(self):
        return map_ws_pair(self.pair) + "@markPrice" + ("@1s" if self.frequency1sec else "")


class MarkPriceAllSubscription(BinanceSubscription):
    def __init__(self, frequency1sec: bool = False, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.frequency1sec = frequency1sec

    def get_channel_name(self):
        return "!markPrice@arr" + ("@1s" if self.frequency1sec else "")


class CandlestickSubscription(BinanceSubscription):
    def __init__(self, pair: Pair, interval: enums.Interval, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.pair = pair
        self.interval = interval

    def get_channel_name(self):
        return f"{map_ws_pair(self.pair)}@kline_{self.interval.value}"


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


class AllMarketMiniTickersSubscription(BinanceSubscription):
    def __init__(self, callbacks: CallbacksType = None):
        super().__init__(callbacks)

    def get_channel_name(self):
        return "!miniTicker@arr"


class MiniTickerSubscription(BinanceSubscription):
    def __init__(self, pair: Pair, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.pair = pair

    def get_channel_name(self):
        return f"{map_ws_pair(self.pair)}@miniTicker"


class AllMarketTickersSubscription(BinanceSubscription):
    def __init__(self, callbacks: CallbacksType = None):
        super().__init__(callbacks)

    def get_channel_name(self):
        return "!ticker@arr"


class TickerSubscription(BinanceSubscription):
    def __init__(self, pair: Pair, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.pair = pair

    def get_channel_name(self):
        return f"{map_ws_pair(self.pair)}@ticker"


class OrderBookTickerSubscription(BinanceSubscription):
    def __init__(self, callbacks: CallbacksType = None):
        super().__init__(callbacks)

    def get_channel_name(self):
        return "!bookTicker"


class OrderBookSymbolTickerSubscription(BinanceSubscription):
    def __init__(self, pair: Pair, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.pair = pair

    def get_channel_name(self):
        return f"{map_ws_pair(self.pair)}@bookTicker"


class LiquidationOrdersSubscription(BinanceSubscription):
    def __init__(self, pair: Pair, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.pair = pair

    def get_channel_name(self):
        return f"{map_ws_pair(self.pair)}@forceOrder"


class AllMarketLiquidationOrdersSubscription(BinanceSubscription):
    def __init__(self, callbacks: CallbacksType = None):
        super().__init__(callbacks)

    def get_channel_name(self):
        return "!forceOrder@arr"


class DepthSubscription(BinanceSubscription):
    DEFAULT_FREQUENCY = 250
    DEFAULT_LEVEL = 0

    def __init__(self, pair: Pair, level: int = DEFAULT_LEVEL, frequency: int = DEFAULT_FREQUENCY,
                 callbacks: CallbacksType = None):
        super().__init__(callbacks)

        if level not in [0, 5, 10, 20]:
            raise BinanceException(f"Level [{level}] must be one of 0, 5, 10 or 20.")

        if frequency not in [100, 250, 500]:
            raise BinanceException(f"Frequency [{frequency}] must be one of 100, 250 or 500.")

        self.pair = pair
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

        return f"{map_ws_pair(self.pair)}@depth{level_str}{frequency_str}"


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