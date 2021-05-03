import json
import logging
import datetime
import hmac
import hashlib
from typing import List, Any

from cryptoxlib.WebsocketMgr import Subscription, WebsocketMgr, WebsocketMessage, Websocket, CallbacksType
from cryptoxlib.clients.eterbase.exceptions import EterbaseException

LOG = logging.getLogger(__name__)


class EterbaseWebsocket(WebsocketMgr):
    WEBSOCKET_URI = "wss://api.eterbase.exchange/feed"
    MAX_MESSAGE_SIZE = 3 * 1024 * 1024  # 3MB

    def __init__(self, subscriptions: List[Subscription], eterbase_client, account_id: str = None,
                 ssl_context = None, startup_delay_ms: int = 0) -> None:
        super().__init__(websocket_uri = self.WEBSOCKET_URI, subscriptions = subscriptions,
                         ssl_context = ssl_context,
                         builtin_ping_interval = None,
                         auto_reconnect = True,
                         max_message_size = self.MAX_MESSAGE_SIZE,
                         periodic_timeout_sec = 30,
                         startup_delay_ms = startup_delay_ms)

        self.eterbase_client = eterbase_client
        self.account_id = account_id

    def get_websocket(self) -> Websocket:
        return self.get_aiohttp_websocket()

    def get_websocket_uri_variable_part(self):
        for subscription in self.subscriptions:
            if subscription.requires_authentication() is True:
                return f"?wstoken={subscription.token}"

        return ""

    async def initialize_subscriptions(self, subscriptions: List[Subscription]) -> None:
        for subscription in subscriptions:
            await subscription.initialize(eterbase_client = self.eterbase_client)

    async def _process_periodic(self, websocket: Websocket) -> None:
        ping_msg = {
            "type": "ping"
        }
        LOG.debug(f"> {ping_msg}")
        await websocket.send(json.dumps(ping_msg))

    async def send_subscription_message(self, subscriptions: List[Subscription]):
        for subscription in subscriptions:
            subscription_message = subscription.get_subscription_message(account_id = self.account_id)
            LOG.debug(f"> {subscription_message}")
            await self.websocket.send(json.dumps(subscription_message))

    async def _process_message(self, websocket: Websocket, message: str) -> None:
        message = json.loads(message)

        if 'type' not in message:
            LOG.error(f"ERROR: Message without 'type' property received: {message}")
        elif message['type'] == 'pong':
            # ignore pong responses
            pass
        else:
            # regular message
            subscription_id = self._map_message_to_subscription_id(message)
            await self.publish_message(WebsocketMessage(
                subscription_id = subscription_id,
                message = message)
            )

    def _map_message_to_subscription_id(self, message: dict):
        if message['type'] in ['ob_snapshot', 'ob_update']:
            return "order_book"
        elif message['type'] == 'trade':
            return "trade_history"
        elif message['type'] == 'ohlcv':
            return "ohlcv_tick"
        elif message['type'] in ["o_placed", "o_rejected", "o_fill", "o_closed", "o_triggered"]:
            return "account"
        else:
            return ""


class EterbaseSubscription(Subscription):
    def __init__(self, callbacks: CallbacksType = None):
        super().__init__(callbacks)

    def requires_authentication(self) -> bool:
        return False


class AccountSubscription(EterbaseSubscription):
    def __init__(self, market_ids: List[str], callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.market_ids = market_ids

    def get_subscription_message(self, **kwargs) -> dict:
        return {
            "type": "subscribe",
            "channelId": "my_orders",
            "marketIds": self.market_ids,
            "accountId": kwargs['account_id']
        }

    def construct_subscription_id(self) -> Any:
        return "account"

    def requires_authentication(self) -> bool:
        return True

    async def initialize(self, **kwargs):
        eterbase_client = kwargs['eterbase_client']
        token_response = await eterbase_client.get_token()
        self.token = token_response["response"]["wstoken"]
        LOG.debug(f'Token: {self.token}')


class OrderbookSubscription(EterbaseSubscription):
    def __init__(self, market_ids: List[str], callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.market_ids = market_ids

    def get_subscription_message(self, **kwargs) -> dict:
        return {
            "type": "subscribe",
            "channelId": "order_book",
            "marketIds": self.market_ids
        }

    def construct_subscription_id(self) -> Any:
        return f"order_book"


class OHLCVSubscription(EterbaseSubscription):
    def __init__(self, market_ids: List[str], callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.market_ids = market_ids

    def get_subscription_message(self, **kwargs) -> dict:
        return {
            "type": "subscribe",
            "channelId": "ohlcv_tick",
            "marketIds": self.market_ids
        }

    def construct_subscription_id(self) -> Any:
        return f"ohlcv_tick"


class TradesSubscription(EterbaseSubscription):
    def __init__(self, market_ids: List[str], callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.market_ids = market_ids

    def get_subscription_message(self, **kwargs) -> dict:
        return {
            "type": "subscribe",
            "channelId": "trade_history",
            "marketIds": self.market_ids
        }

    def construct_subscription_id(self) -> Any:
        return f"trade_history"