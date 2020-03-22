import asyncio
import logging
import os
import json

from cryptolib.CryptoLib import CryptoLib
from cryptolib.Pair import Pair
from cryptolib.clients.bibox import enums
from cryptolib.clients.bibox.exceptions import BiboxException

LOG = logging.getLogger("cryptolib")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

print(f"Available loggers: {[name for name in logging.root.manager.loggerDict]}")


async def run():
    api_key = os.environ['BIBOXAPIKEY']
    sec_key = os.environ['BIBOXSECKEY']

    bibox = CryptoLib.create_bibox_client(api_key, sec_key)

    print("Ping:")
    await bibox.get_ping()

    print("Pair list:")
    await bibox.get_pairs()

    print("Exchange info:")
    await bibox.get_exchange_info()

    print("User assets:")
    await bibox.get_spot_assets(full = True)

    print("Create order:")
    try:
        await bibox.create_order(pair = Pair('ETH', 'BTC'), order_type = enums.OrderType.LIMIT,
                                 order_side = enums.OrderSide.BUY, price = "1", quantity = "1")
    except BiboxException as e:
        print(e)

    print("Cancel order:")
    await bibox.cancel_order(order_id = "1234567890")

    await bibox.close()

if __name__ == "__main__":
    asyncio.run(run())
