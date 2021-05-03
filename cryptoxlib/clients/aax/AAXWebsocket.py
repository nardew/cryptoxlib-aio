import json
import logging
import datetime
import hashlib
import hmac
from abc import abstractmethod
from typing import List, Callable, Any, Union, Optional

from cryptoxlib.WebsocketMgr import Subscription, WebsocketMgr, WebsocketMessage, Websocket
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.aax import enums
from cryptoxlib.clients.aax.exceptions import AAXException
from cryptoxlib.clients.aax.functions import map_pair
from cryptoxlib.PeriodicChecker import PeriodicChecker

LOG = logging.getLogger(__name__)


class AAXWebsocket(WebsocketMgr):
    WEBSOCKET_URI = "wss://stream.aax.com/"

    def __init__(self, subscriptions: List[Subscription], api_key: str = None, sec_key: str = None, user_id: str = None,
                 ssl_context = None) -> None:
        super().__init__(websocket_uri = self.WEBSOCKET_URI, subscriptions = subscriptions,
                         ssl_context = ssl_context,
                         builtin_ping_interval = None,
                         auto_reconnect = True,
                         periodic_timeout_sec = 5)

        self.api_key = api_key
        self.sec_key = sec_key

    def get_websocket(self) -> Websocket:
        return self.get_aiohttp_websocket()

    async def send_authentication_message(self):
        requires_authentication = False
        for subscription in self.subscriptions:
            if subscription.requires_authentication():
                requires_authentication = True
                break

        if requires_authentication:
            handshake_message = '{"event":"#handshake","cid":1}'
            LOG.debug(f"> {handshake_message}")
            await self.websocket.send(handshake_message)
            handshake_response = await self.websocket.receive()
            LOG.debug(f"< {handshake_response}")

            timestamp_ms = int(datetime.datetime.now(tz = datetime.timezone.utc).timestamp() * 1000)
            signature_string = f"{timestamp_ms}:{self.api_key}"
            signature = hmac.new(self.sec_key.encode('utf-8'), signature_string.encode('utf-8'),
                                 hashlib.sha256).hexdigest()

            authentication_message = {
                "event": "login",
                "data": {
                    "apiKey": self.api_key,
                    "nonce": str(timestamp_ms),
                    "signature": signature
                }
            }

            LOG.debug(f"> {authentication_message}")
            await self.websocket.send(json.dumps(authentication_message))

            message = json.loads(await self.websocket.receive())
            LOG.debug(f"< {message}")

            if 'data' in message and 'isAuthenticated' in message['data'] and message['data']['isAuthenticated'] is True:
                LOG.info(f"Websocket authenticated successfully.")
            else:
                raise AAXException(f"Authentication error. Response [{message}]")

    async def send_subscription_message(self, subscriptions: List[Subscription]):
        for subscription in subscriptions:
            LOG.debug(f"> {subscription.get_subscription_message()}")
            await self.websocket.send(json.dumps(subscription.get_subscription_message()))

    async def validate_subscriptions(self, subscriptions: List[Subscription]) -> None:
        pass

    def get_websocket_uri_variable_part(self):
        return self.subscriptions[0].get_stream_uri()

    async def _process_message(self, websocket: Websocket, message: str) -> None:
        if message == '#1':
            pong = '#2'
            LOG.debug(f"> {pong}")
            await websocket.send(pong)
            return

        message = json.loads(message)

        if message['e'] == 'empty':
            pass
        elif message['e'] == 'system':
            pass
        elif message['e'] == 'reply' and message['status'] == 'ok':
            LOG.info("Channel subscribed successfully.")
        elif message['e'] == 'reply' and message['status'] == 'error':
            raise AAXException(f"Websocket error message received: {message}")
        else:
            await self.publish_message(WebsocketMessage(subscription_id = self.map_subscription_id(message), message = message))

    def map_subscription_id(self, message: dict):
        if "event" in message and message['event'] in ['USER_BALANCE', 'SPOT', 'FUTURES']:
            return "notification"
        else:
            return message['e']


class AAXSubscription(Subscription):
    def __init__(self, callbacks: Optional[List[Callable[[dict], Any]]] = None):
        super().__init__(callbacks)

    @abstractmethod
    def get_channel_name(self) -> str:
        pass

    @abstractmethod
    def get_stream_uri(self) -> str:
        pass

    def construct_subscription_id(self) -> Any:
        return self.get_channel_name()

    def get_subscription_message(self, **kwargs) -> dict:
        return {
                "e": "subscribe",
                "stream": self.get_channel_name()
        }

    def requires_authentication(self) -> bool:
        return False


class OrderBookSubscription(AAXSubscription):
    def __init__(self, pair: Pair, depth: int, callbacks: Optional[List[Callable[[dict], Any]]] = None):
        super().__init__(callbacks)

        assert(depth in (20, 50))

        self.pair = pair
        self.depth = depth

    def get_channel_name(self):
        return f"{map_pair(self.pair)}@book_{self.depth}"

    def get_stream_uri(self) -> str:
        return "marketdata/v2/"


class AccountSubscription(AAXSubscription):
    def __init__(self, user_id: str, callbacks: Optional[List[Callable[[dict], Any]]] = None):
        super().__init__(callbacks)

        self.user_id = user_id

    def get_channel_name(self):
        return f"notification"

    def get_stream_uri(self) -> str:
        return "notification/v2/"

    def requires_authentication(self) -> bool:
        return True

    def get_subscription_message(self, **kwargs) -> dict:
        return {
            "e": "subscribe",
            "data": {
                "channel": f"user/{self.user_id}"
            },
            "cid": 2
        }
