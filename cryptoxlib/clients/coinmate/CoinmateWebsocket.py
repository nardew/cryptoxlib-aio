import json
import logging
import datetime
import hmac
import hashlib
from typing import List, Any

from cryptoxlib.WebsocketMgr import Subscription, WebsocketMgr, WebsocketMessage, Websocket, CallbacksType
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.coinmate.functions import map_pair
from cryptoxlib.clients.coinmate.exceptions import CoinmateException

LOG = logging.getLogger(__name__)


class CoinmateWebsocket(WebsocketMgr):
    WEBSOCKET_URI = "wss://coinmate.io/api/websocket"
    MAX_MESSAGE_SIZE = 3 * 1024 * 1024  # 3MB

    def __init__(self, subscriptions: List[Subscription],
                 user_id: str = None, api_key: str = None, sec_key: str = None,
                 ssl_context = None,
                 startup_delay_ms: int = 0) -> None:
        super().__init__(websocket_uri = self.WEBSOCKET_URI, subscriptions = subscriptions,
                         max_message_size = CoinmateWebsocket.MAX_MESSAGE_SIZE,
                         ssl_context = ssl_context,
                         auto_reconnect = True,
                         builtin_ping_interval = None,
                         startup_delay_ms = startup_delay_ms)

        self.user_id = user_id
        self.api_key = api_key
        self.sec_key = sec_key

    def get_websocket(self) -> Websocket:
        return self.get_aiohttp_websocket()

    async def initialize_subscriptions(self, subscriptions: List[Subscription]) -> None:
        for subscription in subscriptions:
            await subscription.initialize(user_id = self.user_id)

    async def send_subscription_message(self, subscriptions: List[Subscription]):
        for subscription in subscriptions:
            subscription_message = {
                "event": "subscribe",
                "data": {
                    "channel": subscription.get_subscription_message()
                }
            }

            if subscription.requires_authentication():
                nonce = int(datetime.datetime.now(tz = datetime.timezone.utc).timestamp() * 1000) # timestamp ms
                input_message = str(nonce) + str(self.user_id) + self.api_key

                m = hmac.new(self.sec_key.encode('utf-8'), input_message.encode('utf-8'), hashlib.sha256)

                subscription_message['data']['signature'] = m.hexdigest().upper()
                subscription_message['data']['clientId'] = self.user_id
                subscription_message['data']['publicKey'] = self.api_key
                subscription_message['data']['nonce'] = nonce

            LOG.debug(f"> {subscription_message}")
            await self.websocket.send(json.dumps(subscription_message))

            message = await self.websocket.receive()
            LOG.debug(f"< {message}")

            message = json.loads(message)
            if message['event'] == 'subscribe_success':
                LOG.info(f"Channel {subscription.get_subscription_message()} subscribed successfully.")
            else:
                raise CoinmateException(f"Subscription failed for channel {subscription.get_subscription_message()}. Response [{message}]")


    async def send_unsubscription_message(self, subscriptions: List[Subscription]):
        unsubscription_message = self._get_unsubscription_message(subscriptions)

        LOG.debug(f"> {unsubscription_message}")
        await self.websocket.send(json.dumps(unsubscription_message))

    async def _process_message(self, websocket: Websocket, message: str) -> None:
        message = json.loads(message)

        # data message
        if "event" in message and message['event'] == "data":
            await self.publish_message(WebsocketMessage(
                subscription_id = message['channel'],
                message = message
            ))


class CoinmateSubscription(Subscription):
    def __init__(self, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.user_id = None

    def construct_subscription_id(self) -> Any:
        return self.get_subscription_message()

    def requires_authentication(self) -> bool:
        return False

    async def initialize(self, **kwargs):
        self.user_id = kwargs['user_id']


class UserOrdersSubscription(CoinmateSubscription):
    def __init__(self, pair: Pair = None, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.pair = pair

    def get_subscription_message(self, **kwargs) -> dict:
        msg = f"private-open_orders-{self.user_id}"

        if self.pair is not None:
            msg += f"-{map_pair(self.pair)}"

        return msg

    def requires_authentication(self) -> bool:
        return True


class UserTradesSubscription(CoinmateSubscription):
    def __init__(self, pair: Pair = None, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.pair = pair

    def get_subscription_message(self, **kwargs) -> dict:
        msg = f"private-user-trades-{self.user_id}"

        if self.pair is not None:
            msg += f"-{map_pair(self.pair)}"

        return msg

    def requires_authentication(self) -> bool:
        return True


class UserTransfersSubscription(CoinmateSubscription):
    def __init__(self, callbacks: CallbacksType = None):
        super().__init__(callbacks)

    def get_subscription_message(self, **kwargs) -> dict:
        return f"private-user-transfers-{self.user_id}"

    def requires_authentication(self) -> bool:
        return True


class BalancesSubscription(CoinmateSubscription):
    def __init__(self, callbacks: CallbacksType = None):
        super().__init__(callbacks)

    def get_subscription_message(self, **kwargs) -> dict:
        return f"private-user_balances-{self.user_id}"

    def requires_authentication(self) -> bool:
        return True


class OrderbookSubscription(CoinmateSubscription):
    def __init__(self, pair: Pair, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.pair = pair

    def get_subscription_message(self, **kwargs) -> dict:
        return f"order_book-{map_pair(self.pair)}"


class TradesSubscription(CoinmateSubscription):
    def __init__(self, pair: Pair, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.pair = pair

    def get_subscription_message(self, **kwargs) -> dict:
        return f"trades-{map_pair(self.pair)}"


class TradeStatsSubscription(CoinmateSubscription):
    def __init__(self, pair: Pair, callbacks: CallbacksType = None):
        super().__init__(callbacks)

        self.pair = pair

    def get_subscription_message(self, **kwargs) -> dict:
        return f"statistics-{map_pair(self.pair)}"