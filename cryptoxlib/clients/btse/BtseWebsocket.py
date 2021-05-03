import json
import logging
import datetime
import websockets
import hmac
import hashlib
from typing import List, Callable, Any, Optional

from cryptoxlib.WebsocketMgr import Subscription, WebsocketMgr, WebsocketMessage, Websocket, CallbacksType
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.btse.functions import map_pair
from cryptoxlib.clients.btse.exceptions import BtseException
from cryptoxlib.PeriodicChecker import PeriodicChecker

LOG = logging.getLogger(__name__)


class BtseWebsocket(WebsocketMgr):
    WEBSOCKET_URI = "wss://ws.btse.com/spotWS"

    def __init__(self, subscriptions: List[Subscription], api_key: str = None, sec_key: str = None,
                 ssl_context = None) -> None:
        super().__init__(websocket_uri = self.WEBSOCKET_URI, subscriptions = subscriptions,
                         ssl_context = ssl_context,
                         builtin_ping_interval = None,
                         auto_reconnect = True,
                         periodic_timeout_sec = 5)

        self.api_key = api_key
        self.sec_key = sec_key

        self.ping_checker = PeriodicChecker(period_ms = 30 * 1000)

    def get_websocket(self) -> Websocket:
        return self.get_aiohttp_websocket()

    async def _process_periodic(self, websocket: Websocket) -> None:
        if self.ping_checker.check():
            await websocket.send("2")

    async def send_authentication_message(self):
        requires_authentication = False
        for subscription in self.subscriptions:
            if subscription.requires_authentication():
                requires_authentication = True
                break

        if requires_authentication:
            timestamp_ms = int(datetime.datetime.now(tz = datetime.timezone.utc).timestamp() * 1000)
            signature_string = f"/spotWS{timestamp_ms}"
            signature = hmac.new(self.sec_key.encode('utf-8'), signature_string.encode('utf-8'),
                                 hashlib.sha384).hexdigest()

            authentication_message = {
                "op": "authKeyExpires",
                "args": [self.api_key, timestamp_ms, signature]
            }

            LOG.debug(f"> {authentication_message}")
            await self.websocket.send(json.dumps(authentication_message))

            message = await self.websocket.receive()
            LOG.debug(f"< {message}")

            message = json.loads(message)
            if 'success' in message and message['success'] is True:
                LOG.info(f"Authenticated websocket connected successfully.")
            else:
                raise BtseException(f"Authentication error. Response [{message}]")

    async def send_subscription_message(self, subscriptions: List[Subscription]):
        subscription_list = []
        for subscription in subscriptions:
            subscription_list += subscription.get_subscription_list()

        subscription_message = {
            "op": "subscribe",
            "args": subscription_list
        }

        LOG.debug(f"> {subscription_message}")
        await self.websocket.send(json.dumps(subscription_message))

        message = await self.websocket.receive()
        LOG.debug(f"< {message}")

        try:
            message = json.loads(message)
            if message['event'] == 'subscribe' and len(message['channel']) > 0:
                LOG.info(f"Websocket subscribed successfully.")
            else:
                raise BtseException(f"Subscription error. Response [{message}]")
        except:
            raise BtseException(f"Subscription error. Response [{message}]")

    async def _process_message(self, websocket: Websocket, message: str) -> None:
        message = json.loads(message)
        topic = message['topic']
        channel = topic.split(':')[0]

        await self.publish_message(WebsocketMessage(subscription_id = channel, message = message))


class BtseSubscription(Subscription):
    def __init__(self, callbacks: CallbacksType = None):
        super().__init__(callbacks)

    def get_subscription_list(self) -> List[str]:
        pass

    def construct_subscription_id(self) -> Any:
        return self.get_subscription_list()[0].split(':')[0]

    def requires_authentication(self) -> bool:
        return False

    def get_subscription_message(self, **kwargs) -> dict:
        return {}


class AccountSubscription(BtseSubscription):
    def __init__(self, callbacks: CallbacksType = None):
        super().__init__(callbacks)

    def get_subscription_list(self) -> List[str]:
        return ["notificationApi"]

    def requires_authentication(self) -> bool:
        return True


class OrderbookSubscription(BtseSubscription):
    def __init__(self, pairs: List[Pair], grouping_level: int = 0, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.pairs = pairs
        self.grouping_level = grouping_level

    def get_subscription_list(self) -> List[str]:
        subscription_list = []
        for pair in self.pairs:
            subscription_list.append(f"orderBookApi:{map_pair(pair)}_{self.grouping_level}")

        return subscription_list


class OrderbookL2Subscription(BtseSubscription):
    def __init__(self, pairs: List[Pair], depth: int, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.pairs = pairs
        self.depth = depth

    def get_subscription_list(self) -> List[str]:
        subscription_list = []
        for pair in self.pairs:
            subscription_list.append(f"orderBookL2Api:{map_pair(pair)}_{self.depth}")

        return subscription_list


class TradeSubscription(BtseSubscription):
    def __init__(self, pairs: List[Pair], callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.pairs = pairs

    def get_subscription_list(self) -> List[str]:
        subscription_list = []
        for pair in self.pairs:
            subscription_list.append(f"tradeHistoryApi:{map_pair(pair)}")

        return subscription_list
