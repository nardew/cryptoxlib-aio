import websockets
import json
import logging
import asyncio
import ssl
import aiohttp
from abc import ABC, abstractmethod
from typing import List, Callable, Any, Optional, Union

from cryptoxlib.exceptions import CryptoXLibException, WebsocketReconnectionException, WebsocketClosed, WebsocketError

LOG = logging.getLogger(__name__)

CallbacksType = List[Callable[..., Any]]


class Websocket(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    async def receive(self):
        pass

    @abstractmethod
    async def send(self, message: str):
        pass


class FullWebsocket(Websocket):
    def __init__(self, websocket_uri: str, builtin_ping_interval: Optional[float] = 20,
                 max_message_size: int = 2**20, ssl_context: ssl.SSLContext = None):
        super().__init__()

        self.websocket_uri = websocket_uri
        self.builtin_ping_interval = builtin_ping_interval
        self.max_message_size = max_message_size
        self.ssl_context = ssl_context

        self.ws = None

    async def connect(self):
        if self.ws is not None:
            raise CryptoXLibException("Websocket reattempted to make connection while previous one is still active.")

        LOG.debug(f"Connecting to websocket {self.websocket_uri}")
        self.ws = await websockets.connect(self.websocket_uri,
                                           ping_interval = self.builtin_ping_interval,
                                           max_size = self.max_message_size,
                                           ssl = self.ssl_context)

    async def close(self):
        if self.ws is None:
            raise CryptoXLibException("Websocket attempted to close connection while connection not open.")

        await self.ws.close()
        self.ws = None

    async def receive(self):
        if self.ws is None:
            raise CryptoXLibException("Websocket attempted to read data while connection not open.")

        return await self.ws.recv()

    async def send(self, message: str):
        if self.ws is None:
            raise CryptoXLibException("Websocket attempted to send data while connection not open.")

        return await self.ws.send(message)

class AiohttpWebsocket(Websocket):
    def __init__(self, websocket_uri: str, builtin_ping_interval: Optional[float] = 20,
                 max_message_size: int = 2 ** 20, ssl_context: ssl.SSLContext = None):
        super().__init__()

        self.websocket_uri = websocket_uri
        self.builtin_ping_interval = builtin_ping_interval
        self.max_message_size = max_message_size
        self.ssl_context = ssl_context

        self.ws = None

    async def connect(self):
        if self.ws is not None:
            raise CryptoXLibException("Websocket reattempted to make connection while previous one is still active.")

        self.session = aiohttp.ClientSession()
        self.ws = await self.session.ws_connect(url = self.websocket_uri,
                                           max_msg_size = self.max_message_size,
                                           autoping = True,
                                           heartbeat = self.builtin_ping_interval,
                                           ssl_context = self.ssl_context)

    async def close(self):
        if self.ws is None:
            raise CryptoXLibException("Websocket attempted to close connection while connection not open.")

        await self.ws.close()
        await self.session.close()
        self.ws = None
        self.session = None

    async def receive(self):
        if self.ws is None:
            raise CryptoXLibException("Websocket attempted to read data while connection not open.")

        message = await self.ws.receive()

        if message.type == aiohttp.WSMsgType.TEXT:
            if message.data == 'close cmd':
                raise WebsocketClosed(f'Websocket was closed: {message.data}')
            else:
                return message.data
        elif message.type == aiohttp.WSMsgType.CLOSED:
            raise WebsocketClosed(f'Websocket was closed: {message.data}')
        elif message.type == aiohttp.WSMsgType.ERROR:
            raise WebsocketError(f'Websocket error: {message.data}')

    async def send(self, message: str):
        if self.ws is None:
            raise CryptoXLibException("Websocket attempted to send data while connection not open.")

        return await self.ws.send_str(message)


class WebsocketOutboundMessage(ABC):
    @abstractmethod
    def to_json(self):
        pass


class ClientWebsocketHandle(object):
    def __init__(self, websocket: Websocket):
        self.websocket = websocket

    async def send(self, message: Union[str, dict, WebsocketOutboundMessage]):
        if isinstance(message, str):
            pass
        elif isinstance(message, dict):
            message = json.dumps(message)
        elif isinstance(message, WebsocketOutboundMessage):
            message = json.dumps(message.to_json())
        else:
            raise CryptoXLibException("Only string or JSON serializable objects can be sent over the websocket.")

        LOG.debug(f"> {message}")
        return await self.websocket.send(message)

    async def receive(self):
        return await self.websocket.receive()


class WebsocketMessage(object):
    def __init__(self, subscription_id: Any, message: dict, websocket: ClientWebsocketHandle = None) -> None:
        self.subscription_id = subscription_id
        self.message = message
        self.websocket = websocket


class Subscription(ABC):
    def __init__(self, callbacks: CallbacksType = None):
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

    async def initialize(self, **kwargs) -> None:
        pass

    async def process_message(self, message: WebsocketMessage) -> None:
        await self.process_callbacks(message)

    async def process_callbacks(self, message: WebsocketMessage) -> None:
        if self.callbacks is not None:
            tasks = []
            for cb in self.callbacks:
                # If message contains a websocket, then the websocket handle will be passed to the callbacks.
                # This is useful for duplex websockets
                if message.websocket is not None:
                    tasks.append(asyncio.create_task(cb(message.message, message.websocket)))
                else:
                    tasks.append(asyncio.create_task(cb(message.message)))
            await asyncio.gather(*tasks)


class WebsocketMgr(ABC):
    def __init__(self, websocket_uri: str, subscriptions: List[Subscription], builtin_ping_interval: Optional[float] = 20,
                 max_message_size: int = 2**20, periodic_timeout_sec: int = None, ssl_context = None,
                 auto_reconnect: bool = False) -> None:
        self.websocket_uri = websocket_uri
        self.subscriptions = subscriptions
        self.builtin_ping_interval = builtin_ping_interval
        self.max_message_size = max_message_size
        self.periodic_timeout_sec = periodic_timeout_sec
        self.ssl_context = ssl_context
        self.auto_reconnect = auto_reconnect

    @abstractmethod
    async def _process_message(self, websocket: Websocket, response: str) -> None:
        pass

    async def _process_periodic(self, websocket: Websocket) -> None:
        pass

    def get_websocket_uri_variable_part(self):
        return ""

    def get_websocket(self) -> Websocket:
        return self.get_full_websocket()

    def get_full_websocket(self) -> Websocket:
        return FullWebsocket(websocket_uri = self.websocket_uri + self.get_websocket_uri_variable_part(),
                      builtin_ping_interval = self.builtin_ping_interval,
                      max_message_size = self.max_message_size,
                      ssl_context = self.ssl_context)

    def get_aiohttp_websocket(self) -> Websocket:
        return AiohttpWebsocket(websocket_uri = self.websocket_uri + self.get_websocket_uri_variable_part(),
                      builtin_ping_interval = self.builtin_ping_interval,
                      max_message_size = self.max_message_size,
                      ssl_context = self.ssl_context)

    async def validate_subscriptions(self) -> None:
        pass

    async def initialize_subscriptions(self) -> None:
        for subscription in self.subscriptions:
            await subscription.initialize()

    async def _authenticate(self, websocket: Websocket):
        pass

    async def _subscribe(self, websocket: Websocket):
        subscription_messages = []
        for subscription in self.subscriptions:
            subscription_messages.append(subscription.get_subscription_message())

        LOG.debug(f"> {subscription_messages}")
        await websocket.send(json.dumps(subscription_messages))

    async def main_loop(self, websocket: Websocket):
        await self._authenticate(websocket)
        await self._subscribe(websocket)

        # start processing incoming messages
        while True:
            message = await websocket.receive()
            LOG.debug(f"< {message}")

            await self._process_message(websocket, message)

    async def periodic_loop(self, websocket: Websocket):
        if self.periodic_timeout_sec is not None:
            while True:
                await self._process_periodic(websocket)
                await asyncio.sleep(self.periodic_timeout_sec)

    async def run(self) -> None:
        await self.validate_subscriptions()
        await self.initialize_subscriptions()

        try:
            # main loop ensuring proper reconnection if required
            while True:
                LOG.debug(f"Initiating websocket connection.")
                websocket = None
                try:
                        websocket = self.get_websocket()
                        await websocket.connect()

                        done, pending = await asyncio.wait(
                            [asyncio.create_task(self.main_loop(websocket)),
                             asyncio.create_task(self.periodic_loop(websocket))],
                            return_when = asyncio.FIRST_EXCEPTION
                        )
                        for task in done:
                            try:
                                task.result()
                            except Exception:
                                LOG.debug("Websocket processing has led to an exception, all pending tasks will be cancelled.")
                                for task in pending:
                                    if not task.cancelled():
                                        task.cancel()
                                if len(pending) > 0:
                                    try:
                                        await asyncio.wait(pending, return_when = asyncio.ALL_COMPLETED)
                                    except asyncio.CancelledError:
                                        await asyncio.wait(pending, return_when = asyncio.ALL_COMPLETED)
                                        raise
                                    finally:
                                        LOG.debug("All pending tasks cancelled successfully.")
                                raise
                except (websockets.ConnectionClosedError,
                        websockets.ConnectionClosedOK,
                        websockets.InvalidStatusCode,
                        ConnectionResetError,
                        WebsocketClosed,
                        WebsocketError,
                        WebsocketReconnectionException) as e:
                    if self.auto_reconnect:
                        LOG.info("A recoverable exception has occurred, the websocket will be restarted automatically.")
                        self._print_subscriptions()
                        LOG.info(f"Exception: {e}")
                    else:
                        raise
                finally:
                    if websocket is not None:
                        LOG.debug("Closing websocket connection.")
                        await websocket.close()
        except asyncio.CancelledError:
            LOG.warning(f"The websocket was requested to be shutdown.")
        except Exception:
            LOG.error(f"An exception occurred. The websocket manager will be closed.")
            self._print_subscriptions()
            raise

    async def publish_message(self, message: WebsocketMessage) -> None:
        for subscription in self.subscriptions:
            if subscription.get_subscription_id() == message.subscription_id:
                await subscription.process_message(message)
                return

        LOG.warning(f"Websocket message with subscription id {message.subscription_id} did not identify any subscription!")

    def _print_subscriptions(self):
        subscription_messages = []
        for subscription in self.subscriptions:
            subscription_messages.append(subscription.get_subscription_id())
        LOG.info(f"Subscriptions: {subscription_messages}")