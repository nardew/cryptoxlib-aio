import unittest
import os
import logging
import datetime

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.clients.aax import enums
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.aax.exceptions import AAXRestException

from CryptoXLibTest import CryptoXLibTest

api_key = os.environ['AAXAPIKEY']
sec_key = os.environ['AAXSECKEY']


class BitpandaRestApi(CryptoXLibTest):
    @classmethod
    def initialize(cls) -> None:
        cls.print_logs = True
        cls.log_level = logging.DEBUG

    async def init_test(self):
        self.client = CryptoXLib.create_aax_client(api_key, sec_key)

    async def clean_test(self):
        await self.client.close()

    def check_response(self, response, code = 1):
        return str(response['status_code'])[0] == '2' and response['response']['code'] == code

    async def test_get_exchange_info(self):
        response = await self.client.get_exchange_info()
        self.assertTrue(self.check_response(response))

    async def test_get_funds(self):
        response = await self.client.get_funds()
        self.assertTrue(self.check_response(response))

    async def test_get_user_info(self):
        response = await self.client.get_user_info()
        self.assertTrue(self.check_response(response))

    async def test_create_spot_order(self):
        response = await self.client.create_spot_order(pair = Pair('BTC', 'USDT'), type = enums.OrderType.LIMIT,
                                                       side = enums.OrderSide.BUY, amount = "10000", price = "1")
        self.assertTrue(self.check_response(response))

    async def test_update_spot_order(self):
        response = await self.client.update_spot_order(order_id = "abcd", amount = "20000")
        self.assertTrue(self.check_response(response, 30000))

    async def test_cancel_spot_order(self):
        response = await self.client.cancel_spot_order(order_id = "abcd")
        self.assertTrue(self.check_response(response, 30000))

    async def test_cancel_batch_spot_order(self):
        response = await self.client.cancel_batch_spot_order(pair = Pair('BTC', 'USDT'))
        self.assertTrue(self.check_response(response, 30000))

    async def test_cancel_all_spot_order(self):
        response = await self.client.cancel_all_spot_order(timeout_ms = 0)
        self.assertTrue(self.check_response(response))


if __name__ == '__main__':
    unittest.main()