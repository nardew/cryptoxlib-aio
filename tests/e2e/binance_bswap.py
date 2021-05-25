import unittest
import os
import logging

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.clients.binance import enums
from cryptoxlib.clients.binance.exceptions import BinanceRestException
from cryptoxlib.Pair import Pair

from CryptoXLibTest import CryptoXLibTest

api_key = os.environ['BINANCEAPIKEY']
sec_key = os.environ['BINANCESECKEY']


class BinanceBSwapRestApi(CryptoXLibTest):
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

    async def test_get_bswap_pools(self):
        response = await self.client.get_bswap_pools()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_bswap_liquidity(self):
        response = await self.client.get_bswap_liquidity()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_bswap_liquidity_operations(self):
        response = await self.client.get_bswap_liquidity_operations()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_bswap_quote(self):
        response = await self.client.get_bswap_quote(Pair('BTC', 'USDT'), '1000')
        self.assertTrue(self.check_positive_response(response))

    async def test_get_bswap_swap_history(self):
        response = await self.client.get_bswap_swap_history()
        self.assertTrue(self.check_positive_response(response))

    async def test_bswap_add_liquidity(self):
        with self.assertRaises(BinanceRestException) as cm:
            await self.client.bswap_add_liquidity(0, 'BTC', '10000000')
        e = cm.exception

        self.assertEqual(e.status_code, 400)
        self.assertEqual(e.body['code'], -12017)

    async def test_bswap_remove_liquidity(self):
        with self.assertRaises(BinanceRestException) as cm:
            await self.client.bswap_remove_liquidity(0, 'BTC', '10000000', type = enums.LiquidityRemovalType.COMBINATION)
        e = cm.exception

        self.assertEqual(e.status_code, 400)
        self.assertEqual(e.body['code'], -9000)

    async def test_bswap_swap(self):
        with self.assertRaises(BinanceRestException) as cm:
            await self.client.bswap_swap(Pair('BTC', 'USDT'), '100000000000')
        e = cm.exception

        self.assertEqual(e.status_code, 400)
        self.assertEqual(e.body['code'], -12000)


if __name__ == '__main__':
    unittest.main()