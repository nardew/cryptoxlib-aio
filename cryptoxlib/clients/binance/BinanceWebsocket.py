import logging
from typing import List

from cryptoxlib.WebsocketMgr import Subscription, CallbacksType
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.binance.BinanceCommonWebsocket import BinanceCommonWebsocket
from cryptoxlib.clients.binance.BinanceCommonWebsocket import BinanceSubscription
from cryptoxlib.clients.binance.exceptions import BinanceException
from cryptoxlib.clients.binance.functions import map_ws_pair
from cryptoxlib.clients.binance.enums import Interval

LOG = logging.getLogger(__name__)


class BinanceWebsocket(BinanceCommonWebsocket):
    WEBSOCKET_URI = "wss://stream.binance.com:9443/"

    def __init__(self, subscriptions: List[Subscription], binance_client, api_key: str = None, sec_key: str = None,
                 ssl_context = None) -> None:
        super().__init__(subscriptions = subscriptions, binance_client = binance_client, api_key = api_key,
                         sec_key = sec_key, websocket_uri = BinanceWebsocket.WEBSOCKET_URI,
                         ssl_context = ssl_context)


class BinanceTestnetWebsocket(BinanceCommonWebsocket):
    WEBSOCKET_URI = "wss://testnet.binance.vision/"

    def __init__(self, subscriptions: List[Subscription], binance_client, api_key: str = None, sec_key: str = None,
                 ssl_context = None) -> None:
        super().__init__(subscriptions = subscriptions, binance_client = binance_client, api_key = api_key,
                         sec_key = sec_key, websocket_uri = BinanceTestnetWebsocket.WEBSOCKET_URI,
                         ssl_context = ssl_context)


class AllMarketTickersSubscription(BinanceSubscription):
    def __init__(self, callbacks: CallbacksType = None):
        super().__init__(callbacks)

    def get_channel_name(self):
        return "!ticker@arr"


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


class TradeSubscription(BinanceSubscription):
    def __init__(self, pair: Pair, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.pair = pair

    def get_channel_name(self):
        return map_ws_pair(self.pair) + "@trade"


class AggregateTradeSubscription(BinanceSubscription):
    def __init__(self, pair: Pair, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.pair = pair

    def get_channel_name(self):
        return map_ws_pair(self.pair) + "@aggTrade"


class CandlestickSubscription(BinanceSubscription):
    def __init__(self, pair: Pair, interval: Interval, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.pair = pair
        self.interval = interval

    def get_channel_name(self):
        return f"{map_ws_pair(self.pair)}@kline_{self.interval.value}"


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


class DepthSubscription(BinanceSubscription):
    DEFAULT_FREQUENCY = 1000
    DEFAULT_LEVEL = 0

    def __init__(self, pair: Pair, level: int = DEFAULT_LEVEL, frequency: int = DEFAULT_FREQUENCY,
                 callbacks: CallbacksType = None):
        super().__init__(callbacks)

        if level not in [0, 5, 10, 20]:
            raise BinanceException(f"Level [{level}] must be one of 0, 5, 10 or 20.")

        if frequency not in [100, 1000]:
            raise BinanceException(f"Frequency [{frequency}] must be one of 100 or 1000.")

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