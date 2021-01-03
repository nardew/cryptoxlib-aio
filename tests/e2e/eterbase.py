import unittest
import os
import logging
import datetime

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.clients.eterbase import enums
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.eterbase.exceptions import EterbaseRestException

from CryptoXLibTest import CryptoXLibTest, WsMessageCounter

api_key = os.environ['ETERBASEAPIKEY']
sec_key = os.environ['ETERBASESECKEY']


class EterbaseRestApi(CryptoXLibTest):
    @classmethod
    def initialize(cls) -> None:
        cls.print_logs = True
        cls.log_level = logging.DEBUG

    def check_positive_response(self, response):
        return str(response['status_code'])[0] == '2'

    async def init_test(self):
        self.client = CryptoXLib.create_eterbase_client(api_key, sec_key)

    async def clean_test(self):
        await self.client.close()

    async def test_get_ping(self):
        response = await self.client.get_ping()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_currencies(self):
        response = await self.client.get_currencies()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_markets(self):
        response = await self.client.get_markets()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_balances(self):
        response = await self.client.get_balances("xyz")
        self.assertTrue(self.check_positive_response(response))

    async def test_create_order(self):
        with self.assertRaises(EterbaseRestException) as cm:
            await self.client.create_order(account_id = "xyz", pair_id = "xyz", side = enums.OrderSide.BUY,
                                                      type = enums.OrderType.LIMIT, amount = "100000", price = "1",
                                                      time_in_force = enums.TimeInForce.GOOD_TILL_CANCELLED)
        e = cm.exception

        self.assertEqual(e.status_code, 400)
        self.assertEqual(e.body['error']['code'], 20001)

    async def test_cancel_order(self):
        with self.assertRaises(EterbaseRestException) as cm:
            await self.client.cancel_order(order_id = "12345678")
        e = cm.exception

        self.assertEqual(e.status_code, 400)
        self.assertEqual(e.body['error']['code'], 20002)


if __name__ == '__main__':
    unittest.main()