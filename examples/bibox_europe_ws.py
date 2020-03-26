import asyncio
import logging
import os
import json
import datetime
from decimal import Decimal

from cryptolib.CryptoLib import CryptoLib
from cryptolib.Pair import Pair
from cryptolib.clients.bibox_europe.BiboxEuropeWebsocket import OrderBookSubscription, UserDataSubscription

LOG = logging.getLogger("cryptolib")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

print(f"Available loggers: {[name for name in logging.root.manager.loggerDict]}")


async def order_book_update(response : dict) -> None:
    print(f"Callback order_book_update: [{response}]")
    data = response['data']
    server_timestamp = int(Decimal(data['update_time']))
    local_tmstmp_ms = int(datetime.datetime.now(tz = datetime.timezone.utc).timestamp() * 1000)
    LOG.debug(f"Timestamp diff: {local_tmstmp_ms - server_timestamp} ms")

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

    bibox = CryptoLib.create_bibox_client(api_key, sec_key)

    bibox.compose_subscriptions([
        OrderBookSubscription(pair = Pair('ETH', 'BTC'), callbacks = [order_book_update]),
        #OrderBookSubscription(pair = Pair('XRP', 'BTC'), callbacks = [order_book_update]),
    ])



    # Execute all websockets asynchronously
    await bibox.start_websockets()

    await bibox.close()

if __name__ == "__main__":
    asyncio.run(run())
