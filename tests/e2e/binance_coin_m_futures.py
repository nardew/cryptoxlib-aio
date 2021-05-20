import unittest
import os
import logging

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.clients.binance import enums
from cryptoxlib.clients.binance.BinanceFuturesWebsocket import AggregateTradeSubscription, MarkPriceSubscription, \
    MarkPriceAllSubscription, AllMarketLiquidationOrdersSubscription, AllMarketMiniTickersSubscription, \
    AllMarketTickersSubscription, MiniTickerSubscription, OrderBookTickerSubscription, \
    OrderBookSymbolTickerSubscription, LiquidationOrdersSubscription, BlvtCandlestickSubscription, \
    BlvtSubscription, CompositeIndexSubscription, DepthSubscription, CandlestickSubscription, \
    ContContractCandlestickSubscription, TickerSubscription, AccountSubscription
from cryptoxlib.clients.binance.exceptions import BinanceRestException
from cryptoxlib.Pair import Pair

from CryptoXLibTest import CryptoXLibTest, WsMessageCounter

api_key = os.environ['BINANCEAPIKEY']
sec_key = os.environ['BINANCESECKEY']
test_api_key = os.environ['BINANCEFUTURESTESTAPIKEY']
test_sec_key = os.environ['BINANCEFUTURESTESTSECKEY']


class BinanceCOINMFuturesMarketRestApi(CryptoXLibTest):
    @classmethod
    def initialize(cls) -> None:
        cls.print_logs = True
        cls.log_level = logging.DEBUG

    async def init_test(self):
        self.client = CryptoXLib.create_binance_coin_m_futures_client(api_key, sec_key)

    async def clean_test(self):
        await self.client.close()

    def check_positive_response(self, response):
        return str(response['status_code'])[0] == '2'

    async def test_get_ping(self):
        response = await self.client.ping()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_time(self):
        response = await self.client.get_time()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_exchange_info(self):
        response = await self.client.get_exchange_info()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_order_book(self):
        response = await self.client.get_orderbook(symbol = 'BTCUSD_PERP')
        self.assertTrue(self.check_positive_response(response))

    async def test_get_trades(self):
        response = await self.client.get_trades(symbol = 'BTCUSD_PERP')
        self.assertTrue(self.check_positive_response(response))

    async def test_get_historical_trades(self):
        response = await self.client.get_historical_trades(symbol = 'BTCUSD_PERP')
        self.assertTrue(self.check_positive_response(response))

    async def test_get_aggregate_trades(self):
        response = await self.client.get_aggregate_trades(symbol = 'BTCUSD_PERP')
        self.assertTrue(self.check_positive_response(response))

    async def test_get_candlesticks(self):
        response = await self.client.get_candlesticks(symbol = 'BTCUSD_PERP', interval = enums.Interval.I_1MIN)
        self.assertTrue(self.check_positive_response(response))

    async def test_get_cont_contract_candlesticks(self):
        response = await self.client.get_cont_contract_candlesticks(pair = Pair('BTC', 'USD'),
                                                                    interval = enums.Interval.I_1MIN,
                                                                    contract_type = enums.ContractType.PERPETUAL)
        self.assertTrue(self.check_positive_response(response))

    async def test_get_index_price_candlesticks(self):
        response = await self.client.get_index_price_candlesticks(pair = Pair('BTC', 'USD'), interval = enums.Interval.I_1MIN)
        self.assertTrue(self.check_positive_response(response))

    async def test_get_mark_price_candlesticks(self):
        response = await self.client.get_mark_price_candlesticks(symbol = 'BTCUSD_PERP', interval = enums.Interval.I_1MIN)
        self.assertTrue(self.check_positive_response(response))

    async def test_get_mark_price(self):
        response = await self.client.get_mark_index_price(pair = Pair('BTC', 'USD'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_fund_rate_history(self):
        response = await self.client.get_fund_rate_history(symbol = 'BTCUSD_PERP')
        self.assertTrue(self.check_positive_response(response))

    async def test_get_24h_price_ticker(self):
        response = await self.client.get_24h_price_ticker(pair = Pair('BTC', 'USD'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_price_ticker(self):
        response = await self.client.get_price_ticker(pair = Pair('BTC', 'USD'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_best_orderbook_ticker(self):
        response = await self.client.get_orderbook_ticker(pair = Pair('BTC', 'USD'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_open_interest(self):
        response = await self.client.get_open_interest(symbol = 'BTCUSD_PERP')
        self.assertTrue(self.check_positive_response(response))

    async def test_get_open_interest_hist(self):
        response = await self.client.get_open_interest_hist(pair = Pair('BTC', 'USD'), interval = enums.Interval.I_1D,
                                                            contract_type = enums.ContractType.PERPETUAL)
        self.assertTrue(self.check_positive_response(response))

    async def test_get_top_long_short_account_ratio(self):
        response = await self.client.get_top_long_short_account_ratio(pair = Pair('BTC', 'USD'), interval = enums.Interval.I_1D)
        self.assertTrue(self.check_positive_response(response))

    async def test_get_top_long_short_position_ratio(self):
        response = await self.client.get_top_long_short_position_ratio(pair = Pair('BTC', 'USD'), interval = enums.Interval.I_1D)
        self.assertTrue(self.check_positive_response(response))


class BinanceCOINMFuturesMarketWs(CryptoXLibTest):
    @classmethod
    def initialize(cls) -> None:
        cls.print_logs = True
        cls.log_level = logging.DEBUG

    async def init_test(self):
        self.client = CryptoXLib.create_binance_coin_m_futures_client(api_key, sec_key)

    async def test_aggregate_trade(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            AggregateTradeSubscription(symbol = "BTCUSDT", callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_mark_price(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            MarkPriceSubscription(pair = Pair("BTC", "USDT"), frequency1sec = True, callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_mark_price_all(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            MarkPriceAllSubscription(True, callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_candlestick(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            CandlestickSubscription(pair = Pair("BTC", "USDT"), interval = enums.Interval.I_1MIN, callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_cont_contract_candlestick(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            ContContractCandlestickSubscription(Pair("BTC", "USDT"), enums.Interval.I_1MIN, enums.ContractType.PERPETUAL,
                                                callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_all_market_mini_ticker(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            AllMarketMiniTickersSubscription(callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_mini_ticker(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            MiniTickerSubscription(Pair('BTC', 'USDT'), callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_all_market_ticker(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            AllMarketTickersSubscription(callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_ticker(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            TickerSubscription(Pair('BTC', 'USDT'), callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_best_orderbook_ticker(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            OrderBookTickerSubscription(callbacks = [message_counter.generate_callback(10)])
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_best_orderbook_symbol_ticker(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            OrderBookSymbolTickerSubscription(Pair('BTC', 'USDT'), callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter)

    # fails since normally there are no liquidation orders
    async def liquidation_orders(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            LiquidationOrdersSubscription(Pair('BTC', 'USDT'), callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_all_liquidation_orders(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            AllMarketLiquidationOrdersSubscription(callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_partial_detph(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            DepthSubscription(pair = Pair('BTC', 'USDT'), level =  5, frequency = 100, callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_partial_detph2(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            DepthSubscription(pair = Pair('BTC', 'USDT'), level = 5, callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_detph(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            DepthSubscription(pair = Pair('BTC', 'USDT'), level = 0, frequency = 100, callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_detph2(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            DepthSubscription(pair = Pair('BTC', 'USDT'), level = 0, callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_blvt(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            BlvtSubscription(Pair('BTC', 'UP'), callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter)

    # typically no data are received
    async def blvt_candlesticks(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            BlvtCandlestickSubscription(Pair('BTC', 'UP'), enums.Interval.I_1MIN,
                                        callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter, timeout = 60)

    async def test_composite_index(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            CompositeIndexSubscription(Pair('DEFI', 'USDT'),
                                        callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter)


if __name__ == '__main__':
    unittest.main()