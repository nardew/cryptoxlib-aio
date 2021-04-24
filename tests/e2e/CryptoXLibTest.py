import logging
import sys
import asyncio
from typing import Any, List

import aiounittest

from cryptoxlib.version_conversions import async_run

LOG = logging.getLogger("cryptoxlib")


class CryptoXLibWsSuccessException(Exception):
    pass


class WsMessageCounterCallback(object):
    message_counts = {}

    def __init__(self, ws_message_counter: 'WsMessageCounter', target_count: int, name: str = None):
        self.ws_message_counter = ws_message_counter
        self.name = name

        self.current_count = 0
        self.target_count = target_count

    async def process_message(self, message):
        self.current_count += 1

        if self.current_count == self.target_count:
            LOG.info(f"Message count reached [counter = {self.name}].")

            self.ws_message_counter.check_target_reached()

    def __call__(self, *args, **kwargs) -> Any:
        return self.process_message(args[0])


class WsMessageCounter(object):
    def __init__(self):
        self.callbacks: List[WsMessageCounterCallback] = []

    def generate_callback(self, target_count: int, name: str = None) -> WsMessageCounterCallback:
        callback = WsMessageCounterCallback(self, target_count, name)
        self.callbacks.append(callback)

        return callback

    def check_target_reached(self):
        target_reached = True
        for callback in self.callbacks:
            if callback.current_count < callback.target_count:
                target_reached = False
                break

        if target_reached:
            raise CryptoXLibWsSuccessException("Websocket message count reached successfully.")


class CryptoXLibTest(aiounittest.AsyncTestCase):
    print_logs: bool = True
    log_level: int = logging.DEBUG

    def __init__(self, methodName = None):
        super().__init__(methodName)

    @classmethod
    def initialize(cls) -> None:
        pass

    @classmethod
    def setUpClass(cls) -> None:
        cls.initialize()

        LOG.setLevel(cls.log_level)
        if cls.print_logs:
            LOG.addHandler(logging.StreamHandler())

    @classmethod
    def tearDownClass(cls) -> None:
        pass

    async def init_test(self):
        pass

    async def clean_test(self):
        pass

    def setUp(self) -> None:
        return async_run(self.init_test())

    def tearDown(self) -> None:
        return async_run(self.clean_test())

    def get_event_loop(self):
        if not hasattr(self, 'loop'):
            self.loop = asyncio.new_event_loop()
            return self.loop
        else:
            return self.loop

    async def assertWsMessageCount(self, ws_message_counter: WsMessageCounter, timeout: float = 25.0):
        try:
            await asyncio.wait_for(self.client.start_websockets(), timeout = timeout)
        except CryptoXLibWsSuccessException as e:
            LOG.info(f"SUCCESS exception: {e}")
            return True
        except asyncio.TimeoutError:
            msg_string = ''
            for counter in ws_message_counter.callbacks:
                name = counter.name if counter.name is not None else 'counter'
                current_count = counter.current_count
                target_count = counter.target_count

                msg_string += f"{name} {current_count}/{target_count}, "

            self.fail(f"Websocket message count timeout ({timeout} secs). Processed messages: {msg_string[:-2]}.")