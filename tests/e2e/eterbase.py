import unittest
import os
import logging
import uuid

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.clients.eterbase import enums
from cryptoxlib.clients.eterbase.exceptions import EterbaseRestException
from cryptoxlib.clients.eterbase.EterbaseWebsocket import OrderbookSubscription

from CryptoXLibTest import CryptoXLibTest, WsMessageCounter

api_key = os.environ['ETERBASEAPIKEY']
sec_key = os.environ['ETERBASESECKEY']
acct_key = os.environ['ETERBASEACCTKEY']


class EterbaseRestApi(CryptoXLibTest):
    @classmethod
    def initialize(cls) -> None:
        cls.print_logs = True
        cls.log_level = logging.DEBUG

    def check_positive_response(self, response):
        return str(response['status_code'])[0] == '2'

    async def get_market_id(self, symbol: str) -> str:
        markets = await self.client.get_markets()
        return next(filter(lambda x: x['symbol'] == symbol, markets['response']))['id']

    async def init_test(self):
        self.client = CryptoXLib.create_eterbase_client(acct_key, api_key, sec_key)

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
        response = await self.client.get_balances()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_token(self):
        response = await self.client.get_token()
        self.assertTrue(self.check_positive_response(response))

    async def test_create_order(self):
        ethusdt_id = await self.get_market_id('ETHUSDT')
        print(f'ETHUSDT: {ethusdt_id}')

        with self.assertRaises(EterbaseRestException) as cm:
            await self.client.create_order(pair_id = ethusdt_id, side = enums.OrderSide.BUY,
                                                      type = enums.OrderType.LIMIT, amount = "100000", price = "1",
                                                      time_in_force = enums.TimeInForce.GOOD_TILL_CANCELLED)
        e = cm.exception

        self.assertEqual(e.status_code, 400)

    async def test_cancel_order(self):
        with self.assertRaises(EterbaseRestException) as cm:
            await self.client.cancel_order(order_id = str(uuid.uuid4()))
        e = cm.exception

        self.assertEqual(e.status_code, 400)


class EterbaseWs(CryptoXLibTest):
    @classmethod
    def initialize(cls) -> None:
        cls.print_logs = True
        cls.log_level = logging.DEBUG

    async def init_test(self):
        self.client = CryptoXLib.create_eterbase_client(acct_key, api_key, sec_key)

    async def clean_test(self):
        await self.client.close()

    async def get_market_id(self, symbol: str) -> str:
        markets = await self.client.get_markets()
        return next(filter(lambda x: x['symbol'] == symbol, markets['response']))['id']

    async def test_order_book_subscription(self):
        ethusdt_id = await self.get_market_id('ETHUSDT')
        print(f'ETHUSDT: {ethusdt_id}')

        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            OrderbookSubscription(market_ids = [ethusdt_id], callbacks = [message_counter.generate_callback(1)]),
        ])

        await self.assertWsMessageCount(message_counter)


if __name__ == '__main__':
    unittest.main()