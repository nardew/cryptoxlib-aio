import logging
import os

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.Pair import Pair
from cryptoxlib.version_conversions import async_run

LOG = logging.getLogger("cryptoxlib")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

print(f"Available loggers: {[name for name in logging.root.manager.loggerDict]}")


async def order_book_update(response: dict) -> None:
    print(f"Callback order_book_update: [{response}]")

async def run():
    api_key = os.environ['HITBTCAPIKEY']
    sec_key = os.environ['HITBTCSECKEY']

    client = CryptoXLib.create_hitbtc_client(api_key, sec_key)

    print("Account balance:")
    await client.get_balance()

    print("Symbols:")
    await client.get_symbols()

    print("Orderbook:")
    await client.get_order_book(pair = Pair("ETH", "BTC"), limit = 2)

    await client.close()


if __name__ == "__main__":
    async_run(run())
