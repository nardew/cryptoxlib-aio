import logging
import os

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.aax.AAXWebsocket import OrderBookSubscription, AccountSubscription
from cryptoxlib.version_conversions import async_run

LOG = logging.getLogger("cryptoxlib")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

print(f"Available loggers: {[name for name in logging.root.manager.loggerDict]}\n")

async def trade_update(response : dict) -> None:
    print(f"Callback trade_update: [{response}]")


async def order_book_update(response : dict) -> None:
    print(f"Callback order_book_update: [{response}]")


async def order_book_update2(response : dict) -> None:
    print(f"Callback order_book_update2: [{response}]")


async def ticker_update(response : dict) -> None:
    print(f"Callback ticker_update: [{response}]")


async def ticker24_update(response : dict) -> None:
    print(f"Callback ticker24_update: [{response}]")


async def run():
    # to retrieve your API/SEC key go to your bitforex account, create the keys and store them in
    # BITFOREXAPIKEY/BITFOREXSECKEY environment variables
    api_key = os.environ['AAXAPIKEY']
    sec_key = os.environ['AAXSECKEY']
    user_id = os.environ['AAXUSERID']

    aax = CryptoXLib.create_aax_client(api_key, sec_key)

    # Bundle several subscriptions into a single websocket
    aax.compose_subscriptions([
        OrderBookSubscription(pair = Pair('BTC', 'USDT'), depth = 20, callbacks = [order_book_update]),
        OrderBookSubscription(pair = Pair('ETH', 'USDT'), depth = 20, callbacks = [order_book_update2]),
    ])

    # Bundle subscriptions into a separate websocket
    aax.compose_subscriptions([
        AccountSubscription(user_id)
    ])

    # Execute all websockets asynchronously
    await aax.start_websockets()

    await aax.close()

if __name__ == "__main__":
    async_run(run())
