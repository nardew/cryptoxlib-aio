import json
import logging
from typing import List, Any

from cryptoxlib.WebsocketMgr import Subscription, WebsocketMgr, WebsocketMessage, Websocket, CallbacksType

LOG = logging.getLogger(__name__)


class BinanceCommonWebsocket(WebsocketMgr):
    SUBSCRIPTION_ID = 0

    def __init__(self, subscriptions: List[Subscription], binance_client, api_key: str = None, sec_key: str = None,
                 websocket_uri: str = None, builtin_ping_interval: float = 20, periodic_timeout_sec: int = None,
                 ssl_context = None) -> None:
        super().__init__(websocket_uri = websocket_uri,
                         subscriptions = subscriptions,
                         builtin_ping_interval = builtin_ping_interval,
                         periodic_timeout_sec = periodic_timeout_sec,
                         ssl_context = ssl_context,
                         auto_reconnect = True)

        self.api_key = api_key
        self.sec_key = sec_key
        self.binance_client = binance_client

    def get_websocket_uri_variable_part(self):
        return "stream?streams=" + "/".join([subscription.get_channel_name() for subscription in self.subscriptions])

    def get_websocket(self) -> Websocket:
        return self.get_aiohttp_websocket()

    async def initialize_subscriptions(self, subscriptions: List[Subscription]) -> None:
        for subscription in subscriptions:
            await subscription.initialize(binance_client = self.binance_client)

    async def send_subscription_message(self, subscriptions: List[Subscription]):
        BinanceCommonWebsocket.SUBSCRIPTION_ID += 1

        subscription_message = {
            "method": "SUBSCRIBE",
            "params": [
                subscription.get_channel_name() for subscription in subscriptions
            ],
            "id": BinanceCommonWebsocket.SUBSCRIPTION_ID
        }

        LOG.debug(f"> {subscription_message}")
        await self.websocket.send(json.dumps(subscription_message))

    async def send_unsubscription_message(self, subscriptions: List[Subscription]):
        BinanceCommonWebsocket.SUBSCRIPTION_ID += 1

        subscription_message = {
            "method": "UNSUBSCRIBE",
            "params": [
                subscription.get_channel_name() for subscription in subscriptions
            ],
            "id": BinanceCommonWebsocket.SUBSCRIPTION_ID
        }

        LOG.debug(f"> {subscription_message}")
        await self.websocket.send(json.dumps(subscription_message))

    @staticmethod
    def _is_subscription_confirmation(response):
        if 'result' in response and response['result'] is None:
            return True
        else:
            return False

    async def _process_message(self, websocket: Websocket, message: str) -> None:
        if message is None:
            return

        message = json.loads(message)

        if self._is_subscription_confirmation(message):
            LOG.info(f"Subscription updated for id: {message['id']}")
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

    def is_authenticated(self) -> bool:
        return False

    def is_isolated_margin_authenticated(self) -> bool:
        return False

    def is_cross_margin_authenticated(self) -> bool:
        return False