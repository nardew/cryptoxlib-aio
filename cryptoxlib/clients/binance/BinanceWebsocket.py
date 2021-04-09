import logging
from typing import List

from cryptoxlib.WebsocketMgr import Subscription, CallbacksType
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.binance.BinanceCommonWebsocket import BinanceCommonWebsocket
from cryptoxlib.clients.binance.BinanceCommonWebsocket import BinanceSubscription
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


class BestOrderBookTickerSubscription(BinanceSubscription):
    def __init__(self, callbacks: CallbacksType = None):
        super().__init__(callbacks)

    def get_channel_name(self):
        return "!bookTicker"


class BestOrderBookSymbolTickerSubscription(BinanceSubscription):
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