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

    print("All Open Orders:")
    await client.get_all_open_orders()

    await client.close()

if __name__ == "__main__":
    async_run(run())
