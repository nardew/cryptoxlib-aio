import json
import jwt
import time
import logging
import websockets
from abc import abstractmethod
from typing import List, Callable, Any, Optional

from cryptolib.WebsocketMgr import Subscription, WebsocketMgr, WebsocketMessage
from cryptolib.Pair import Pair
from cryptolib.clients.liquid.functions import map_pair
from cryptolib.clients.liquid import enums
from cryptolib.clients.liquid.exceptions import LiquidException
from cryptolib.PeriodicChecker import PeriodicChecker

LOG = logging.getLogger(__name__)


class LiquidWebsocket(WebsocketMgr):
    WEBSOCKET_URI = "wss://tap.liquid.com/app/LiquidTapClient"

    PING_MSG = 'ping_p'
    PONG_MSG = 'pong_p'

    def __init__(self, subscriptions: List[Subscription], api_key: str = None, sec_key: str = None, ssl_context = None) -> None:
        super().__init__(websocket_uri = self.WEBSOCKET_URI, subscriptions = subscriptions,
                         builtin_ping_interval = None, ssl_context = ssl_context)

        self.api_key = api_key
        self.sec_key = sec_key

        self.ping_checker = PeriodicChecker(period_ms = 60 * 1000)

    async def _subscribe(self, websocket: websockets.WebSocketClientProtocol):
        authentication_payload = {
            "token_id": self.api_key,
            "path": '/realtime',
            "nonce": int(time.time_ns())
        }
        LOG.debug(f"Authentication payload: {authentication_payload}")
        signature = jwt.encode(authentication_payload, self.sec_key, 'HS256')

        authentication_data = {
            "headers": {
                "X-Quoine-Auth": signature.decode('utf-8')
            },
            "path": "/realtime"
        }

        authentication_request = {
            "event": "quoine:auth_request",
            "data": authentication_data
        }
        LOG.debug(f"> {authentication_request}")
        await websocket.send(json.dumps(authentication_request))

    async def _process_message(self, websocket: websockets.WebSocketClientProtocol, message: str) -> None:
        message = json.loads(message)

        if message['event'] == "pusher:connection_established":
            pass
        elif message['event'] == "quoine:auth_success":
            subscription_messages = []
            for subscription in self.subscriptions:
                subscription_message = subscription.get_subscription_message()
                subscription_messages.append(subscription_message)

            LOG.debug(f"> {subscription_messages}")
            await websocket.send(json.dumps(subscription_messages))
        elif message['event'] == "quoine:auth_failure":
            raise LiquidException(f"Websocket authentication error: {message}")
        elif message['event'] == "pusher_internal:subscription_succeeded":
            LOG.info(f'Websocket subscribed successfuly: {message}')
        elif message['event'] == "updated":
            await self.publish_message(WebsocketMessage(subscription_id = message['channel'], message = message))
        else:
            raise LiquidException(f"Websocket unknown event type: {message}")


class LiquidSubscription(Subscription):
    def __init__(self, callbacks: Optional[List[Callable[[dict], Any]]] = None):
        super().__init__(callbacks)

    @abstractmethod
    def get_channel_name(self) -> str:
        pass

    def construct_subscription_id(self) -> Any:
        return self.get_channel_name()

    def get_subscription_message(self, **kwargs) -> dict:
        return {
            "event": "pusher:subscribe",
            "data": {
                "channel": self.get_channel_name()
            },
        }


class OrderBookSideSubscription(LiquidSubscription):
    def __init__(self, pair: Pair, order_side: enums.OrderSide, callbacks: Optional[List[Callable[[dict], Any]]] = None):
        super().__init__(callbacks)

        self.pair = pair
        self.order_side = order_side

    def get_channel_name(self):
        return f"price_ladders_cash_{map_pair(self.pair)}_{self.order_side.value}"


class OrderBookSubscription(LiquidSubscription):
    def __init__(self, pair: Pair, callbacks: Optional[List[Callable[[dict], Any]]] = None):
        super().__init__(callbacks)

        self.pair = pair

    def get_channel_name(self):
        return f"price_ladders_cash_{map_pair(self.pair)}"

class OrderSubscription(LiquidSubscription):
    def __init__(self, quote: str, callbacks: Optional[List[Callable[[dict], Any]]] = None):
        super().__init__(callbacks)

        self.quote = quote

    def get_channel_name(self):
        return f"user_account_{self.quote}_orders"
