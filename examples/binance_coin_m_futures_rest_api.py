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

    client = CryptoXLib.create_binance_coin_m_futures_client(api_key, sec_key)

    print("Ping:")
    await client.ping()

    print("Server time:")
    await client.get_time()

    print("Exchange info:")
    await client.get_exchange_info()

    print("Order book:")
    await client.get_orderbook(symbol = 'BTCUSD_PERP', limit = enums.DepthLimit.L_5)

    print("Trades:")
    await client.get_trades(symbol = 'BTCUSD_PERP', limit = 5)

    print("Historical trades:")
    await client.get_historical_trades(symbol = 'BTCUSD_PERP', limit = 5)

    print("Aggregate trades:")
    await client.get_aggregate_trades(symbol = 'BTCUSD_PERP', limit = 5)

    print("Index price candlesticks:")
    await client.get_index_price_candlesticks(pair = Pair('BTC', 'USD'), interval = enums.Interval.I_1MIN)

    print("24hour price ticker:")
    await client.get_24h_price_ticker(pair = Pair('BTC', 'USD'))

    print("Price ticker:")
    await client.get_price_ticker(pair = Pair('BTC', 'USD'))

    print("Best order book ticker:")
    await client.get_orderbook_ticker(pair = Pair('BTC', 'USD'))

    print("Create limit order:")
    try:
        await client.create_order(symbol = 'BTCUSD_PERP', side = enums.OrderSide.BUY, type = enums.OrderType.LIMIT,
                                  quantity = "1",
                                  price = "0",
                                  time_in_force = enums.TimeInForce.GOOD_TILL_CANCELLED,
                                  new_order_response_type = enums.OrderResponseType.FULL)
    except BinanceException as e:
        print(e)

    await client.close()

if __name__ == "__main__":
    async_run(run())
