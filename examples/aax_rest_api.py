import asyncio
import logging
import os

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.clients.aax import enums
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.aax.exceptions import AAXException

LOG = logging.getLogger("cryptoxlib")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

print(f"Available loggers: {[name for name in logging.root.manager.loggerDict]}")


async def run():
    # to retrieve your API/SEC key go to your bitforex account, create the keys and store them in
    # BITFOREXAPIKEY/BITFOREXSECKEY environment variables
    api_key = os.environ['AAXAPIKEY']
    sec_key = os.environ['AAXSECKEY']

    aax = CryptoXLib.create_bitforex_client(api_key, sec_key)

    print("Exchange info:")
    await aax.get_exchange_info()

    await aax.close()

if __name__ == "__main__":
    asyncio.run(run())
