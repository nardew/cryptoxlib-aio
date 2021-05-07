import json
import jwt
import time
import logging
import hmac
import zlib
import hashlib
import base64
import websockets
from abc import abstractmethod
from typing import List, Callable, Any, Optional

from cryptoxlib.WebsocketMgr import Subscription, WebsocketMgr, WebsocketMessage, Websocket
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.bibox.functions import map_pair
from cryptoxlib.clients.bibox import enums
from cryptoxlib.clients.bibox.exceptions import BiboxException

LOG = logging.getLogger(__name__)


class BiboxEuropeWebsocket(WebsocketMgr):
    WEBSOCKET_URI = "wss://push.bibox.cc/"

    def __init__(self, subscriptions: List[Subscription], api_key: str = None, sec_key: str = None, ssl_context = None) -> None:
        super().__init__(websocket_uri = self.WEBSOCKET_URI, subscriptions = subscriptions,
                         builtin_ping_interval = None, ssl_context = ssl_context,
                         auto_reconnect = True)
        self.api_key = api_key
        self.sec_key = sec_key

    async def send_subscription_message(self, subscriptions: List[Subscription]):
        for subscription in subscriptions:
            subscription_message = json.dumps(subscription.get_subscription_message(api_key = self.api_key, sec_key = self.sec_key))

            LOG.debug(f"> {subscription_message}")
            await self.websocket.send(subscription_message)

    async def _process_message(self, websocket: Websocket, message: str) -> None:
        messages = json.loads(message)

        if "ping" in messages:
            pong_message = {
                "pong": messages['ping']
            }
            LOG.debug(f"> {pong_message}")
            await websocket.send(json.dumps(pong_message))
        elif 'error' in messages:
            raise BiboxException(f"BiboxException: Bibox error received: {message}")
        else:
            for message in messages:
                if 'data' in message:
                    data = message['data']
                    if 'binary' in message and message['binary'] == '1':
                        data = zlib.decompress(base64.b64decode(data), zlib.MAX_WBITS | 32)
                        message['data'] = json.loads(data.decode("utf-8"))
                    await self.publish_message(WebsocketMessage(subscription_id = message['channel'], message = message))
                else:
                    LOG.warning(f"No data element received: {message}")


class BiboxEuropeSubscription(Subscription):
    def __init__(self, callbacks: Optional[List[Callable[[dict], Any]]] = None):
        super().__init__(callbacks)

    @abstractmethod
    def get_channel_name(self) -> str:
        pass

    def construct_subscription_id(self) -> Any:
        return self.get_channel_name()

    def get_subscription_message(self, **kwargs) -> dict:
        return {
            "binary": 0,
            "channel": self.get_channel_name(),
            "event": "addChannel",
        }


class OrderBookSubscription(BiboxEuropeSubscription):
    def __init__(self, pair: Pair, callbacks: Optional[List[Callable[[dict], Any]]] = None):
        super().__init__(callbacks)

        self.pair = pair

    def get_channel_name(self):
        return f"bibox_sub_spot_{map_pair(self.pair)}_depth"


class TickerSubscription(BiboxEuropeSubscription):
    def __init__(self, pair: Pair, callbacks: Optional[List[Callable[[dict], Any]]] = None):
        super().__init__(callbacks)

        self.pair = pair

    def get_channel_name(self):
        return f"bibox_sub_spot_{map_pair(self.pair)}_ticker"


class MarketSubscription(BiboxEuropeSubscription):
    def __init__(self, pair: Pair, callbacks: Optional[List[Callable[[dict], Any]]] = None):
        super().__init__(callbacks)

        self.pair = pair

    def get_channel_name(self):
        return "bibox_sub_spot_ALL_ALL_market"


class TradeSubscription(BiboxEuropeSubscription):
    def __init__(self, pair: Pair, callbacks: Optional[List[Callable[[dict], Any]]] = None):
        super().__init__(callbacks)

        self.pair = pair

    def get_channel_name(self):
        return f"bibox_sub_spot_{map_pair(self.pair)}_deals"


class UserDataSubscription(BiboxEuropeSubscription):
    def __init__(self, callbacks: Optional[List[Callable[[dict], Any]]] = None):
        super().__init__(callbacks)

    def get_channel_name(self):
        return "bibox_sub_spot_ALL_ALL_login"

    def get_subscription_message(self, **kwargs) -> dict:
        subscription =  {
            "apikey": kwargs['api_key'],
            'binary': 0,
            "channel": self.get_channel_name(),
            "event": "addChannel",
        }

        signature = hmac.new(kwargs['sec_key'].encode('utf-8'),
                             json.dumps(subscription, sort_keys=True).replace("\'", "\"").replace(" ", "").encode('utf-8'),
                             hashlib.md5).hexdigest()

        subscription['sign'] = signature

        return subscription