import unittest
import os
import logging

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.clients.btse import enums
from cryptoxlib.clients.btse.exceptions import BtseRestException
from cryptoxlib.clients.btse.BtseWebsocket import OrderbookSubscription, OrderbookL2Subscription, TradeSubscription
from cryptoxlib.Pair import Pair

from CryptoXLibTest import CryptoXLibTest, WsMessageCounter

api_key = os.environ['BTSEAPIKEY']
sec_key = os.environ['BTSESECKEY']


class BtseRestApi(CryptoXLibTest):
    @classmethod
    def initialize(cls) -> None:
        cls.print_logs = True
        cls.log_level = logging.DEBUG

    async def init_test(self):
        self.client = CryptoXLib.create_btse_client(api_key, sec_key)

    async def clean_test(self):
        await self.client.close()

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
                                           amount = "1000", price = "1")
        e = cm.exception

        self.assertEqual(e.status_code, 400)
        self.assertTrue(str(e.body['errorCode']) == '51523')

    async def test_cancel_order(self):
        response = await self.client.cancel_order(pair = Pair('BTC', 'USD'))
        self.assertTrue(self.check_positive_response(response))


class BtseWs(CryptoXLibTest):
    @classmethod
    def initialize(cls) -> None:
        cls.print_logs = True
        cls.log_level = logging.DEBUG

    async def init_test(self):
        self.client = CryptoXLib.create_btse_client(api_key, sec_key)

    async def test_order_book_subscription(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            OrderbookSubscription([Pair('BTSE', 'BTC')], callbacks = [message_counter.generate_callback(2)]),
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_order_book_L2_subscription(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            OrderbookL2Subscription([Pair('BTSE', 'BTC')], depth = 1, callbacks = [message_counter.generate_callback(2)]),
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_trade_subscription(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            TradeSubscription([Pair('BTC', 'USDT')], callbacks = [message_counter.generate_callback(1)]),
        ])

        await self.assertWsMessageCount(message_counter)


if __name__ == '__main__':
    unittest.main()