import logging
import os

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.coinmate.CoinmateWebsocket import OrderbookSubscription, TradesSubscription, \
    UserOrdersSubscription, BalancesSubscription, UserTradesSubscription, UserTransfersSubscription
from cryptoxlib.version_conversions import async_run

LOG = logging.getLogger("cryptoxlib")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

print(f"Available loggers: {[name for name in logging.root.manager.loggerDict]}\n")


async def order_book_update(response: dict) -> None:
    print(f"Callback order_book_update: [{response}]")


async def trades_update(response: dict) -> None:
    print(f"Callback trades_update: [{response}]")


async def account_update(response: dict) -> None:
    print(f"Callback account_update: [{response}]")


async def run():
    api_key = os.environ['COINMATEAPIKEY']
    sec_key = os.environ['COINMATESECKEY']
    user_id = os.environ['COINMATEUSERID']

    client = CryptoXLib.create_coinmate_client(user_id, api_key, sec_key)

    # Bundle several subscriptions into a single websocket
    client.compose_subscriptions([
        OrderbookSubscription(Pair("BTC", "EUR"), callbacks = [order_book_update]),
        TradesSubscription(Pair("BTC", "EUR"), callbacks = [trades_update])
    ])

    # Bundle private subscriptions into a separate websocket
    client.compose_subscriptions([
        UserOrdersSubscription(callbacks = [account_update]),
        UserTradesSubscription(callbacks = [account_update]),
        UserTransfersSubscription(callbacks = [account_update]),
        BalancesSubscription(callbacks = [account_update])
    ])

    # Execute all websockets asynchronously
    await client.start_websockets()

if __name__ == "__main__":
    async_run(run())
