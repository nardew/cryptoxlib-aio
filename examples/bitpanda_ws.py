import asyncio
import logging
import os

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.bitpanda.enums import TimeUnit
from cryptoxlib.clients.bitpanda.BitpandaWebsocket import AccountSubscription, PricesSubscription, \
    OrderbookSubscription, CandlesticksSubscription, CandlesticksSubscriptionParams, MarketTickerSubscription

LOG = logging.getLogger("cryptoxlib")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

print(f"Available loggers: {[name for name in logging.root.manager.loggerDict]}\n")


async def order_book_update(response: dict) -> None:
    print(f"Callback order_book_update: [{response}]")


async def run():
    api_key = os.environ['BITPANDAAPIKEY']

    client = CryptoXLib.create_bitpanda_client(api_key)

    # Bundle several subscriptions into a single websocket
    client.compose_subscriptions([
        AccountSubscription(),
        PricesSubscription([Pair("BTC", "EUR")]),
        OrderbookSubscription([Pair("BTC", "EUR")], "50", callbacks = [order_book_update]),
        CandlesticksSubscription([CandlesticksSubscriptionParams(Pair("BTC", "EUR"), TimeUnit.MINUTES, 1)]),
        MarketTickerSubscription([Pair("BTC", "EUR")])
    ])

    # Bundle another subscriptions into a separate websocket
    client.compose_subscriptions([
        OrderbookSubscription([Pair("ETH", "EUR")], "3", callbacks = [order_book_update]),
    ])

    # Execute all websockets asynchronously
    await client.start_websockets()

if __name__ == "__main__":
    asyncio.run(run())
