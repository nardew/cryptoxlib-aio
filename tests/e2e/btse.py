import unittest
import os
import logging
import datetime

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.clients.btse import enums
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.btse.exceptions import BtseRestException

from CryptoXLibTest import CryptoXLibTest

api_key = os.environ['BTSEAPIKEY']
sec_key = os.environ['BTSESECKEY']


class BtseRestApi(CryptoXLibTest):
    @classmethod
    def initialize(cls) -> None:
        cls.client = CryptoXLib.create_btse_client(api_key, sec_key)
        cls.print_logs = True
        cls.log_level = logging.DEBUG

    def check_positive_response(self, response):
        return str(response['status_code'])[0] == '2'

    async def test_get_time(self):
        response = await self.client.get_time()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_exchange_info(self):
        response = await self.client.get_exchange_info(pair = Pair('BTC', 'USD'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_order_book(self):
        response = await self.client.get_order_book(pair = Pair('BTC', 'USD'), depth = 3)
        self.assertTrue(self.check_positive_response(response))

    async def test_get_price(self):
        response = await self.client.get_price(pair = Pair('BTC', 'USD'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_funds(self):
        response = await self.client.get_funds()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_open_orders(self):
        response = await self.client.get_open_orders(pair = Pair('BTC', 'USD'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_fees(self):
        response = await self.client.get_fees(pair = Pair('BTC', 'USD'))
        self.assertTrue(self.check_positive_response(response))

    async def test_create_order(self):
        with self.assertRaises(BtseRestException) as cm:
            await self.client.create_order(pair = Pair('BTC', 'USD'), type = enums.OrderType.LIMIT,
                                           side = enums.OrderSide.BUY,
                                           amount = "10000", price = "1")
        e = cm.exception

        self.assertEqual(e.status_code, 401)

    async def test_cancel_order(self):
        response = await self.client.cancel_order(pair = Pair('BTC', 'USD'))
        self.assertTrue(self.check_positive_response(response))


if __name__ == '__main__':
    unittest.main()