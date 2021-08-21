import logging
import os

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.clients.binance import enums
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.binance.exceptions import BinanceException
from cryptoxlib.version_conversions import async_run

LOG = logging.getLogger("cryptoxlib")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

print(f"Available loggers: {[name for name in logging.root.manager.loggerDict]}")

async def run():
    api_key = os.environ['APIKEY']
    sec_key = os.environ['SECKEY']

    client = CryptoXLib.create_binance_usds_m_futures_client(api_key, sec_key)

    print("Ping:")
    await client.ping()

    print("Server time:")
    await client.get_time()

    print("Exchange info:")
    await client.get_exchange_info()

    print("Order book:")
    await client.get_orderbook(symbol = Pair('BTC', 'USDT'), limit = enums.DepthLimit.L_5)

    print("Trades:")
    await client.get_trades(symbol=Pair('BTC', 'USDT'), limit = 5)

    print("Historical trades:")
    await client.get_historical_trades(symbol=Pair('BTC', 'USDT'), limit = 5)

    print("Aggregate trades:")
    await client.get_aggregate_trades(symbol=Pair('BTC', 'USDT'), limit = 5)

    print("Index price candlesticks:")
    await client.get_index_price_candlesticks(pair = Pair('BTC', 'USDT'), interval = enums.Interval.I_1MIN)

    print("Index info:")
    await client.get_index_info(pair = Pair('DEFI', 'USDT'))

    print("24hour price ticker:")
    await client.get_24h_price_ticker(pair = Pair('BTC', 'USDT'))

    print("Price ticker:")
    await client.get_price_ticker(pair = Pair('BTC', 'USDT'))

    print("Best order book ticker:")
    await client.get_orderbook_ticker(pair = Pair('BTC', 'USDT'))

    print("Create limit order:")
    try:
        await client.create_order(Pair("BTC", "USDT"), side = enums.OrderSide.BUY, type = enums.OrderType.LIMIT,
                                  quantity = "1",
                                  price = "0",
                                  time_in_force = enums.TimeInForce.GOOD_TILL_CANCELLED,
                                  new_order_response_type = enums.OrderResponseType.FULL)
    except BinanceException as e:
        print(e)

    print("Account:")
    await client.get_account(recv_window_ms = 5000)

    print("Account trades:")
    await client.get_account_trades(pair = Pair('BTC', 'USDT'))

    print("All Open Orders:")
    await client.get_all_open_orders()

    await client.close()

if __name__ == "__main__":
    async_run(run())
