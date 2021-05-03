import json
import logging
import datetime
import hmac
import pytz
import hashlib
from typing import List, Any

from cryptoxlib.WebsocketMgr import Subscription, WebsocketMgr, WebsocketMessage, Websocket, CallbacksType, \
    ClientWebsocketHandle, WebsocketOutboundMessage
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.hitbtc.functions import map_pair
from cryptoxlib.clients.hitbtc.exceptions import HitbtcException
from cryptoxlib.clients.hitbtc import enums

LOG = logging.getLogger(__name__)


class HitbtcWebsocket(WebsocketMgr):
    WEBSOCKET_URI = "wss://api.hitbtc.com/api/2/ws"
    MAX_MESSAGE_SIZE = 3 * 1024 * 1024  # 3MB

    def __init__(self, subscriptions: List[Subscription], api_key: str = None, sec_key: str = None,
                 ssl_context = None, startup_delay_ms: int = 0) -> None:
        super().__init__(websocket_uri = self.WEBSOCKET_URI, subscriptions = subscriptions,
                         ssl_context = ssl_context,
                         builtin_ping_interval = None,
                         auto_reconnect = True,
                         max_message_size = self.MAX_MESSAGE_SIZE,
                         startup_delay_ms = startup_delay_ms)

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
            await self.websocket.send(json.dumps(authentication_message))

            message = await self.websocket.receive()
            LOG.debug(f"< {message}")

            message = json.loads(message)
            if 'result' in message and message['result'] == True:
                LOG.info(f"Authenticated websocket connected successfully.")
            else:
                raise HitbtcException(f"Authentication error. Response [{message}]")

    async def send_subscription_message(self, subscriptions: List[Subscription]):
        for subscription in subscriptions:
            subscription_message = subscription.get_subscription_message()
            LOG.debug(f"> {subscription_message}")
            await self.websocket.send(json.dumps(subscription_message))

    async def _process_message(self, websocket: Websocket, message: str) -> None:
        message = json.loads(message)

        if 'id' in message and 'result' in message and message['result'] == True:
            # subscription confirmation
            # for confirmed account channel publish the confirmation downstream in order to communicate the websocket handle
            for subscription in self.subscriptions:
                    if subscription.external_id == message['id'] and subscription.get_subscription_id() == 'account':
                        await self.publish_message(WebsocketMessage(
                            subscription_id = 'account',
                            message = message,
                            websocket = ClientWebsocketHandle(websocket = websocket)
                        ))
        else:
            # regular message
            subscription_id = self._map_message_to_subscription_id(message)
            await self.publish_message(WebsocketMessage(
                subscription_id = subscription_id,
                message = message,
                # for account channel communicate also the websocket handle
                websocket = ClientWebsocketHandle(websocket = websocket) if subscription_id == 'account' else None
            )
            )

    def _map_message_to_subscription_id(self, message: dict):
        if 'method' in message:
            if message['method'] in ['snapshotOrderbook', 'updateOrderbook']:
                return f"orderbook{message['params']['symbol']}"
            elif message['method'] == 'ticker':
                return f"{message['method']}{message['params']['symbol']}"
            elif message['method'] in ['snapshotTrades', 'updateTrades']:
                return f"trades{message['params']['symbol']}"
            elif message['method'] in ['activeOrders', 'report']:
                return "account"
        elif 'error' in message and 'id' in message:
            for subscription in self.subscriptions:
                if subscription.external_id == message['id']:
                    return subscription.get_subscription_id()

            # if error message does not belong to any subscription based on the id, then assume it relates
            # to a placed order and send it to the account channel
            return "account"
        else:
            return ""

class HitbtcSubscription(Subscription):
    EXTERNAL_SUBSCRIPTION_ID = 0

    def __init__(self, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.external_id = HitbtcSubscription.generate_new_external_id()

    def requires_authentication(self) -> bool:
        return False

    @staticmethod
    def generate_new_external_id():
        HitbtcSubscription.EXTERNAL_SUBSCRIPTION_ID += 1
        return HitbtcSubscription.EXTERNAL_SUBSCRIPTION_ID


class AccountSubscription(HitbtcSubscription):
    def __init__(self, callbacks: CallbacksType = None):
        super().__init__(callbacks)

    def get_subscription_message(self, **kwargs) -> dict:
        return {
            "method": "subscribeReports",
            "params": {},
            "id": self.external_id
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
            "id": self.external_id
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
            "id": self.external_id
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
            "id": self.external_id
        }

        if self.limit is not None:
            params['params']['limit'] = self.limit

        return params

    def construct_subscription_id(self) -> Any:
        return f"trades{map_pair(self.pair)}"


class CreateOrderMessage(WebsocketOutboundMessage):
    def __init__(self, pair: Pair, side: enums.OrderSide, type: enums.OrderType, amount: str,client_id: str,
                 price: str = None, stop_price: str = None, time_in_force: enums.TimeInForce = None,
                 expire_time: datetime.datetime = None, strict_validate: bool = None,
                 post_only: bool = None):
        self.pair = pair
        self.type = type
        self.side = side
        self.amount = amount
        self.price = price
        self.stop_price = stop_price
        self.time_in_force = time_in_force
        self.client_id = client_id
        self.expire_time = expire_time
        self.strict_validate = strict_validate
        self.post_only = post_only

    def to_json(self):
        id = HitbtcSubscription.generate_new_external_id()

        ret = {
            "method": "newOrder",
            "params": {
                "symbol": map_pair(self.pair),
                "side": self.side.value,
                "type": self.type.value,
                "quantity": self.amount,
                'clientOrderId': self.client_id
            },
            "id": id
        }

        if self.price is not None:
            ret['params']['price'] = self.price

        if self.stop_price is not None:
            ret['params']['stopPrice'] = self.stop_price

        if self.strict_validate is not None:
            ret['params']['strictValidate'] = self.strict_validate

        if self.post_only is not None:
            ret['params']['postOnly'] = self.post_only

        if self.time_in_force is not None:
            ret['params']['timeInForce'] = self.time_in_force.value

        if self.expire_time:
            ret['parms']["expireTime"] = self.expire_time.astimezone(pytz.utc).isoformat()

        return ret


class CancelOrderMessage(WebsocketOutboundMessage):
    def __init__(self, client_id: str):
        self.client_id = client_id

    def to_json(self):
        id = HitbtcSubscription.generate_new_external_id()

        ret = {
            'method': 'cancelOrder',
            'params': {
                "clientOrderId": self.client_id
            },
            'id': id
        }

        return ret