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

    client = CryptoXLib.create_binance_client(api_key, sec_key)

    print("Ping:")
    await client.ping()

    print("Server time:")
    await client.get_time()

    print("Exchange info:")
    await client.get_exchange_info()

    print("Order book:")
    await client.get_orderbook(pair = Pair('ETH', 'BTC'), limit = enums.DepthLimit.L_5)

    print("Trades:")
    await client.get_trades(pair=Pair('ETH', 'BTC'), limit = 5)

    print("Historical trades:")
    await client.get_historical_trades(pair=Pair('ETH', 'BTC'), limit = 5)

    print("Aggregate trades:")
    await client.get_aggregate_trades(pair=Pair('ETH', 'BTC'), limit = 5)

    print("Candlesticks:")
    await client.get_candlesticks(pair=Pair('ETH', 'BTC'), interval = enums.Interval.I_1D, limit=5)

    print("Average price:")
    await client.get_average_price(pair = Pair('ETH', 'BTC'))

    print("24hour price ticker:")
    await client.get_24h_price_ticker(pair = Pair('ETH', 'BTC'))

    print("Price ticker:")
    await client.get_price_ticker(pair = Pair('ETH', 'BTC'))

    print("Best order book ticker:")
    await client.get_orderbook_ticker(pair = Pair('ETH', 'BTC'))

    print("Create test market order:")
    await client.create_test_order(Pair("ETH", "BTC"), side = enums.OrderSide.BUY, type = enums.OrderType.MARKET,
                              quantity = "1",
                              new_order_response_type = enums.OrderResponseType.FULL)

    print("Create limit order:")
    try:
        await client.create_order(Pair("ETH", "BTC"), side = enums.OrderSide.BUY, type = enums.OrderType.LIMIT,
                                  quantity = "1",
                                  price = "0",
                                  time_in_force = enums.TimeInForce.GOOD_TILL_CANCELLED,
                                  new_order_response_type = enums.OrderResponseType.FULL)
    except BinanceException as e:
        print(e)

    print("Cancel order:")
    try:
        await client.cancel_order(pair = Pair('ETH', 'BTC'), order_id = "1")
    except BinanceException as e:
        print(e)

    print("Get order:")
    try:
        await client.get_order(pair = Pair('ETH', 'BTC'), order_id = 1)
    except BinanceException as e:
        print(e)

    print("Get open orders:")
    await client.get_open_orders(pair = Pair('ETH', 'BTC'))

    print("Get all orders:")
    await client.get_all_orders(pair = Pair('ETH', 'BTC'))

    print("Create OCO order:")
    try:
        await client.create_oco_order(Pair("ETH", "BTC"), side = enums.OrderSide.BUY,
                                  quantity = "1",
                                  price = "0",
                                  stop_price = "0",
                                  new_order_response_type = enums.OrderResponseType.FULL)
    except BinanceException as e:
        print(e)

    print("Cancel OCO order:")
    try:
        await client.cancel_oco_order(pair = Pair('ETH', 'BTC'), order_list_id = "1")
    except BinanceException as e:
        print(e)

    print("Get OCO order:")
    try:
        await client.get_oco_order(order_list_id = 1)
    except BinanceException as e:
        print(e)

    print("Get open OCO orders:")
    await client.get_open_oco_orders()

    print("Get all OCO orders:")
    await client.get_all_oco_orders()

    print("Account:")
    await client.get_account(recv_window_ms = 5000)

    print("Account trades:")
    await client.get_account_trades(pair = Pair('ETH', 'BTC'))

    await client.close()

if __name__ == "__main__":
    async_run(run())
