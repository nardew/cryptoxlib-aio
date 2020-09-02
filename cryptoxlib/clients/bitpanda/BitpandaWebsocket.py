import json
import logging
from typing import List, Any

from cryptoxlib.WebsocketMgr import Subscription, WebsocketMgr, WebsocketMessage, Websocket, CallbacksType, \
    ClientWebsocketHandle, WebsocketOutboundMessage
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.bitpanda.functions import map_pair, map_multiple_pairs
from cryptoxlib.clients.bitpanda import enums
from cryptoxlib.clients.bitpanda.exceptions import BitpandaException
from cryptoxlib.exceptions import WebsocketReconnectionException

LOG = logging.getLogger(__name__)


class BitpandaWebsocket(WebsocketMgr):
    WEBSOCKET_URI = "wss://streams.exchange.bitpanda.com"
    MAX_MESSAGE_SIZE = 3 * 1024 * 1024  # 3MB

    def __init__(self, subscriptions: List[Subscription], api_key: str = None, ssl_context = None) -> None:
        super().__init__(websocket_uri = self.WEBSOCKET_URI, subscriptions = subscriptions,
                         max_message_size = BitpandaWebsocket.MAX_MESSAGE_SIZE,
                         ssl_context = ssl_context,
                         auto_reconnect = True)

        self.api_key = api_key

    async def _authenticate(self, websocket: Websocket):
        requires_authentication = False
        for subscription in self.subscriptions:
            if subscription.requires_authentication():
                requires_authentication = True
                break

        if requires_authentication:
            authentication_message = {
                "type": "AUTHENTICATE",
                "api_token": self.api_key
            }

            LOG.debug(f"> {authentication_message}")
            await websocket.send(json.dumps(authentication_message))

            message = await websocket.receive()
            LOG.debug(f"< {message}")

            message = json.loads(message)
            if 'type' in message and message['type'] == 'AUTHENTICATED':
                LOG.info(f"Websocket authenticated successfully.")
            else:
                raise BitpandaException(f"Authentication error. Response [{message}]")

    def _get_subscription_message(self):
        return {
            "type": "SUBSCRIBE",
            "channels": [
                subscription.get_subscription_message() for subscription in self.subscriptions
            ]
        }

    async def _subscribe(self, websocket: Websocket):
        subscription_message =  self._get_subscription_message()

        LOG.debug(f"> {subscription_message}")
        await websocket.send(json.dumps(subscription_message))

    async def _process_message(self, websocket: Websocket, message: str) -> None:
        message = json.loads(message)

        # subscription negative response
        if "error" in message or message['type'] == "ERROR":
            raise BitpandaException(
                f"Subscription error. Request [{json.dumps(self._get_subscription_message())}] Response [{json.dumps(message)}]")

        # subscription positive response
        elif message['type'] == "SUBSCRIPTIONS":
            LOG.info(f"Subscription confirmed for channels [" + ",".join(
                [channel["name"] for channel in message["channels"]]) + "]")

            # for confirmed ORDERS channel publish the confirmation downstream in order to communicate the websocket handle
            if 'ORDERS' in [channel['name'] for channel in message['channels']]:
                await self.publish_message(WebsocketMessage(
                    subscription_id = 'ORDERS',
                    message = message,
                    websocket = ClientWebsocketHandle(websocket = websocket)
                ))

        # remote termination with an opportunity to reconnect
        elif message["type"] == "CONNECTION_CLOSING":
            LOG.warning(f"Server is performing connection termination with an opportunity to reconnect.")
            raise WebsocketReconnectionException("Graceful connection termination.")

        # heartbeat message
        elif message["type"] == "HEARTBEAT":
            pass

        # regular message
        else:
            await self.publish_message(WebsocketMessage(
                subscription_id = message['channel_name'],
                message = message,
                # for ORDERS channel communicate also the websocket handle
                websocket = ClientWebsocketHandle(websocket = websocket) if message['channel_name'] == 'ORDERS' else None
            ))


class BitpandaSubscription(Subscription):
    def __init__(self, callbacks: CallbacksType = None):
        super().__init__(callbacks)

    @staticmethod
    def get_channel_name():
        pass

    def construct_subscription_id(self) -> Any:
        return self.get_channel_name()

    def requires_authentication(self) -> bool:
        return False

class AccountSubscription(BitpandaSubscription):
    def __init__(self, callbacks: CallbacksType = None):
        super().__init__(callbacks)

    @staticmethod
    def get_channel_name():
        return "ACCOUNT_HISTORY"

    def get_subscription_message(self, **kwargs) -> dict:
        return {
            "name": self.get_channel_name(),
        }

    def requires_authentication(self) -> bool:
        return True


class PricesSubscription(BitpandaSubscription):
    def __init__(self, pairs: List[Pair], callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.pairs = pairs

    @staticmethod
    def get_channel_name():
        return "PRICE_TICKS"

    def get_subscription_message(self, **kwargs) -> dict:
        return {
            "name": self.get_channel_name(),
            "instrument_codes": map_multiple_pairs(self.pairs, sort = True)
        }


class OrderbookSubscription(BitpandaSubscription):
    def __init__(self, pairs: List[Pair], depth: str, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.pairs = pairs
        self.depth = depth

    @staticmethod
    def get_channel_name():
        return "ORDER_BOOK"

    def get_subscription_message(self, **kwargs) -> dict:
        return {
            "name": self.get_channel_name(),
            "depth": self.depth,
            "instrument_codes": map_multiple_pairs(self.pairs, sort = True)
        }


class CandlesticksSubscriptionParams(object):
    def __init__(self, pair : Pair, unit : enums.TimeUnit, period):
        self.pair = pair
        self.unit = unit
        self.period = period


class CandlesticksSubscription(BitpandaSubscription):
    def __init__(self, subscription_params: List[CandlesticksSubscriptionParams], callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.subscription_params = subscription_params

    @staticmethod
    def get_channel_name():
        return "CANDLESTICKS"

    def get_subscription_message(self, **kwargs) -> dict:
        return {
            "name": self.get_channel_name(),
            "properties": [{
                "instrument_code": map_pair(params.pair),
                "time_granularity": {
                    "unit": params.unit.value,
                    "period": params.period
                }
            } for params in sorted(self.subscription_params)]
        }


class MarketTickerSubscription(BitpandaSubscription):
    def __init__(self, pairs: List[Pair], callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.pairs = pairs

    @staticmethod
    def get_channel_name():
        return "MARKET_TICKER"

    def get_subscription_message(self, **kwargs) -> dict:
        return {
            "name": self.get_channel_name(),
            "instrument_codes": map_multiple_pairs(self.pairs, sort = True)
        }


class TradingSubscription(BitpandaSubscription):
    def __init__(self, callbacks: CallbacksType = None):
        super().__init__(callbacks)

    @staticmethod
    def get_channel_name():
        return "TRADING"

    def get_subscription_message(self, **kwargs) -> dict:
        return {
            "name": self.get_channel_name(),
        }

    def requires_authentication(self) -> bool:
        return True


class OrdersSubscription(BitpandaSubscription):
    def __init__(self, callbacks: CallbacksType = None):
        super().__init__(callbacks)

    @staticmethod
    def get_channel_name():
        return "ORDERS"

    def get_subscription_message(self, **kwargs) -> dict:
        return {
            "name": self.get_channel_name(),
        }

    def requires_authentication(self) -> bool:
        return True


class CreateOrderMessage(WebsocketOutboundMessage):
    def __init__(self, pair: Pair, type: enums.OrderType, side: enums.OrderSide, amount: str, price: str = None,
                 stop_price: str = None, client_id: str = None):
        self.pair = pair
        self.type = type
        self.side = side
        self.amount = amount
        self.price = price
        self.stop_price = stop_price
        self.client_id = client_id

    def to_json(self):
        ret = {
            "type": "CREATE_ORDER",
            "order": {
                "instrument_code": map_pair(self.pair),
                "type": self.type.value,
                "side": self.side.value,
                "amount": self.amount
            }
        }

        if self.price is not None:
            ret['order']['price'] = self.price

        if self.stop_price is not None:
            ret['order']['trigger_price'] = self.stop_price

        if self.client_id is not None:
            ret['order']['client_id'] = self.client_id

        return ret


class CancelOrderMessage(WebsocketOutboundMessage):
    def __init__(self, order_id: str = None, client_id: str = None):
        self.order_id = order_id
        self.client_id = client_id

    def to_json(self):
        ret = {
            "type": "CANCEL_ORDER",
        }

        if self.order_id is not None:
            ret['order_id'] = self.order_id

        if self.client_id is not None:
            ret['client_id'] = self.client_id

        return ret