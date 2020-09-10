import logging

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.bibox_europe.BiboxEuropeWebsocket import OrderBookSubscription
from cryptoxlib.version_conversions import async_run

LOG = logging.getLogger("cryptoxlib")
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
    #api_key = os.environ['BIBOXEUROPEAPIKEY']
    #sec_key = os.environ['BIBOXEUROPESECKEY']
    api_key = ""
    sec_key = ""

    bibox = CryptoXLib.create_bibox_europe_client(api_key, sec_key)

    bibox.compose_subscriptions([
        OrderBookSubscription(pair = Pair('ETH', 'BTC'), callbacks = [order_book_update]),
        OrderBookSubscription(pair = Pair('BTC', 'EUR'), callbacks = [order_book_update]),
    ])

    # Execute all websockets asynchronously
    await bibox.start_websockets()

    await bibox.close()

if __name__ == "__main__":
    async_run(run())
