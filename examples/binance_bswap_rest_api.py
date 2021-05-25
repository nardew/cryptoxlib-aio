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

    print('Swap pools:')
    await client.get_bswap_pools()

    print('Swap liquidity:')
    await client.get_bswap_liquidity()

    print('Add liquidity:')
    try:
        await client.bswap_add_liquidity(0, 'BTC', '10000000')
    except Exception as e:
        print(e)

    print('Remove liquidity:')
    try:
        await client.bswap_remove_liquidity(0, 'BTC', '10000000', type = enums.LiquidityRemovalType.COMBINATION)
    except Exception as e:
        print(e)

    print('Liquidity history:')
    await client.get_bswap_liquidity_operations()

    print('Request quote:')
    await client.get_bswap_quote(Pair('BTC', 'USDT'), '1000')

    print('Swap:')
    try:
        await client.bswap_swap(Pair('BTC', 'USDT'), '100000000000')
    except Exception as e:
        print(e)

    print('Swap hisotry:')
    await client.get_bswap_swap_history()

    await client.close()

if __name__ == "__main__":
    async_run(run())
