import unittest
import os
import logging

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.clients.bitforex import enums
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.bitforex.exceptions import BitforexRestException

from CryptoXLibTest import CryptoXLibTest

api_key = os.environ['BITFOREXAPIKEY']
sec_key = os.environ['BITFOREXSECKEY']


class BitforexRestApi(CryptoXLibTest):
    @classmethod
    def initialize(cls) -> None:
        cls.print_logs = True
        cls.log_level = logging.DEBUG

    async def init_test(self):
        self.client = CryptoXLib.create_bitforex_client(api_key, sec_key)

    async def clean_test(self):
        await self.client.close()

    def check_positive_response(self, response):
        return response['response']['success'] is True

    async def test_get_exchange_info(self):
        response = await self.client.get_exchange_info()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_order_book(self):
        response = await self.client.get_order_book(pair = Pair('ETH', 'BTC'), depth = "1")
        self.assertTrue(self.check_positive_response(response))

    async def test_get_ticker(self):
        response = await self.client.get_ticker(pair = Pair('ETH', 'BTC'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_single_fund(self):
        response = await self.client.get_single_fund(currency = "NOBS")
        self.assertTrue(self.check_positive_response(response))

    async def test_get_funds(self):
        response = await self.client.get_funds()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_trades(self):
        response = await self.client.get_trades(pair = Pair('ETH', 'BTC'), size = "1")
        self.assertTrue(self.check_positive_response(response))

    async def test_get_candlesticks(self):
        response = await self.client.get_candlesticks(pair = Pair('ETH', 'BTC'), interval = enums.CandlestickInterval.I_1W, size = "5")
        self.assertTrue(self.check_positive_response(response))

    async def test_create_order(self):
        with self.assertRaises(BitforexRestException) as cm:
            await self.client.create_order(Pair("ETH", "BTC"), side = enums.OrderSide.SELL, quantity = "1", price = "1")
        e = cm.exception

        self.assertEqual(e.body['code'], '3002')

    async def test_create_multi_order(self):
        response = await self.client.create_multi_order(Pair("ETH", "BTC"),
                                          orders = [("1", "1", enums.OrderSide.SELL), ("2", "1", enums.OrderSide.SELL)])
        self.assertTrue(self.check_positive_response(response))

    async def test_cancel_order(self):
        response = await self.client.cancel_order(pair = Pair('ETH', 'BTC'), order_id = "10")
        self.assertTrue(self.check_positive_response(response))

    async def test_cancel_multi_order(self):
        response = await self.client.cancel_multi_order(pair = Pair('ETH', 'BTC'), order_ids = ["10", "20"])
        self.assertTrue(self.check_positive_response(response))

    async def test_cancel_all_orders(self):
        response = await self.client.cancel_all_orders(pair = Pair('ETH', 'BTC'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_order(self):
        with self.assertRaises(BitforexRestException) as cm:
            await self.client.get_order(pair = Pair('ETH', 'BTC'), order_id = "1")
        e = cm.exception

        self.assertEqual(e.body['code'], '4004')

    async def test_get_orders(self):
        response = await self.client.get_orders(pair = Pair('ETH', 'BTC'), order_ids = ["1", "2"])
        self.assertTrue(self.check_positive_response(response))

    async def test_find_order(self):
        response = await self.client.find_order(pair = Pair('ETH', 'BTC'), state = enums.OrderState.PENDING)
        self.assertTrue(self.check_positive_response(response))


if __name__ == '__main__':
    unittest.main()