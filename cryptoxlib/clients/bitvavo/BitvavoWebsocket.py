import json
import logging
import websockets
import hmac
import hashlib
import datetime
from typing import List, Callable, Any, Optional

from cryptoxlib.WebsocketMgr import Subscription, WebsocketMgr, WebsocketMessage, Websocket
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.bitvavo.functions import map_pair
from cryptoxlib.clients.bitvavo import enums
from cryptoxlib.clients.bitvavo.exceptions import BitvavoException

LOG = logging.getLogger(__name__)


class BitvavoWebsocket(WebsocketMgr):
    WEBSOCKET_URI = "wss://ws.bitvavo.com/v2/"

    def __init__(self, subscriptions: List[Subscription], api_key: str = None, sec_key: str = None,
                 ssl_context = None) -> None:
        super().__init__(websocket_uri = self.WEBSOCKET_URI, subscriptions = subscriptions,
                         ssl_context = ssl_context,
                         auto_reconnect = True)

        self.api_key = api_key
        self.sec_key = sec_key

    async def send_authentication_message(self):
        requires_authentication = False
        for subscription in self.subscriptions:
            if subscription.requires_authentication():
                requires_authentication = True
                break

        if requires_authentication:
            timestamp = int(datetime.datetime.now(tz = datetime.timezone.utc).timestamp() * 1000)
            signature_string = str(timestamp) + 'GET/v2/websocket'
            signature = hmac.new(self.sec_key.encode('utf-8'), signature_string.encode('utf-8'),
                                 hashlib.sha256).hexdigest()

            authentication_message = {
                "action": "authenticate",
                "key": self.api_key,
                "signature": signature,
                "timestamp": timestamp
            }

            LOG.debug(f"> {authentication_message}")
            await self.websocket.send(json.dumps(authentication_message))

            message = await self.websocket.receive()
            LOG.debug(f"< {message}")

            message = json.loads(message)
            if 'event' in message and message['event'] == 'authenticate' and \
                    'authenticated' in message and message['authenticated'] is True:
                LOG.info(f"Websocket authenticated successfully.")
            else:
                raise BitvavoException(f"Authentication error. Response [{json.dumps(message)}]")

    async def send_subscription_message(self, subscriptions: List[Subscription]):
        subscription_message = {
            "action": "subscribe",
            "channels": [
                subscription.get_subscription_message() for subscription in subscriptions
            ]
        }

        LOG.debug(f"> {subscription_message}")
        await self.websocket.send(json.dumps(subscription_message))

    async def _process_message(self, websocket: websockets.WebSocketClientProtocol, message: str) -> None:
        message = json.loads(message)

        # subscription negative response
        if 'action' in message and message['action'] == 'subscribe' and "error" in message:
            raise BitvavoException(f"Subscription error. Response [{json.dumps(message)}]")

        # subscription positive response
        if 'event' in message and message['event'] == 'subscribed':
            if len(message['subscriptions']) > 0:
                LOG.info(f"Subscription confirmed for channels [{message['subscriptions']}]")
            else:
                raise BitvavoException(f"Subscription error. No subscription confirmed. Response [{json.dumps(message)}]")

        # regular message
        else:
            await self.publish_message(WebsocketMessage(subscription_id = self._map_event_id_to_subscription_id(message['event']),
                                                        message = message))

    @staticmethod
    def _map_event_id_to_subscription_id(event_typ: str):
        if event_typ in ['order', 'fill']:
            return AccountSubscription.get_channel_name()
        elif event_typ == 'trade':
            return TradesSubscription.get_channel_name()
        elif event_typ == 'candle':
            return CandlesticksSubscription.get_channel_name()
        else:
            return event_typ

class BitvavoSubscription(Subscription):
    def __init__(self, callbacks: Optional[List[Callable[[dict], Any]]] = None):
        super().__init__(callbacks)

    @staticmethod
    def get_channel_name():
        pass

    def construct_subscription_id(self) -> Any:
        return self.get_channel_name()

    def requires_authentication(self) -> bool:
        return False


class AccountSubscription(BitvavoSubscription):
    def __init__(self, pairs: List[Pair], callbacks : List[Callable[[dict], Any]] = None):
        super().__init__(callbacks)

        self.pairs = pairs

    def requires_authentication(self) -> bool:
        return True

    @staticmethod
    def get_channel_name():
        return "account"

    def get_subscription_message(self, **kwargs) -> dict:
        return {
            "name": self.get_channel_name(),
            "markets": [
                map_pair(pair) for pair in self.pairs
            ]
        }


class TickerSubscription(BitvavoSubscription):
    def __init__(self, pairs : List[Pair], callbacks : List[Callable[[dict], Any]] = None):
        super().__init__(callbacks)

        self.pairs = pairs

    @staticmethod
    def get_channel_name():
        return "ticker"

    def get_subscription_message(self, **kwargs) -> dict:
        return {
            "name": self.get_channel_name(),
            "markets": [
                map_pair(pair) for pair in self.pairs
            ]
        }


class Ticker24Subscription(BitvavoSubscription):
    def __init__(self, pairs : List[Pair], callbacks : List[Callable[[dict], Any]] = None):
        super().__init__(callbacks)

        self.pairs = pairs

    @staticmethod
    def get_channel_name():
        return "ticker24h"

    def get_subscription_message(self, **kwargs) -> dict:
        return {
            "name": self.get_channel_name(),
            "markets": [
                map_pair(pair) for pair in self.pairs
            ]
        }


class TradesSubscription(BitvavoSubscription):
    def __init__(self, pairs : List[Pair], callbacks : List[Callable[[dict], Any]] = None):
        super().__init__(callbacks)

        self.pairs = pairs

    @staticmethod
    def get_channel_name():
        return "trades"

    def get_subscription_message(self, **kwargs) -> dict:
        return {
            "name": self.get_channel_name(),
            "markets": [
                map_pair(pair) for pair in self.pairs
            ]
        }


class OrderbookSubscription(BitvavoSubscription):
    def __init__(self, pairs : List[Pair], callbacks : List[Callable[[dict], Any]] = None):
        super().__init__(callbacks)

        self.pairs = pairs

    @staticmethod
    def get_channel_name():
        return "book"

    def get_subscription_message(self, **kwargs) -> dict:
        return {
            "name": self.get_channel_name(),
            "markets": [
                map_pair(pair) for pair in self.pairs
            ]
        }


class CandlesticksSubscription(BitvavoSubscription):
    def __init__(self, pairs : List[Pair], intervals: List[enums.CandlestickInterval], callbacks : List[Callable[[dict], Any]] = None):
        super().__init__(callbacks)

        self.pairs = pairs
        self.intervals = intervals

    @staticmethod
    def get_channel_name():
        return "candles"

    def get_subscription_message(self, **kwargs) -> dict:
        return {
            "name": self.get_channel_name(),
            "markets": [
                map_pair(pair) for pair in self.pairs
            ],
            "interval": [
                interval.value for interval in self.intervals
            ]
        }
