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

    print("BLVT symbol info:")
    await client.get_blvt_info()

    print("Subscribe BTCUP:")
    try:
        await client.blvt_subscribe("BTCUP", "500000000")
    except Exception as e:
        print(e)

    print("Subscription history:")
    await client.get_blvt_subscribtion_record()

    print("Redeem BTCUP:")
    try:
        await client.blvt_redeem("BTCUP", "500000000")
    except Exception as e:
        print(e)

    print("Redemption history:")
    await client.get_blvt_redemption_record()

    print("BLVT user limits:")
    await client.get_blvt_user_info()

    await client.close()

if __name__ == "__main__":
    async_run(run())
