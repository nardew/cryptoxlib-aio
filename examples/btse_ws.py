import logging
import os

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.btse.BtseWebsocket import AccountSubscription, OrderbookL2Subscription, OrderbookSubscription, \
    TradeSubscription
from cryptoxlib.version_conversions import async_run

LOG = logging.getLogger("cryptoxlib")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

print(f"Available loggers: {[name for name in logging.root.manager.loggerDict]}\n")


async def order_book_update(response: dict) -> None:
    print(f"Callback order_book_update: [{response}]")


async def run():
    api_key = os.environ['BTSEAPIKEY']
    sec_key = os.environ['BTSESECKEY']

    client = CryptoXLib.create_btse_client(api_key, sec_key)

    # Bundle several subscriptions into a single websocket
    client.compose_subscriptions([
        AccountSubscription(),
        OrderbookL2Subscription([Pair("BTC", "USD"), Pair('ETH', 'BTC')], depth = 1)
    ])

    # Bundle another subscriptions into a separate websocket
    client.compose_subscriptions([
        OrderbookSubscription([Pair('BTSE', 'BTC')], callbacks = [order_book_update]),
        TradeSubscription([Pair('BTSE', 'BTC')])
    ])

    # Execute all websockets asynchronously
    await client.start_websockets()

if __name__ == "__main__":
    async_run(run())
