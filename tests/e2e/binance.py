import unittest
import os
import logging
import datetime

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.clients.binance import enums
from cryptoxlib.clients.binance.BinanceWebsocket import CandlestickSubscription, DepthSubscription
from cryptoxlib.Pair import Pair

from CryptoXLibTest import CryptoXLibTest, WsMessageCounter

api_key = os.environ['BINANCEAPIKEY']
sec_key = os.environ['BINANCESECKEY']


class BinanceRestApi(CryptoXLibTest):
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

    async def test_listen_key(self):
        response = await self.client.get_spot_listen_key()
        self.assertTrue(self.check_positive_response(response))

        response = await self.client.keep_alive_spot_listen_key(response['response']['listenKey'])
        self.assertTrue(self.check_positive_response(response))

    async def test_get_exchange_info1(self):
        response = await self.client.get_exchange_info()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_exchange_info2(self):
        response = await self.client.get_exchange_info(pairs = [Pair('BTC', 'USDT')])
        self.assertTrue(self.check_positive_response(response))

    async def test_get_exchange_info3(self):
        response = await self.client.get_exchange_info(pairs = [Pair('BTC', 'USDT'), Pair('BNB', 'USDT')])
        self.assertTrue(self.check_positive_response(response))


class BinanceWs(CryptoXLibTest):
    @classmethod
    def initialize(cls) -> None:
        cls.print_logs = True
        cls.log_level = logging.DEBUG

    async def init_test(self):
        self.client = CryptoXLib.create_binance_client(api_key, sec_key)

    #@unittest.expectedFailure
    async def test_candlesticks_subscription(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            CandlestickSubscription(Pair("BTC", "USDT"), enums.Interval.I_1MIN,
                                     callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter, 15.0)

    async def test_partial_detph(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            DepthSubscription(Pair('BTC', 'USDT'), 5, 100, callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_partial_detph2(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            DepthSubscription(Pair('BTC', 'USDT'), 5, callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_detph(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            DepthSubscription(Pair('BTC', 'USDT'), 0, 1000, callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_detph2(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            DepthSubscription(Pair('BTC', 'USDT'), 0, callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter)


if __name__ == '__main__':
    unittest.main()