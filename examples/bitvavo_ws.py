import logging
import os

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.bitvavo import enums
from cryptoxlib.clients.bitvavo.BitvavoWebsocket import AccountSubscription, \
    OrderbookSubscription, CandlesticksSubscription, TickerSubscription, Ticker24Subscription
from cryptoxlib.version_conversions import async_run

LOG = logging.getLogger("cryptoxlib")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())
LOG = logging.getLogger("websockets")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

print(f"Available loggers: {[name for name in logging.root.manager.loggerDict]}\n")


async def order_book_update(response: dict) -> None:
    print(f"Callback order_book_update: [{response}]")


async def ticker_update(response: dict) -> None:
    print(f"Callback ticker_update: [{response}]")


async def ticker24_update(response: dict) -> None:
    print(f"Callback ticker24_update: [{response}]")


async def run():
    api_key = os.environ['BITVAVOAPIKEY']
    sec_key = os.environ['BITVAVOSECKEY']

    client = CryptoXLib.create_bitvavo_client(api_key, sec_key)

    # Bundle several subscriptions into a single websocket
    client.compose_subscriptions([
        AccountSubscription(pairs = [Pair("BTC", "EUR")]),
        TickerSubscription([Pair("BTC", "EUR")], callbacks = [ticker_update]),
        Ticker24Subscription([Pair("BTC", "EUR")], callbacks = [ticker24_update]),
        OrderbookSubscription([Pair("BTC", "EUR")], callbacks = [order_book_update]),
    ])

    # Bundle another subscriptions into a separate websocket
    client.compose_subscriptions([
        CandlesticksSubscription(pairs = [Pair("BTC", "EUR")], intervals = [enums.CandlestickInterval.I_1MIN])
    ])

    # Execute all websockets asynchronously
    await client.start_websockets()

if __name__ == "__main__":
    async_run(run())
