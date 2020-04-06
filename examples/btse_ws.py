import asyncio
import logging
import os

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.Pair import Pair
#from cryptoxlib.clients.btse.enums import TimeUnit
from cryptoxlib.clients.btse.BtseWebsocket import AccountSubscription

LOG = logging.getLogger("cryptoxlib")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

LOG = logging.getLogger("websockets")
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
        #OrderbookSubscription([Pair("BTC", "EUR")], "50", callbacks = [order_book_update]),
    ])

    # Bundle another subscriptions into a separate websocket
    #client.compose_subscriptions([
    #    OrderbookSubscription([Pair("ETH", "EUR")], "3", callbacks = [order_book_update]),
    #])

    # Execute all websockets asynchronously
    await client.start_websockets()

if __name__ == "__main__":
    asyncio.run(run())
