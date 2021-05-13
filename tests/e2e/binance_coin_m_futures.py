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


if __name__ == '__main__':
    unittest.main()