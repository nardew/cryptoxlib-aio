import logging
import os

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.clients.bitforex import enums
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.bitforex.exceptions import BitforexException
from cryptoxlib.version_conversions import async_run

LOG = logging.getLogger("cryptoxlib")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

print(f"Available loggers: {[name for name in logging.root.manager.loggerDict]}")


async def run():
    # to retrieve your API/SEC key go to your bitforex account, create the keys and store them in
    # BITFOREXAPIKEY/BITFOREXSECKEY environment variables
    api_key = os.environ['BITFOREXAPIKEY']
    sec_key = os.environ['BITFOREXSECKEY']

    bitforex = CryptoXLib.create_bitforex_client(api_key, sec_key)

    print("Exchange info:")
    await bitforex.get_exchange_info()

    print("Order book:")
    await bitforex.get_order_book(pair = Pair('ETH', 'BTC'), depth = "1")

    print("Ticker:")
    await bitforex.get_ticker(pair = Pair('ETH', 'BTC'))

    print("Single fund:")
    await bitforex.get_single_fund(currency = "NOBS")

    print("Funds:")
    await bitforex.get_funds()

    print("Trades:")
    await bitforex.get_trades(pair = Pair('ETH', 'BTC'), size = "1")

    print("Candlesticks:")
    await bitforex.get_candlesticks(pair = Pair('ETH', 'BTC'), interval = enums.CandlestickInterval.I_1W, size = "5")

    print("Create order:")
    try:
        await bitforex.create_order(Pair("ETH", "BTC"), side = enums.OrderSide.SELL, quantity = "1", price = "1")
    except BitforexException as e:
        print(e)

    print("Create multiple orders:")
    await bitforex.create_multi_order(Pair("ETH", "BTC"),
                                      orders = [("1", "1", enums.OrderSide.SELL), ("2", "1", enums.OrderSide.SELL)])

    print("Cancel order:")
    await bitforex.cancel_order(pair = Pair('ETH', 'BTC'), order_id = "10")

    print("Cancel multiple orders:")
    await bitforex.cancel_multi_order(pair = Pair('ETH', 'BTC'), order_ids = ["10", "20"])

    print("Cancel all orders:")
    await bitforex.cancel_all_orders(pair = Pair('ETH', 'BTC'))

    print("Get order:")
    try:
        await bitforex.get_order(pair = Pair('ETH', 'BTC'), order_id = "1")
    except BitforexException as e:
        print(e)

    print("Get orders:")
    await bitforex.get_orders(pair = Pair('ETH', 'BTC'), order_ids = ["1", "2"])

    print("Find orders:")
    await bitforex.find_order(pair = Pair('ETH', 'BTC'), state = enums.OrderState.PENDING)

    await bitforex.close()

if __name__ == "__main__":
    async_run(run())
