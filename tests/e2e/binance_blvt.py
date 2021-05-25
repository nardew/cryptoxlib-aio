import unittest
import os
import logging

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.clients.binance.exceptions import BinanceRestException

from CryptoXLibTest import CryptoXLibTest

api_key = os.environ['BINANCEAPIKEY']
sec_key = os.environ['BINANCESECKEY']


class BinanceBLVTRestApi(CryptoXLibTest):
    @classmethod
    def initialize(cls) -> None:
        cls.print_logs = True
        cls.log_level = logging.DEBUG

    async def init_test(self):
        self.client = CryptoXLib.create_binance_client(api_key, sec_key)

    async def clean_test(self):
        await self.client.close()

    def check_positive_response(self, response):
        return str(response['status_code'])[0] == '2'

    async def test_get_blvt_info(self):
        response = await self.client.get_blvt_info()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_blvt_subscribtion_record(self):
        response = await self.client.get_blvt_subscribtion_record()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_blvt_redemption_record(self):
        response = await self.client.get_blvt_redemption_record()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_blvt_user_info(self):
        response = await self.client.get_blvt_user_info()
        self.assertTrue(self.check_positive_response(response))

    async def test_blvt_subscribe(self):
        with self.assertRaises(BinanceRestException) as cm:
            await self.client.blvt_subscribe("BTCUP", "50000000000")
        e = cm.exception

        self.assertEqual(e.status_code, 400)
        self.assertEqual(e.body['code'], -5002)

    async def test_blvt_redeem(self):
        with self.assertRaises(BinanceRestException) as cm:
            await self.client.blvt_redeem("BTCUP", "50000000000")
        e = cm.exception

        self.assertEqual(e.status_code, 400)
        self.assertEqual(e.body['code'], -5002)


if __name__ == '__main__':
    unittest.main()