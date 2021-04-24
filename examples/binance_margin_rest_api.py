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

    print("All margin assets:")
    await client.get_margin_all_assets()

    print("Margin pair:")
    await client.get_margin_pair(Pair('BTC', 'USDT'))

    print("Margin price index:")
    await client.get_margin_price_index(Pair('BTC', 'USDT'))

    print("Margin account balance:")
    await client.get_margin_account()

    await client.close()

if __name__ == "__main__":
    async_run(run())
