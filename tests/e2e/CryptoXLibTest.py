import logging
import asyncio

import aiounittest

LOG = logging.getLogger("cryptoxlib")


class CryptoXLibTest(aiounittest.AsyncTestCase):
    client = None
    print_logs: bool = True
    log_level: int = logging.DEBUG

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
        asyncio.run(cls.client.close())

    def get_event_loop(self):
        return asyncio.get_event_loop()