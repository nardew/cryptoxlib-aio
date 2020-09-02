import json
import logging
import datetime
import hmac
import hashlib
from typing import List, Any

from cryptoxlib.WebsocketMgr import Subscription, WebsocketMgr, WebsocketMessage, Websocket, CallbacksType
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.hitbtc.functions import map_pair
from cryptoxlib.clients.hitbtc.exceptions import HitbtcException

LOG = logging.getLogger(__name__)


class HitbtcWebsocket(WebsocketMgr):
    WEBSOCKET_URI = "wss://api.hitbtc.com/api/2/ws"
    MAX_MESSAGE_SIZE = 3 * 1024 * 1024  # 3MB

    def __init__(self, subscriptions: List[Subscription], api_key: str = None, sec_key: str = None,
                 ssl_context = None) -> None:
        super().__init__(websocket_uri = self.WEBSOCKET_URI, subscriptions = subscriptions,
                         ssl_context = ssl_context,
                         builtin_ping_interval = None,
                         auto_reconnect = True,
                         max_message_size = self.MAX_MESSAGE_SIZE)

        self.api_key = api_key
        self.sec_key = sec_key

    def get_websocket(self) -> Websocket:
        return self.get_aiohttp_websocket()

    async def _authenticate(self, websocket: Websocket):
        requires_authentication = False
        for subscription in self.subscriptions:
            if subscription.requires_authentication():
                requires_authentication = True
                break

        if requires_authentication:
            timestamp_ms = str(int(datetime.datetime.now(tz = datetime.timezone.utc).timestamp() * 1000))
            signature = hmac.new(self.sec_key.encode('utf-8'), timestamp_ms.encode('utf-8'),
                                 hashlib.sha256).hexdigest()

            authentication_message = {
                "method": "login",
                "params": {
                    "algo": "HS256",
                    "pKey": self.api_key,
                    "nonce": timestamp_ms,
                    "signature": signature
                }
            }

            LOG.debug(f"> {authentication_message}")
            await websocket.send(json.dumps(authentication_message))

            message = await websocket.receive()
            LOG.debug(f"< {message}")

            message = json.loads(message)
            if 'result' in message and message['result'] == True:
                LOG.info(f"Authenticated websocket connected successfully.")
            else:
                raise HitbtcException(f"Authentication error. Response [{message}]")

    async def _subscribe(self, websocket: Websocket):
        for subscription in self.subscriptions:
            subscription_message = subscription.get_subscription_message()
            LOG.debug(f"> {subscription_message}")
            await websocket.send(json.dumps(subscription_message))

    async def _process_message(self, websocket: Websocket, message: str) -> None:
        message = json.loads(message)

        if 'id' in message and 'result' in message and message['result'] == True:
            # subscription confirmation
            pass
        else:
            # regular message
            await self.publish_message(WebsocketMessage(
                subscription_id = self._map_message_to_subscription_id(message), message = message))

    @staticmethod
    def _map_message_to_subscription_id(message: dict):
        if message['method'] in ['snapshotOrderbook', 'updateOrderbook']:
            return f"orderbook{message['params']['symbol']}"
        elif message['method'] == 'ticker':
            return f"{message['method']}{message['params']['symbol']}"
        elif message['method'] in ['snapshotTrades', 'updateTrades']:
            return f"trades{message['params']['symbol']}"
        elif message['method'] in ['activeOrders', 'report']:
            return "account"


class HitbtcSubscription(Subscription):
    SUBSCRIPTION_ID = 1

    def __init__(self, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        HitbtcSubscription.SUBSCRIPTION_ID += 1
        self.id = HitbtcSubscription.SUBSCRIPTION_ID

    def requires_authentication(self) -> bool:
        return False


class AccountSubscription(HitbtcSubscription):
    def __init__(self, callbacks: CallbacksType = None):
        super().__init__(callbacks)

    def get_subscription_message(self, **kwargs) -> dict:
        return {
            "method": "subscribeReports",
            "params": {},
            "id": self.id
        }

    def construct_subscription_id(self) -> Any:
        return "account"

    def requires_authentication(self) -> bool:
        return True


class OrderbookSubscription(HitbtcSubscription):
    def __init__(self, pair: Pair, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.pair = pair

    def get_subscription_message(self, **kwargs) -> dict:
        return {
            "method": "subscribeOrderbook",
            "params": {
                "symbol": map_pair(self.pair),
            },
            "id": self.id
        }

    def construct_subscription_id(self) -> Any:
        return f"orderbook{map_pair(self.pair)}"


class TickerSubscription(HitbtcSubscription):
    def __init__(self, pair: Pair, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.pair = pair

    def get_subscription_message(self, **kwargs) -> dict:
        return {
            "method": "subscribeTicker",
            "params": {
                "symbol": map_pair(self.pair),
            },
            "id": self.id
        }

    def construct_subscription_id(self) -> Any:
        return f"ticker{map_pair(self.pair)}"


class TradesSubscription(HitbtcSubscription):
    def __init__(self, pair: Pair, limit: int = None, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.pair = pair
        self.limit = limit

    def get_subscription_message(self, **kwargs) -> dict:
        params = {
            "method": "subscribeTrades",
            "params": {
                "symbol": map_pair(self.pair),
            },
            "id": self.id
        }

        if self.limit is not None:
            params['params']['limit'] = self.limit

        return params

    def construct_subscription_id(self) -> Any:
        return f"trades{map_pair(self.pair)}"