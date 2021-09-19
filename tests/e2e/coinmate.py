import unittest
import os
import logging
import datetime

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.coinmate.exceptions import CoinmateRestException
from cryptoxlib.clients.coinmate.CoinmateWebsocket import OrderbookSubscription
from cryptoxlib.clients.coinmate import enums

from CryptoXLibTest import CryptoXLibTest, WsMessageCounter

api_key = os.environ['COINMATEAPIKEY']
sec_key = os.environ['COINMATESECKEY']
user_id = os.environ['COINMATEUSERID']


class CoinmateRestApi(CryptoXLibTest):
    @classmethod
    def initialize(cls) -> None:
        cls.print_logs = True
        cls.log_level = logging.DEBUG

    def check_positive_response(self, response):
        return str(response['status_code'])[0] == '2'

    async def init_test(self):
        self.client = CryptoXLib.create_coinmate_client(user_id, api_key, sec_key)

    async def clean_test(self):
        await self.client.close()

    async def test_get_pairs(self):
        response = await self.client.get_exchange_info()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_order_book(self):
        response = await self.client.get_order_book(pair = Pair("BTC", "EUR"))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_order_book2(self):
        response = await self.client.get_order_book(pair = Pair("BTC", "EUR"), group = True)
        self.assertTrue(self.check_positive_response(response))

    async def test_get_ticker(self):
        response = await self.client.get_ticker(pair = Pair("BTC", "EUR"))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_currency_pairs(self):
        response = await self.client.get_currency_pairs()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_transactions(self):
        response = await self.client.get_transactions(minutes_history = 10)
        self.assertTrue(self.check_positive_response(response))

    async def test_get_transactions2(self):
        response = await self.client.get_transactions(minutes_history = 10, currency_pair = Pair("BTC", "EUR"))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_balances(self):
        response = await self.client.get_balances()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_fees(self):
        response = await self.client.get_fees()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_fees2(self):
        response = await self.client.get_fees(pair = Pair('BTC', 'EUR'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_transaction_history(self):
        response = await self.client.get_transaction_history()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_trade_history(self):
        response = await self.client.get_trade_history()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_trade_history2(self):
        response = await self.client.get_trade_history(pair = Pair('BTC', 'EUR'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_transfer(self):
        with self.assertRaises(CoinmateRestException) as cm:
            await self.client.get_transfer(transaction_id = "0")
        e = cm.exception

        self.assertEqual(e.status_code, 200)
        self.assertTrue(e.body['errorMessage'] == 'No transfer with given ID')

    async def test_get_transfer_history(self):
        response = await self.client.get_transfer_history()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_transfer_history2(self):
        response = await self.client.get_transfer_history(currency = 'EUR')
        self.assertTrue(self.check_positive_response(response))

    async def test_get_order_history(self):
        response = await self.client.get_order_history(pair = Pair('BTC', 'EUR'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_open_orders(self):
        response = await self.client.get_open_orders()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_open_orders2(self):
        response = await self.client.get_open_orders(pair = Pair('BTC', 'EUR'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_order(self):
        with self.assertRaises(CoinmateRestException) as cm:
            await self.client.get_order(order_id = "0")
        e = cm.exception

        self.assertEqual(e.status_code, 200)
        self.assertTrue(e.body['errorMessage'] == 'No order with given ID')

    async def test_get_order2(self):
        response = await self.client.get_order(client_id = "0")
        self.assertTrue(self.check_positive_response(response))

    async def test_cancel_order(self):
        response = await self.client.cancel_order(order_id = "0")
        self.assertTrue(self.check_positive_response(response))

    async def test_cancel_all_orders(self):
        response = await self.client.cancel_all_orders()
        self.assertTrue(self.check_positive_response(response))

    async def test_cancel_all_orders2(self):
        response = await self.client.cancel_all_orders(pair = Pair('BTC', 'EUR'))
        self.assertTrue(self.check_positive_response(response))

    async def test_create_order(self):
        with self.assertRaises(CoinmateRestException) as cm:
            await self.client.create_order(type = enums.OrderType.MARKET, side = enums.OrderSide.BUY, amount = "100",
                                           pair = Pair('BTC', 'EUR'))
        e = cm.exception

        self.assertEqual(e.status_code, 200)

    async def test_create_order2(self):
        with self.assertRaises(CoinmateRestException) as cm:
            await self.client.create_order(type = enums.OrderType.MARKET, side = enums.OrderSide.SELL, amount = "100",
                                           pair = Pair('BTC', 'EUR'))
        e = cm.exception

        self.assertEqual(e.status_code, 200)

    async def test_create_order3(self):
        with self.assertRaises(CoinmateRestException) as cm:
            await self.client.create_order(type = enums.OrderType.LIMIT, side = enums.OrderSide.BUY, price = "1",
                                           amount = "100",
                                           pair = Pair('BTC', 'EUR'))
        e = cm.exception

        self.assertEqual(e.status_code, 200)

    async def test_create_order4(self):
        with self.assertRaises(CoinmateRestException) as cm:
            await self.client.create_order(type = enums.OrderType.LIMIT, side = enums.OrderSide.SELL, price = "1000000",
                                           amount = "0.001",
                                           pair = Pair('BTC', 'EUR'))
        e = cm.exception

        self.assertEqual(e.status_code, 200)


class CoinmateWs(CryptoXLibTest):
    @classmethod
    def initialize(cls) -> None:
        cls.print_logs = True
        cls.log_level = logging.DEBUG

    async def init_test(self):
        self.client = CryptoXLib.create_coinmate_client(user_id, api_key, sec_key)

    async def test_order_book_subscription(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            OrderbookSubscription(Pair("BTC", "EUR"), callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter)


if __name__ == '__main__':
    unittest.main()