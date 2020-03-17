import websockets
import json
import logging
import asyncio
from abc import ABC, abstractmethod
from typing import List, Callable, Any, Union, Optional

LOG = logging.getLogger(__name__)


class Subscription(ABC):
    def __init__(self, callbacks: Optional[List[Callable[[dict], Any]]] = None):
        self.callbacks = callbacks

        self.subscription_id = None

    @abstractmethod
    def construct_subscription_id(self) -> Any:
        pass

    @abstractmethod
    def get_subscription_message(self, **kwargs) -> dict:
        pass

    def get_subscription_id(self) -> Any:
        if self.subscription_id is None:
            self.subscription_id = self.construct_subscription_id()
            LOG.debug(f"New subscription id constructed: {self.subscription_id}")

        return self.subscription_id

    async def initialize(self) -> None:
        pass

    async def process_message(self, response: dict) -> None:
        await self.process_callbacks(response)

    async def process_callbacks(self, response: dict) -> None:
        if self.callbacks is not None:
            await asyncio.gather(*[asyncio.create_task(cb(response)) for cb in self.callbacks])


class WebsocketMessage(object):
    def __init__(self, subscription_id: Any, message: dict) -> None:
        self.subscription_id = subscription_id
        self.message = message


class WebsocketMgr(ABC):
    def __init__(self, websocket_uri: str, subscriptions: List[Subscription], builtin_ping_interval: Optional[float] = 20,
                 max_message_size: int = 2**20, periodic_timeout_sec: int = None, ssl_context = None) -> None:
        self.websocket_uri = websocket_uri
        self.subscriptions = subscriptions
        self.builtin_ping_interval = builtin_ping_interval
        self.max_message_size = max_message_size
        self.periodic_timeout_sec = periodic_timeout_sec
        self.ssl_context = ssl_context

    @abstractmethod
    async def _process_message(self, websocket: websockets.WebSocketClientProtocol, response: str) -> None:
        pass

    async def _process_periodic(self, websocket: websockets.WebSocketClientProtocol) -> None:
        pass

    async def _subscribe(self, websocket: websockets.WebSocketClientProtocol):
        subscription_messages = []
        for subscription in self.subscriptions:
            subscription_messages.append(subscription.get_subscription_message())

        LOG.debug(f"> {subscription_messages}")
        await websocket.send(json.dumps(subscription_messages))

    async def main_loop(self, websocket: websockets.WebSocketClientProtocol):
        await self._subscribe(websocket)

        # start processing incoming messages
        while True:
            message = await websocket.recv()
            LOG.debug(f"< {message}")

            await self._process_message(websocket, message)

    async def periodic_loop(self, websocket: websockets.WebSocketClientProtocol):
        if self.periodic_timeout_sec is not None:
            while True:
                await self._process_periodic(websocket)
                await asyncio.sleep(self.periodic_timeout_sec)

    async def run(self) -> None:
        for subscription in self.subscriptions:
            await subscription.initialize()

        try:
            # main loop ensuring proper reconnection after a graceful connection termination by the remote server
            while True:
                LOG.debug(f"Initiating websocket connection.")
                async with websockets.connect(self.websocket_uri, ping_interval = self.builtin_ping_interval,
                                              max_size = self.max_message_size, ssl = self.ssl_context) as websocket:
                    done, pending = await asyncio.wait(
                        [asyncio.create_task(self.main_loop(websocket)),
                         asyncio.create_task(self.periodic_loop(websocket))],
                        return_when = asyncio.FIRST_EXCEPTION
                    )
                    for task in done:
                        try:
                            task.result()
                        except Exception:
                            for task in pending:
                                if not task.cancelled():
                                    task.cancel()
                            raise
        except asyncio.CancelledError:
            LOG.warning(f"The websocket was requested to be shutdown.")
        except Exception:
            LOG.error(f"An exception occurred. The websocket will be closed.")
            raise

    async def publish_message(self, message: WebsocketMessage) -> None:
        for subscription in self.subscriptions:
            if subscription.get_subscription_id() == message.subscription_id:
                await subscription.process_message(message.message)
                return

        LOG.warning(f"Websocket message with subscription id {message.subscription_id} did not identify any subscription!")
