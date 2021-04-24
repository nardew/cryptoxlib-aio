import json
import logging
import websockets
from abc import abstractmethod
from typing import List, Callable, Any, Union, Optional

from cryptoxlib.WebsocketMgr import Subscription, WebsocketMgr, WebsocketMessage, Websocket
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.bitforex import enums
from cryptoxlib.clients.bitforex.exceptions import BitforexException
from cryptoxlib.clients.bitforex.functions import map_pair
from cryptoxlib.PeriodicChecker import PeriodicChecker

LOG = logging.getLogger(__name__)


class BitforexWebsocket(WebsocketMgr):
    WEBSOCKET_URI = "wss://www.bitforex.com/mkapi/coinGroup1/ws"

    PING_MSG = 'ping_p'
    PONG_MSG = 'pong_p'

    def __init__(self, subscriptions: List[Subscription], ssl_context = None) -> None:
        super().__init__(websocket_uri = BitforexWebsocket.WEBSOCKET_URI, subscriptions = subscriptions,
                         builtin_ping_interval = None, periodic_timeout_sec = 10, ssl_context = ssl_context)

        self.ping_checker = PeriodicChecker(period_ms = 30 * 1000)

    async def _process_periodic(self, websocket: Websocket) -> None:
        if self.ping_checker.check():
            LOG.debug(f"> {BitforexWebsocket.PING_MSG}")
            await websocket.send(BitforexWebsocket.PING_MSG)

    async def _process_message(self, websocket: Websocket, message: str) -> None:
        if message != BitforexWebsocket.PONG_MSG:
            message = json.loads(message)
            subscription_id = BitforexSubscription.make_subscription_id(message['event'], message['param'])
            await self.publish_message(WebsocketMessage(subscription_id = subscription_id, message = message))


class BitforexSubscription(Subscription):
    def __init__(self, callbacks: Optional[List[Callable[[dict], Any]]] = None):
        super().__init__(callbacks)

    @staticmethod
    def get_channel_name() -> str:
        pass

    @abstractmethod
    def get_params(self) -> dict:
        pass

    @staticmethod
    def make_subscription_id(channel: str, params: dict) -> dict:
        subscription_id = {'channel': channel}

        if channel == OrderBookSubscription.get_channel_name():
            subscription_id.update(params)
        elif channel == TradeSubscription.get_channel_name():
            subscription_id['businessType'] = params['businessType']
        elif channel == TickerSubscription.get_channel_name():
            subscription_id['businessType'] = params['businessType']
            subscription_id['kType'] = params['kType']
        elif channel == Ticker24hSubscription.get_channel_name():
            subscription_id.update(params)
        else:
            raise BitforexException(f'Unknown channel name {channel}')

        return subscription_id

    def construct_subscription_id(self) -> Any:
        return BitforexSubscription.make_subscription_id(self.get_channel_name(), self.get_params())

    def get_subscription_message(self, **kwargs) -> dict:
        return {
                "type": "subHq",
                "event": self.get_channel_name(),
                "param": self.get_params(),
            }


class OrderBookSubscription(BitforexSubscription):
    def __init__(self, pair: Pair, depth: str, callbacks: Optional[List[Callable[[dict], Any]]] = None):
        super().__init__(callbacks)

        self.pair = pair
        self.depth = depth

    @staticmethod
    def get_channel_name():
        return "depth10"

    def get_params(self):
        return {
            "businessType": map_pair(self.pair),
            "dType": int(self.depth)
        }


class Ticker24hSubscription(BitforexSubscription):
    def __init__(self, pair: Pair, callbacks: List[Callable[[dict], Any]] = None):
        super().__init__(callbacks)

        self.pair = pair

    @staticmethod
    def get_channel_name():
        return "ticker"

    def get_params(self):
        return {
            "businessType": map_pair(self.pair)
        }


class TickerSubscription(BitforexSubscription):
    def __init__(self, pair: Pair, size: str, interval: enums.CandlestickInterval, callbacks: List[Callable[[dict], Any]] = None):
        super().__init__(callbacks)

        self.pair = pair
        self.size = size
        self.interval = interval

    @staticmethod
    def get_channel_name():
        return "kline"

    def get_params(self):
        return {
            "businessType": map_pair(self.pair),
            "size": int(self.size),
            "kType": self.interval.value
        }


class TradeSubscription(BitforexSubscription):
    def __init__(self, pair: Pair, size: str, callbacks: List[Callable[[dict], Any]] = None):
        super().__init__(callbacks)

        self.pair = pair
        self.size = size

    @staticmethod
    def get_channel_name():
        return "trade"

    def get_params(self):
        return {
            "businessType": map_pair(self.pair),
            "size": int(self.size)
        }
