import json
import logging
import datetime
import websockets
import hmac
import hashlib
from typing import List, Callable, Any, Optional

from cryptoxlib.WebsocketMgr import Subscription, WebsocketMgr, WebsocketMessage
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.btse.functions import map_pair
from cryptoxlib.clients.btse import enums
from cryptoxlib.clients.btse.exceptions import BtseException
from cryptoxlib.exceptions import WebsocketReconnectionException

LOG = logging.getLogger(__name__)


class BtseWebsocket(WebsocketMgr):
    WEBSOCKET_URI = "wss://ws.btse.com/spotWS"

    def __init__(self, subscriptions: List[Subscription], api_key: str = None, sec_key: str = None,
                 ssl_context = None) -> None:
        super().__init__(websocket_uri = self.WEBSOCKET_URI, subscriptions = subscriptions,
                         ssl_context = ssl_context,
                         auto_reconnect = True)

        self.api_key = api_key
        self.sec_key = sec_key

    async def _authenticate(self, websocket: websockets.WebSocketClientProtocol):
        requires_authentication = False
        for subscription in self.subscriptions:
            if subscription.requires_authentication():
                requires_authentication = True
                break

        if requires_authentication:
            timestamp_ms = int(datetime.datetime.now(tz = datetime.timezone.utc).timestamp() * 1000)
            signature_string = f"/futures/api/topic{timestamp_ms}"
            signature = hmac.new(self.sec_key.encode('utf-8'), signature_string.encode('utf-8'),
                                 hashlib.sha384).hexdigest()

            authentication_message = {
                "op": "authKeyExpires",
                "args": [self.api_key, timestamp_ms, signature]
            }

            LOG.debug(f"> {authentication_message}")
            await websocket.send(json.dumps(authentication_message))

            message = await websocket.recv()
            LOG.debug(f"< {message}")

            message = json.loads(message)
            if 'event' in message and message['event'] == 'authenticate' and \
                    'authenticated' in message and message['authenticated'] is True:
                LOG.info(f"Websocket authenticated successfully.")
            else:
                raise BtseException(f"Authentication error. Response [{json.dumps(message)}]")

    async def _subscribe(self, websocket: websockets.WebSocketClientProtocol):
        subscription_list = []
        for subscription in self.subscriptions:
            subscription_list += subscription.get_subscription_message()

        subscription_message = {
            "op": "subscribe",
            "args": subscription_list
        }

        LOG.debug(f"> {subscription_message}")
        await websocket.send(json.dumps(subscription_message))

    async def _process_message(self, websocket: websockets.WebSocketClientProtocol, message: str) -> None:
        message = json.loads(message)

        # subscription negative response
        if "error" in message or message['type'] == "ERROR":
            raise BtseException(
                f"Subscription error. Request [{json.dumps(self._get_subscription_message())}] Response [{json.dumps(message)}]")

        # subscription positive response
        elif message['type'] == "SUBSCRIPTIONS":
            LOG.info(f"Subscription confirmed for channels [" + ",".join(
                [channel["name"] for channel in message["channels"]]) + "]")

        # remote termination with an opportunity to reconnect
        elif message["type"] == "CONNECTION_CLOSING":
            LOG.warning(f"Server is performing connection termination with an opportunity to reconnect.")
            raise WebsocketReconnectionException("Graceful connection termination.")

        # heartbeat message
        elif message["type"] == "HEARTBEAT":
            pass

        # regular message
        else:
            await self.publish_message(WebsocketMessage(subscription_id = message['channel_name'], message = message))


class BtseSubscription(Subscription):
    def __init__(self, callbacks: Optional[List[Callable[[dict], Any]]] = None):
        super().__init__(callbacks)

    @staticmethod
    def get_channel_name():
        pass

    def construct_subscription_id(self) -> Any:
        return self.get_channel_name()

    def requires_authentication(self) -> bool:
        return False


class AccountSubscription(BtseSubscription):
    def __init__(self, callbacks : List[Callable[[dict], Any]] = None):
        super().__init__(callbacks)

    @staticmethod
    def get_channel_name():
        return "ACCOUNT_HISTORY"

    def get_subscription_message(self, **kwargs) -> dict:
        return ["notificationApi"]

    def requires_authentication(self) -> bool:
        return True


class OrderbookSubscription(BtseSubscription):
    def __init__(self, pairs : List[Pair], depth : str, callbacks : List[Callable[[dict], Any]] = None):
        super().__init__(callbacks)

        self.pairs = pairs
        self.depth = depth

    @staticmethod
    def get_channel_name():
        return "ORDER_BOOK"

    def get_subscription_message(self, **kwargs) -> dict:
        subscription_list = []
        for pair in self.pairs:
            subscription_list.append(f"orderBookApi:{map_pair(pair)}_{self.depth}")

        return subscription_list