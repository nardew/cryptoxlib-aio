import json
import logging
from typing import List, Callable, Any, Optional

from cryptoxlib.WebsocketMgr import Subscription, WebsocketMgr, WebsocketMessage, Websocket, CallbacksType
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.binance.functions import map_ws_pair
from cryptoxlib.clients.binance.enums import CandelstickInterval

LOG = logging.getLogger(__name__)


class BinanceWebsocket(WebsocketMgr):
    WEBSOCKET_URI = "wss://stream.binance.com:9443/"
    SUBSCRIPTION_ID = 0

    def __init__(self, subscriptions: List[Subscription], binance_client, api_key: str = None, sec_key: str = None,
                 ssl_context = None) -> None:
        super().__init__(websocket_uri = self.WEBSOCKET_URI,
                         subscriptions = subscriptions,
                         builtin_ping_interval = None,
                         ssl_context = ssl_context,
                         auto_reconnect = True)

        self.api_key = api_key
        self.sec_key = sec_key
        self.binance_client = binance_client

    def get_websocket_uri_variable_part(self):
        return "stream?streams=" + "/".join([subscription.get_channel_name() for subscription in self.subscriptions])

    async def initialize_subscriptions(self) -> None:
        for subscription in self.subscriptions:
            await subscription.initialize(binance_client = self.binance_client)

    async def _subscribe(self, websocket: Websocket):
        BinanceWebsocket.SUBSCRIPTION_ID += 1

        subscription_message = {
            "method": "SUBSCRIBE",
            "params": [
                subscription.get_channel_name() for subscription in self.subscriptions
            ],
            "id": BinanceWebsocket.SUBSCRIPTION_ID
        }

        LOG.debug(f"> {subscription_message}")
        await websocket.send(json.dumps(subscription_message))

    @staticmethod
    def _is_subscription_confirmation(response):
        if 'result' in response and response['result'] is None:
            return True
        else:
            return False

    async def _process_message(self, websocket: Websocket, message: str) -> None:
        message = json.loads(message)

        if self._is_subscription_confirmation(message):
            LOG.info(f"Subscription confirmed for id: {message['id']}")
        else:
            # regular message
            await self.publish_message(WebsocketMessage(subscription_id = message['stream'], message = message))


class BinanceSubscription(Subscription):
    def __init__(self, callbacks: CallbacksType = None):
        super().__init__(callbacks)

    @staticmethod
    def get_channel_name():
        pass

    def get_subscription_message(self, **kwargs) -> dict:
        pass

    def construct_subscription_id(self) -> Any:
        return self.get_channel_name()


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
    def __init__(self, pair: Pair, interval: CandelstickInterval, callbacks: CallbacksType = None):
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
