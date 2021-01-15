import unittest
import os
import logging
import datetime

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.clients.bitpanda import enums
from cryptoxlib.clients.bitpanda.BitpandaWebsocket import PricesSubscription, AccountSubscription, OrderbookSubscription, \
    CandlesticksSubscription, CandlesticksSubscriptionParams, MarketTickerSubscription
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.bitpanda.exceptions import BitpandaRestException

from CryptoXLibTest import CryptoXLibTest, WsMessageCounter

api_key = os.environ['BITPANDAAPIKEY']


class BitpandaRestApi(CryptoXLibTest):
    @classmethod
    def initialize(cls) -> None:
        cls.print_logs = True
        cls.log_level = logging.DEBUG

    def check_positive_response(self, response):
        return str(response['status_code'])[0] == '2'

    async def init_test(self):
        self.client = CryptoXLib.create_bitpanda_client(api_key)

    async def clean_test(self):
        await self.client.close()

    async def test_get_time(self):
        response = await self.client.get_time()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_account_balances(self):
        response = await self.client.get_account_balances()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_account_orders(self):
        response = await self.client.get_account_orders()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_account_order(self):
        with self.assertRaises(BitpandaRestException) as cm:
            await self.client.get_account_order("1")
        e = cm.exception

        self.assertEqual(e.status_code, 400)

    async def test_create_market_order(self):
        with self.assertRaises(BitpandaRestException) as cm:
            await self.client.create_market_order(Pair("BTC", "EUR"), enums.OrderSide.BUY, "100000")
        e = cm.exception

        self.assertEqual(e.status_code, 422)

    async def test_create_limit_order(self):
        with self.assertRaises(BitpandaRestException) as cm:
            await self.client.create_limit_order(Pair("BTC", "EUR"), enums.OrderSide.BUY, "10000", "1")
        e = cm.exception

        self.assertEqual(e.status_code, 422)

    async def test_create_stop_limit_order(self):
        with self.assertRaises(BitpandaRestException) as cm:
            await self.client.create_stop_limit_order(Pair("BTC", "EUR"), enums.OrderSide.BUY, "10000", "1", "1")
        e = cm.exception

        self.assertEqual(e.status_code, 422)

    async def test_get_account_order_trades(self):
        with self.assertRaises(BitpandaRestException) as cm:
            await self.client.get_account_order_trades("1")
        e = cm.exception

        self.assertEqual(e.status_code, 400)

    async def test_get_account_trades(self):
        response = await self.client.get_account_trades()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_account_trade(self):
        with self.assertRaises(BitpandaRestException) as cm:
            await self.client.get_account_trade("1")
        e = cm.exception

        self.assertEqual(e.status_code, 400)

    async def test_get_account_trading_volume(self):
        response = await self.client.get_account_trading_volume()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_currencies(self):
        response = await self.client.get_currencies()
        self.assertTrue(self.check_positive_response(response))

    async def test_find_order(self):
        response = await self.client.get_candlesticks(Pair("BTC", "EUR"), enums.TimeUnit.DAYS, "1",
                                                      datetime.datetime.now() - datetime.timedelta(days = 7),
                                                      datetime.datetime.now())
        self.assertTrue(self.check_positive_response(response))

    async def test_get_account_fees(self):
        response = await self.client.get_account_fees()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_instruments(self):
        response = await self.client.get_instruments()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_order_book(self):
        response = await self.client.get_order_book(Pair("BTC", "EUR"))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_fee_groups(self):
        response = await self.client.get_fee_groups()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_order_book2(self):
        response = await self.client.get_order_book(Pair("BTC", "EUR"), level = "3", depth = "1")
        self.assertTrue(self.check_positive_response(response))

    async def test_get_market_tickers(self):
        response = await self.client.get_market_tickers()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_market_ticker(self):
        response = await self.client.get_market_ticker(Pair('ETH', 'EUR'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_price_ticks(self):
        response = await self.client.get_price_tick(Pair('ETH', 'EUR'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_price_ticks2(self):
        response = await self.client.get_price_tick(Pair('ETH', 'EUR'),
                                                    from_timestamp = datetime.datetime.now() - datetime.timedelta(hours = 2),
                                                    to_timestamp = datetime.datetime.now())
        self.assertTrue(self.check_positive_response(response))

    async def test_create_deposit_crypto_address(self):
        with self.assertRaises(BitpandaRestException) as cm:
            await self.client.create_deposit_crypto_address("ABC")
        e = cm.exception

        self.assertEqual(e.status_code, 404)
        self.assertTrue(e.body['error'] == 'CURRENCY_NOT_FOUND')

    async def test_get_deposit_crypto_address(self):
        response = await self.client.get_deposit_crypto_address("BTC")
        self.assertTrue(self.check_positive_response(response))

    async def test_get_fiat_deposit_info(self):
        response = await self.client.get_fiat_deposit_info()
        self.assertTrue(self.check_positive_response(response))

    async def test_withdraw_crypto(self):
        with self.assertRaises(BitpandaRestException) as cm:
            await self.client.withdraw_crypto('ABC', '1.0', 'ABC')
        e = cm.exception

        self.assertEqual(e.status_code, 404)
        self.assertTrue(e.body['error'] == 'CURRENCY_NOT_FOUND')

    async def test_delete_auto_cancel_all_orders(self):
        response = await self.client.delete_auto_cancel_all_orders()
        self.assertTrue(self.check_positive_response(response))

    @unittest.skip
    # SERVICE_UNAVAILABLE
    async def test_withdraw_fiat(self):
        with self.assertRaises(BitpandaRestException) as cm:
            await self.client.withdraw_fiat('ABC', '1.0', 'ABC')
        e = cm.exception

        self.assertEqual(e.status_code, 404)

    async def test_get_deposits(self):
        response = await self.client.get_deposits()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_deposits2(self):
        response = await self.client.get_deposits(currency = 'CHF')
        self.assertTrue(self.check_positive_response(response))

    async def test_get_bitpanda_deposits(self):
        response = await self.client.get_bitpanda_deposits()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_bitpanda_deposits2(self):
        response = await self.client.get_bitpanda_deposits(currency = 'CHF')
        self.assertTrue(self.check_positive_response(response))

    async def test_get_withdrawals(self):
        response = await self.client.get_withdrawals()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_withdrawals2(self):
        response = await self.client.get_withdrawals(currency = 'CHF')
        self.assertTrue(self.check_positive_response(response))

    async def test_get_bitpanda_withdrawals(self):
        response = await self.client.get_bitpanda_withdrawals()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_bitpanda_withdrawals2(self):
        response = await self.client.get_bitpanda_withdrawals(currency = 'CHF')
        self.assertTrue(self.check_positive_response(response))

    @unittest.skip
    # updates account settings
    async def test_toggle_best_fee_collection(self):
        response = await self.client.toggle_best_fee_collection(True)
        self.assertTrue(self.check_positive_response(response))

    async def test_delete_account_order(self):
        with self.assertRaises(BitpandaRestException) as cm:
            await self.client.delete_account_order(order_id = "1")
        e = cm.exception

        self.assertEqual(e.status_code, 404)

    async def test_delete_account_order2(self):
        with self.assertRaises(BitpandaRestException) as cm:
            await self.client.delete_account_order(client_id = "1")
        e = cm.exception

        self.assertEqual(e.status_code, 404)

    async def test_order_update_order_id(self):
        with self.assertRaises(BitpandaRestException) as cm:
            await self.client.update_order(amount = "10", order_id = "1")
        e = cm.exception

        self.assertEqual(e.status_code, 404)

    async def test_order_update_client_id(self):
        with self.assertRaises(BitpandaRestException) as cm:
            await self.client.update_order(amount = "10", client_id = "1")
        e = cm.exception

        self.assertEqual(e.status_code, 404)


class BitpandaWs(CryptoXLibTest):
    @classmethod
    def initialize(cls) -> None:
        cls.print_logs = True
        cls.log_level = logging.DEBUG

    async def init_test(self):
        self.client = CryptoXLib.create_bitpanda_client(api_key)

    async def test_price_subscription(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            PricesSubscription([Pair("BTC", "EUR")], callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_account_subscription(self):
        message_counter = WsMessageCounter()

        self.client.compose_subscriptions([
            AccountSubscription(callbacks = [message_counter.generate_callback(3)])
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_order_book_subscription(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            OrderbookSubscription([Pair("BTC", "EUR")], "1", [message_counter.generate_callback(1)]),
        ])

        await self.assertWsMessageCount(message_counter)

    @unittest.skip
    async def test_candlesticks_subscription(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            CandlesticksSubscription([CandlesticksSubscriptionParams(Pair("BTC", "EUR"), enums.TimeUnit.MINUTES, 1)],
                                     callbacks = [message_counter.generate_callback(1)]),
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_market_ticker_subscription(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            MarketTickerSubscription([Pair("BTC", "EUR")], callbacks = [message_counter.generate_callback(2)])
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_multiple_subscription(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            MarketTickerSubscription([Pair("BTC", "EUR")], callbacks = [message_counter.generate_callback(2, name = "MarketTicker")]),
            OrderbookSubscription([Pair("BTC", "EUR")], "1", callbacks = [message_counter.generate_callback(1, name = "Orderbook")])
        ])

        await self.assertWsMessageCount(message_counter)


if __name__ == '__main__':
    unittest.main()