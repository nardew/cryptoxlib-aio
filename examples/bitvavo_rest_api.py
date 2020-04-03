import asyncio
import logging
import os

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.bitvavo import enums
from cryptoxlib.clients.bitvavo.exceptions import BitvavoException

LOG = logging.getLogger("cryptoxlib")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

print(f"Available loggers: {[name for name in logging.root.manager.loggerDict]}")


async def order_book_update(response: dict) -> None:
    print(f"Callback order_book_update: [{response}]")

async def run():
    api_key = os.environ['BITVAVOAPIKEY']
    sec_key = os.environ['BITVAVOSECKEY']

    client = CryptoXLib.create_bitvavo_client(api_key, sec_key)

    print("Time:")
    await client.get_time()

    print("Exchange info:")
    await client.get_exchange_info()

    print("Assets:")
    await client.get_assets()

    print("Open orders:")
    await client.get_open_orders()

    print("Create order:")
    try:
        await client.create_order(pair = Pair("BTC", "EUR"), side = enums.OrderSide.BUY, type = enums.OrderType.LIMIT,
                                  amount = "10000", price = "1")
    except BitvavoException as e:
        print(e)

    print("Cancel order:")
    try:
        await client.cancel_order(pair = Pair("BTC", "EUR"), order_id = "1")
    except BitvavoException as e:
        print(e)

    print("Balance:")
    await client.get_balance()

    await client.close()


if __name__ == "__main__":
    asyncio.run(run())
