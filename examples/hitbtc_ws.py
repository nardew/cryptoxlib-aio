import asyncio
import logging
import os

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.hitbtc.HitbtcWebsocket import TickerSubscription, OrderbookSubscription, TradesSubscription, \
    AccountSubscription

LOG = logging.getLogger("cryptoxlib")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

print(f"Available loggers: {[name for name in logging.root.manager.loggerDict]}\n")


async def order_book_update(response: dict) -> None:
    print(f"Callback order_book_update: [{response}]")

async def ticker_update(response: dict) -> None:
    print(f"Callback ticker_update: [{response}]")

async def trade_update(response: dict) -> None:
    print(f"Callback trade_update: [{response}]")


async def run():
    api_key = os.environ['HITBTCAPIKEY']
    sec_key = os.environ['HITBTCSECKEY']

    client = CryptoXLib.create_hitbtc_client(api_key, sec_key)

    # Bundle several subscriptions into a single websocket
    client.compose_subscriptions([
        AccountSubscription(),
        OrderbookSubscription(pair = Pair("BTC", "USD"), callbacks = [order_book_update]),
        TickerSubscription(pair = Pair("BTC", "USD"), callbacks = [ticker_update])
    ])

    # Bundle another subscriptions into a separate websocket
    client.compose_subscriptions([
        TradesSubscription(pair = Pair("ETH", "BTC"), limit = 5,callbacks = [trade_update])
    ])

    # Execute all websockets asynchronously
    await client.start_websockets()

if __name__ == "__main__":
    asyncio.run(run())
