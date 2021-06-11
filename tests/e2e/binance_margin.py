import unittest
import os
import logging
import datetime

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.clients.binance import enums
from cryptoxlib.clients.binance.exceptions import BinanceRestException
from cryptoxlib.clients.binance.BinanceWebsocket import CandlestickSubscription, DepthSubscription
from cryptoxlib.Pair import Pair

from CryptoXLibTest import CryptoXLibTest, WsMessageCounter

api_key = os.environ['BINANCEAPIKEY']
sec_key = os.environ['BINANCESECKEY']


class BinanceMarginRestApi(CryptoXLibTest):
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

    def check_error_code(self, e: BinanceRestException, status: str, code: str):
        return str(e.status_code) == status and str(e.body['code']) == code

    async def test_create_order1(self):
        with self.assertRaises(BinanceRestException) as cm:
            response = await self.client.create_margin_order(pair = Pair('BTC', 'USDT'), side = enums.OrderSide.BUY,
                                                             order_type = enums.OrderType.MARKET, quantity = '100')
            self.assertTrue(self.check_positive_response(response))
        e = cm.exception

        self.assertTrue(self.check_error_code(e, '400', '-2010')) # insufficient funds

    async def test_create_order2(self):
        with self.assertRaises(BinanceRestException) as cm:
            response = await self.client.create_margin_order(pair = Pair('BTC', 'USDT'), side = enums.OrderSide.BUY,
                                                             order_type = enums.OrderType.LIMIT, quantity = '100', price = "10000")
            self.assertTrue(self.check_positive_response(response))
        e = cm.exception

        self.assertTrue(self.check_error_code(e, '400', '-2010')) # insufficient funds

    async def test_create_order3(self):
        with self.assertRaises(BinanceRestException) as cm:
            response = await self.client.create_margin_order(pair = Pair('BTC', 'USDT'), side = enums.OrderSide.BUY,
                                                             order_type = enums.OrderType.LIMIT, quantity = '100', price = "10000",
                                                             time_in_force = enums.TimeInForce.FILL_OR_KILL)
            self.assertTrue(self.check_positive_response(response))
        e = cm.exception

        self.assertTrue(self.check_error_code(e, '400', '-2010')) # insufficient funds

    async def test_isolated_listen_key(self):
        response = await self.client.get_isolated_margin_listen_key(pair = Pair('BTC', 'USDT'))
        self.assertTrue(self.check_positive_response(response))

        response = await self.client.keep_alive_isolated_margin_listen_key(pair = Pair('BTC', 'USDT'),
                                                                           listen_key = response['response']['listenKey'])
        self.assertTrue(self.check_positive_response(response))

    async def test_cross_listen_key(self):
        response = await self.client.get_cross_margin_listen_key()
        self.assertTrue(self.check_positive_response(response))

        response = await self.client.keep_alive_cross_margin_listen_key(response['response']['listenKey'])
        self.assertTrue(self.check_positive_response(response))


if __name__ == '__main__':
    unittest.main()