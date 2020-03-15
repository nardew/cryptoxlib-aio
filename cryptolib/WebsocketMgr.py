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

    def get_subscription_id(self) -> Any:
        if self.subscription_id is None:
            self.subscription_id = self.construct_subscription_id()
            LOG.info(f"New subscription id constructed: {self.subscription_id}")

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
                 max_message_size: int = 2**20, ssl_context = None) -> None:
        self.websocket_uri = websocket_uri
        self.subscriptions = subscriptions
        self.builtin_ping_interval = builtin_ping_interval
        self.max_message_size = max_message_size
        self.ssl_context = ssl_context

    @abstractmethod
    def _create_subscription_message(self) -> Union[List[dict], dict]:
        pass

    @abstractmethod
    async def _process_message(self, websocket: websockets.WebSocketClientProtocol, response: str) -> None:
        pass

    async def run(self) -> None:
        for subscription in self.subscriptions:
            await subscription.initialize()

        try:
            # main loop ensuring proper reconnection after a graceful connection termination by the remote server
            while True:
                LOG.debug(f"Initiating websocket connection.")
                async with websockets.connect(self.websocket_uri, ping_interval = self.builtin_ping_interval,
                                              max_size = self.max_message_size, ssl = self.ssl_context) as websocket:
                    subscription_message = self._create_subscription_message()
                    LOG.debug(f"> {subscription_message}")
                    await websocket.send(json.dumps(subscription_message))

                    # start processing incoming messages
                    while True:
                        message = await websocket.recv()
                        LOG.debug(f"< {message}")

                        await self._process_message(websocket, message)
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
