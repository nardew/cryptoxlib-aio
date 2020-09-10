import logging
import os
import uuid

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.hitbtc.HitbtcWebsocket import TickerSubscription, OrderbookSubscription, TradesSubscription, \
    AccountSubscription, ClientWebsocketHandle, CreateOrderMessage, CancelOrderMessage
from cryptoxlib.clients.hitbtc import enums
from cryptoxlib.version_conversions import async_run

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


async def account_update(response: dict, websocket: ClientWebsocketHandle) -> None:
    print(f"Callback account_update: [{response}]")

    # as soon as account channel subscription is confirmed, fire testing orders
    if 'id' in response and 'result' in response and response['result'] == True:
        await websocket.send(CreateOrderMessage(
            pair = Pair('ETH', 'BTC'),
            type = enums.OrderType.LIMIT,
            side = enums.OrderSide.BUY,
            amount = "1000000000",
            price = "0.000001",
            client_id = str(uuid.uuid4())[:32]
        ))

        await websocket.send(CancelOrderMessage(
            client_id = "client_id"
        ))


async def run():
    api_key = os.environ['HITBTCAPIKEY']
    sec_key = os.environ['HITBTCSECKEY']

    client = CryptoXLib.create_hitbtc_client(api_key, sec_key)

    # Bundle several subscriptions into a single websocket
    client.compose_subscriptions([
        AccountSubscription(callbacks = [account_update]),
        OrderbookSubscription(pair = Pair("ETH", "BTC"), callbacks = [order_book_update]),
        TickerSubscription(pair = Pair("BTC", "USD"), callbacks = [ticker_update])
    ])

    # Bundle another subscriptions into a separate websocket
    client.compose_subscriptions([
        TradesSubscription(pair = Pair("ETH", "BTC"), limit = 5,callbacks = [trade_update])
    ])

    # Execute all websockets asynchronously
    await client.start_websockets()

if __name__ == "__main__":
    async_run(run())
