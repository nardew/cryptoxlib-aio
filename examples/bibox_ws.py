import logging
import os
import datetime
from decimal import Decimal

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.bibox.BiboxWebsocket import OrderBookSubscription, TradeSubscription
from cryptoxlib.version_conversions import async_run

LOG = logging.getLogger("cryptoxlib")
LOG.setLevel(logging.INFO)
LOG.addHandler(logging.StreamHandler())

print(f"Available loggers: {[name for name in logging.root.manager.loggerDict]}")


async def order_book_update(response : dict) -> None:
    print(f"Order_book_update: [{response['data']['asks'][0]}] [{response['data']['bids'][0]}]")
    data = response['data']
    server_timestamp = int(Decimal(data['update_time']))
    local_tmstmp_ms = int(datetime.datetime.now(tz = datetime.timezone.utc).timestamp() * 1000)
    print(f"Timestamp diff: {local_tmstmp_ms - server_timestamp} ms")


async def trade_update(response : dict) -> None:
    print(f"Trade_update: {response['data'][0]}")


async def order_book_update3(response : dict) -> None:
    print(f"Callback order_book_update3: [{response}]")


async def user_data_update(response : dict) -> None:
    print(f"Callback user_data_update: [{response}]")


async def run():
    api_key = os.environ['BIBOXAPIKEY']
    sec_key = os.environ['BIBOXSECKEY']

    bibox = CryptoXLib.create_bibox_client(api_key, sec_key)

    bibox.compose_subscriptions([
        OrderBookSubscription(pair = Pair('BTC', 'USDT'), callbacks = [order_book_update]),
    ])

    bibox.compose_subscriptions([
        TradeSubscription(pair = Pair('BTC', 'USDT'), callbacks = [trade_update]),
    ])

    # Execute all websockets asynchronously
    await bibox.start_websockets()

    await bibox.close()

if __name__ == "__main__":
    async_run(run())
