import unittest
import os
import logging

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.clients.hitbtc import enums
from cryptoxlib.clients.hitbtc.HitbtcWebsocket import OrderbookSubscription, TickerSubscription, TradesSubscription, \
    AccountSubscription
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.hitbtc.exceptions import HitbtcRestException

from CryptoXLibTest import CryptoXLibTest, WsMessageCounter

api_key = os.environ['HITBTCAPIKEY']
sec_key = os.environ['HITBTCSECKEY']


class HitbtcRestApi(CryptoXLibTest):
    @classmethod
    def initialize(cls) -> None:
        cls.print_logs = True
        cls.log_level = logging.DEBUG

    def check_positive_response(self, response):
        return str(response['status_code'])[0] == '2'

    async def init_test(self):
        self.client = CryptoXLib.create_hitbtc_client(api_key, sec_key)

    async def clean_test(self):
        await self.client.close()

    async def test_get_currencies(self):
        response = await self.client.get_currencies()
        #for x in sorted(response['response'], key = lambda x: x['id']):
        #    print(x)
        self.assertTrue(self.check_positive_response(response))

    async def test_get_currencies2(self):
        response = await self.client.get_currencies(['BTC', 'ETH'])
        self.assertTrue(self.check_positive_response(response))

    async def test_get_currency(self):
        response = await self.client.get_currency('BTC')
        self.assertTrue(self.check_positive_response(response))

    async def test_get_symbols(self):
        response = await self.client.get_symbols()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_symbols2(self):
        response = await self.client.get_symbols([Pair('ETH', 'BTC'), Pair('XRP', 'BTC')])
        self.assertTrue(self.check_positive_response(response))

    async def test_get_symbol(self):
        response = await self.client.get_symbol(Pair('ETH', 'BTC'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_tickers(self):
        response = await self.client.get_tickers()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_tickers2(self):
        response = await self.client.get_tickers([Pair('ETH', 'BTC'), Pair('XRP', 'BTC')])
        self.assertTrue(self.check_positive_response(response))

    async def test_get_ticker(self):
        response = await self.client.get_ticker(Pair('ETH', 'BTC'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_order_books(self):
        response = await self.client.get_order_books(limit = 1, pairs = [Pair('ETH', 'BTC')])
        self.assertTrue(self.check_positive_response(response))

    async def test_get_order_books2(self):
        response = await self.client.get_order_books(pairs = [Pair('ETH', 'BTC')])
        self.assertTrue(self.check_positive_response(response))

    async def test_get_order_books3(self):
        response = await self.client.get_order_books()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_order_book(self):
        response = await self.client.get_order_book(pair = Pair('ETH', 'BTC'), limit = 1)
        self.assertTrue(self.check_positive_response(response))

    async def test_get_order_book2(self):
        response = await self.client.get_order_book(pair = Pair('ETH', 'BTC'), limit = 1, volume = 100)
        self.assertTrue(self.check_positive_response(response))

    async def test_get_balance(self):
        response = await self.client.get_balance()
        self.assertTrue(self.check_positive_response(response))

    async def test_create_order(self):
        with self.assertRaises(HitbtcRestException) as cm:
            await self.client.create_order(pair = Pair("BTC", "USD"), side = enums.OrderSide.BUY,
                                                      type = enums.OrderType.LIMIT, amount = "100000", price = "1",
                                                      time_in_force = enums.TimeInForce.GOOD_TILL_CANCELLED)
        e = cm.exception

        self.assertEqual(e.status_code, 400)
        self.assertEqual(e.body['error']['code'], 20001)

    async def test_cancel_orders(self):
        response = await self.client.cancel_orders(pair = Pair("BTC", "USD"))
        self.assertTrue(self.check_positive_response(response))

    async def test_cancel_order(self):
        with self.assertRaises(HitbtcRestException) as cm:
            await self.client.cancel_order(client_id = "12345678")
        e = cm.exception

        self.assertEqual(e.status_code, 400)
        self.assertEqual(e.body['error']['code'], 20002)


class HitbtcWs(CryptoXLibTest):
    @classmethod
    def initialize(cls) -> None:
        cls.print_logs = True
        cls.log_level = logging.DEBUG

    async def init_test(self):
        self.client = CryptoXLib.create_hitbtc_client(api_key, sec_key)

    #@unittest.skip
    async def test_order_book_subscription(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            OrderbookSubscription(Pair('BTC', 'USD'), callbacks = [message_counter.generate_callback(2)]),
        ])

        await self.assertWsMessageCount(message_counter)

    #@unittest.skip
    async def test_ticker_subscription(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            TickerSubscription(Pair('BTC', 'USD'), callbacks = [message_counter.generate_callback(2)]),
        ])

        await self.assertWsMessageCount(message_counter)

    #@unittest.skip
    async def test_trades_subscription(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            TradesSubscription(Pair('ETH', 'BTC'), callbacks = [message_counter.generate_callback(1)]),
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_account_subscription(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            AccountSubscription(callbacks = [message_counter.generate_callback(1)]),
        ])

        await self.assertWsMessageCount(message_counter)


if __name__ == '__main__':
    unittest.main()