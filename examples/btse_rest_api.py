import logging
import os

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.Pair import Pair
from cryptoxlib.version_conversions import async_run

LOG = logging.getLogger("cryptoxlib")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

print(f"Available loggers: {[name for name in logging.root.manager.loggerDict]}")


async def run():
    api_key = os.environ['BTSEAPIKEY']
    sec_key = os.environ['BTSESECKEY']

    client = CryptoXLib.create_btse_client(api_key, sec_key)

    print("Exchange details:")
    await client.get_exchange_info(pair = Pair('BTC', 'USD'))

    print("Account funds:")
    await client.get_funds()

    await client.close()


if __name__ == "__main__":
    async_run(run())
