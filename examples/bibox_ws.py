import asyncio
import logging
import os

from cryptolib.CryptoLib import CryptoLib
from cryptolib.clients.bibox import enums
from cryptolib.Pair import Pair
from cryptolib.clients.bibox.BiboxWebsocket import OrderBookSubscription, UserDataSubscription

LOG = logging.getLogger("cryptolib")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

print(f"Available loggers: {[name for name in logging.root.manager.loggerDict]}")


async def order_book_update(response : dict) -> None:
    print(f"Callback order_book_update: [{response}]")


async def order_book_update2(response : dict) -> None:
    print(f"Callback order_book_update2: [{response}]")


async def order_book_update3(response : dict) -> None:
    print(f"Callback order_book_update3: [{response}]")


async def user_data_update(response : dict) -> None:
    print(f"Callback user_data_update: [{response}]")


async def run():
    api_key = os.environ['BIBOXAPIKEY']
    sec_key = os.environ['BIBOXSECKEY']

    bibox = CryptoLib.create_bibox_client(api_key, sec_key)

    bibox.compose_subscriptions([
        OrderBookSubscription(pair = Pair('ETH', 'BTC'), callbacks = [order_book_update]),
    ])

    bibox.compose_subscriptions([
        UserDataSubscription(callbacks = [user_data_update]),
    ])

    # Execute all websockets asynchronously
    await bibox.start_websockets()

    await bibox.close()

if __name__ == "__main__":
    asyncio.run(run())
