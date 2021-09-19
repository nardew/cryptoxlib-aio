import logging
import datetime
import os

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.bitpanda.exceptions import BitpandaException
from cryptoxlib.clients.bitpanda.enums import OrderSide, TimeUnit
from cryptoxlib.version_conversions import async_run

LOG = logging.getLogger("cryptoxlib")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

print(f"Available loggers: {[name for name in logging.root.manager.loggerDict]}")


async def order_book_update(response: dict) -> None:
    print(f"Callback order_book_update: [{response}]")

async def run():
    api_key = os.environ['BITPANDAAPIKEY']

    client = CryptoXLib.create_coinmate_client(api_key, "", "")

    print("Trading pairs:")
    await client.get_exchange_info()

    print("Currency pairs:")
    await client.get_currency_pairs()

    print("Ticker:")
    await client.get_ticker(pair = Pair('BTC', 'EUR'))

    await client.close()


if __name__ == "__main__":
    async_run(run())
