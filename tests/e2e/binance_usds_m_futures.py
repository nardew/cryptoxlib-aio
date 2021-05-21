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


class BinanceUSDSMFuturesMarketRestApi(CryptoXLibTest):
    @classmethod
    def initialize(cls) -> None:
        cls.print_logs = True
        cls.log_level = logging.DEBUG

    async def init_test(self):
        self.client = CryptoXLib.create_binance_usds_m_futures_client(api_key, sec_key)

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
        response = await self.client.get_orderbook(symbol = Pair('BTC', 'USDT'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_trades(self):
        response = await self.client.get_trades(symbol = Pair('BTC', 'USDT'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_historical_trades(self):
        response = await self.client.get_historical_trades(symbol = Pair('BTC', 'USDT'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_aggregate_trades(self):
        response = await self.client.get_aggregate_trades(symbol = Pair('BTC', 'USDT'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_candlesticks(self):
        response = await self.client.get_candlesticks(symbol = Pair('BTC', 'USDT'), interval = enums.Interval.I_1MIN)
        self.assertTrue(self.check_positive_response(response))

    async def test_get_cont_contract_candlesticks(self):
        response = await self.client.get_cont_contract_candlesticks(pair = Pair('BTC', 'USDT'),
                                                                    interval = enums.Interval.I_1MIN,
                                                                    contract_type = enums.ContractType.PERPETUAL)
        self.assertTrue(self.check_positive_response(response))

    async def test_get_index_price_candlesticks(self):
        response = await self.client.get_index_price_candlesticks(pair = Pair('BTC', 'USDT'), interval = enums.Interval.I_1MIN)
        self.assertTrue(self.check_positive_response(response))

    async def test_get_mark_price_candlesticks(self):
        response = await self.client.get_mark_price_candlesticks(symbol = Pair('BTC', 'USDT'), interval = enums.Interval.I_1MIN)
        self.assertTrue(self.check_positive_response(response))

    async def test_get_mark_price(self):
        response = await self.client.get_mark_price(pair = Pair('BTC', 'USDT'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_fund_rate_history(self):
        response = await self.client.get_fund_rate_history(pair = Pair('BTC', 'USDT'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_24h_price_ticker(self):
        response = await self.client.get_24h_price_ticker(pair = Pair('BTC', 'USDT'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_price_ticker(self):
        response = await self.client.get_price_ticker(pair = Pair('BTC', 'USDT'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_best_orderbook_ticker(self):
        response = await self.client.get_orderbook_ticker(pair = Pair('BTC', 'USDT'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_open_interest(self):
        response = await self.client.get_open_interest(symbol = Pair('BTC', 'USDT'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_open_interest_hist(self):
        response = await self.client.get_open_interest_hist(pair = Pair('BTC', 'USDT'), interval = enums.Interval.I_1D)
        self.assertTrue(self.check_positive_response(response))

    async def test_get_top_long_short_account_ratio(self):
        response = await self.client.get_top_long_short_account_ratio(pair = Pair('BTC', 'USDT'), interval = enums.Interval.I_1D)
        self.assertTrue(self.check_positive_response(response))

    async def test_get_top_long_short_position_ratio(self):
        response = await self.client.get_top_long_short_position_ratio(pair = Pair('BTC', 'UP'), interval = enums.Interval.I_1D)
        self.assertTrue(self.check_positive_response(response))

    async def test_get_global_long_short_account_ratio(self):
        response = await self.client.get_global_long_short_account_ratio(pair = Pair('BTC', 'USDT'), interval = enums.Interval.I_1D)
        self.assertTrue(self.check_positive_response(response))

    async def test_get_taker_long_short_ratio(self):
        response = await self.client.get_taker_long_short_ratio(pair = Pair('BTC', 'USDT'), interval = enums.Interval.I_1D)
        self.assertTrue(self.check_positive_response(response))

    async def test_get_blvt_candlesticks(self):
        response = await self.client.get_blvt_candlesticks(pair = Pair('BTC', 'UP'), interval = enums.Interval.I_1D)
        self.assertTrue(self.check_positive_response(response))

    async def test_get_index_info(self):
        response = await self.client.get_index_info(pair = Pair('DEFI', 'USDT'))
        self.assertTrue(self.check_positive_response(response))

    async def test_listen_key(self):
        response = await self.client.get_listen_key()
        self.assertTrue(self.check_positive_response(response))

        response = await self.client.keep_alive_listen_key(response['response']['listenKey'])
        self.assertTrue(self.check_positive_response(response))


class BinanceUSDSMFuturesAccountRestApi(CryptoXLibTest):
    @classmethod
    def initialize(cls) -> None:
        cls.print_logs = True
        cls.log_level = logging.DEBUG

    async def init_test(self):
        self.client = CryptoXLib.create_binance_usds_m_futures_testnet_client(test_api_key, test_sec_key)

    async def clean_test(self):
        await self.client.close()

    def check_positive_response(self, response):
        return str(response['status_code'])[0] == '2'

    def check_error_code(self, e: BinanceRestException, status: str, code: str):
        return str(e.status_code) == status and str(e.body['code']) == code

    async def test_get_ping(self):
        response = await self.client.ping()
        self.assertTrue(self.check_positive_response(response))

    async def test_change_position_type(self):
        # make sure some position exists in order for the change of position to fail
        await self.client.create_order(symbol = Pair('XRP', 'USDT'), side = enums.OrderSide.BUY,
                                       type = enums.OrderType.MARKET, quantity = '10')

        with self.assertRaises(BinanceRestException) as cm:
            current_type = await self.client.get_position_type()
            response = await self.client.change_position_type(not current_type['response']['dualSidePosition'])
            self.assertTrue(self.check_positive_response(response))
        e = cm.exception

        self.assertTrue(self.check_error_code(e, '400', '-4068'))

    async def test_get_position_type(self):
        response = await self.client.get_position_type()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_all_orders(self):
        response = await self.client.get_all_orders(pair = Pair('BTC', 'USDT'))
        self.assertTrue(self.check_positive_response(response))

    # market order
    async def test_create_order1(self):
        current_position_type = await self.client.get_position_type()
        if current_position_type['response']['dualSidePosition']:
            await self.client.change_position_type(False)

        response = await self.client.create_order(symbol = Pair('BTC', 'USDT'), side = enums.OrderSide.BUY,
                                                  type = enums.OrderType.MARKET, quantity = '0.001')
        self.assertTrue(self.check_positive_response(response))

    # limit order
    async def test_create_order2(self):
        current_position_type = await self.client.get_position_type()
        if current_position_type['response']['dualSidePosition']:
            await self.client.change_position_type(False)

        response = await self.client.create_order(symbol = Pair('BTC', 'USDT'), side = enums.OrderSide.BUY,
                                                  type = enums.OrderType.LIMIT, quantity = '0.1', price = '2000',
                                                  time_in_force = enums.TimeInForce.GOOD_TILL_CANCELLED)
        self.assertTrue(self.check_positive_response(response))

    async def test_get_order(self):
        with self.assertRaises(BinanceRestException) as cm:
            await self.client.get_order(symbol = Pair('BTC', 'USDT'), order_id = 1)
        e = cm.exception

        self.assertTrue(self.check_error_code(e, '400', '-2013'))

    async def test_cancel_order(self):
        with self.assertRaises(BinanceRestException) as cm:
            await self.client.cancel_order(symbol = Pair('BTC', 'USDT'), order_id = 1)
        e = cm.exception

        self.assertTrue(self.check_error_code(e, '400', '-2011'))

    async def test_cancel_all_orders(self):
        response = await self.client.cancel_all_orders(symbol = Pair('BTC', 'USDT'))
        self.assertTrue(self.check_positive_response(response))

    @unittest.expectedFailure
    # not supported for testnet
    async def test_auto_cancel_orders(self):
        response = await self.client.auto_cancel_orders(symbol = Pair('BTC', 'USDT'), countdown_time_ms = 0)
        self.assertTrue(self.check_positive_response(response))

    async def test_get_open_order(self):
        with self.assertRaises(BinanceRestException) as cm:
            await self.client.get_open_order(symbol = Pair('BTC', 'USDT'), order_id = 1)
        e = cm.exception

        self.assertTrue(self.check_error_code(e, '400', '-2013'))

    async def test_get_all_open_orders(self):
        response = await self.client.get_all_open_orders(pair = Pair('BTC', 'USDT'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_balance(self):
        response = await self.client.get_balance()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_account(self):
        response = await self.client.get_account()
        self.assertTrue(self.check_positive_response(response))

    async def test_change_init_leverage(self):
        response = await self.client.change_init_leverage(symbol = Pair('BTC', 'USDT'), leverage = 1)
        self.assertTrue(self.check_positive_response(response))

    async def test_change_margin_type(self):
        position = await self.client.get_position(pair = Pair('ETH', 'USDT'))
        margin_type = position['response'][0]['marginType']
        if margin_type == 'cross':
            new_margin_type = enums.MarginType.ISOLATED
        else:
            new_margin_type = enums.MarginType.CROSSED

        response = await self.client.change_margin_type(symbol = Pair('ETH', 'USDT'), margin_type = new_margin_type)
        self.assertTrue(self.check_positive_response(response))

    async def test_update_isolated_position_margin(self):
        position = await self.client.get_position(pair = Pair('BNB', 'USDT'))
        margin_type = position['response'][0]['marginType']
        if margin_type == 'cross':
            await self.client.change_margin_type(symbol = Pair('BNB', 'USDT'), margin_type = enums.MarginType.ISOLATED)

        await self.client.create_order(symbol = Pair('BNB', 'USDT'), side = enums.OrderSide.BUY,
                                                  type = enums.OrderType.MARKET, quantity = '0.1')

        response = await self.client.update_isolated_position_margin(symbol = Pair('BNB', 'USDT'), quantity = '0.001',
                                                                     type = 2)
        self.assertTrue(self.check_positive_response(response))

    async def test_get_position_margin_change_history(self):
        response = await self.client.get_position_margin_change_history(symbol = Pair('BTC', 'USDT'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_position(self):
        response = await self.client.get_position()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_position2(self):
        response = await self.client.get_position(pair = Pair('BTC', 'USDT'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_account_trades(self):
        response = await self.client.get_account_trades(pair = Pair('BTC', 'USDT'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_income_history(self):
        response = await self.client.get_income_history(symbol = Pair('BTC', 'USDT'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_notional_and_leverage_brackets(self):
        response = await self.client.get_notional_and_leverage_brackets(pair = Pair('BTC', 'USDT'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_adl_quantile(self):
        response = await self.client.get_adl_quantile(symbol = Pair('BTC', 'USDT'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_force_orders(self):
        response = await self.client.get_force_orders(symbol = Pair('BTC', 'USDT'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_api_trading_status(self):
        response = await self.client.get_api_trading_status(pair = Pair('BTC', 'USDT'))
        self.assertTrue(self.check_positive_response(response))

    async def test_get_commission_rate(self):
        response = await self.client.get_commission_rate(symbol = Pair('BTC', 'USDT'))
        self.assertTrue(self.check_positive_response(response))


class BinanceUSDSMFuturesMarketWs(CryptoXLibTest):
    @classmethod
    def initialize(cls) -> None:
        cls.print_logs = True
        cls.log_level = logging.DEBUG

    async def init_test(self):
        self.client = CryptoXLib.create_binance_usds_m_futures_client(api_key, sec_key)

    async def test_aggregate_trade(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            AggregateTradeSubscription(Pair("BTC", "USDT"), callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_mark_price(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            MarkPriceSubscription(symbol = Pair("BTC", "USDT"), frequency1sec = True, callbacks = [message_counter.generate_callback(1)])
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
            CandlestickSubscription(symbol = Pair("BTC", "USDT"), interval = enums.Interval.I_1MIN, callbacks = [message_counter.generate_callback(1)])
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
            DepthSubscription(symbol = Pair('BTC', 'USDT'), level =  5, frequency = 100, callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_partial_detph2(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            DepthSubscription(symbol = Pair('BTC', 'USDT'), level = 5, callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_detph(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            DepthSubscription(symbol = Pair('BTC', 'USDT'), level = 0, frequency = 100, callbacks = [message_counter.generate_callback(1)])
        ])

        await self.assertWsMessageCount(message_counter)

    async def test_detph2(self):
        message_counter = WsMessageCounter()
        self.client.compose_subscriptions([
            DepthSubscription(symbol = Pair('BTC', 'USDT'), level = 0, callbacks = [message_counter.generate_callback(1)])
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