import logging
import os

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.bitpanda.enums import TimeUnit, OrderSide, OrderType
from cryptoxlib.clients.bitpanda.BitpandaWebsocket import AccountSubscription, PricesSubscription, \
    OrderbookSubscription, CandlesticksSubscription, CandlesticksSubscriptionParams, MarketTickerSubscription, \
    TradingSubscription, OrdersSubscription, ClientWebsocketHandle, CreateOrderMessage, CancelOrderMessage, \
    UpdateOrderMessage, CancelAllOrdersMessage
from cryptoxlib.version_conversions import async_run

LOG = logging.getLogger("cryptoxlib")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

print(f"Available loggers: {[name for name in logging.root.manager.loggerDict]}\n")


async def order_book_update(response: dict) -> None:
    print(f"Callback order_book_update: [{response}]")


async def trading_update(response: dict) -> None:
    print(f"Callback trading_update: [{response}]")


async def account_update(response: dict) -> None:
    print(f"Callback account_update: [{response}]")


async def orders_update(response: dict, websocket: ClientWebsocketHandle) -> None:
    print(f"Callback orders_update: [{response}]")

    # as soon as ORDERS channel subscription is confirmed, fire testing orders
    if response['type'] == 'SUBSCRIPTIONS':
        await websocket.send(CreateOrderMessage(
            pair = Pair('BTC', 'EUR'),
            type = OrderType.LIMIT,
            side = OrderSide.BUY,
            amount = "0.0001",
            price = "10"
        ))

        await websocket.send(CancelOrderMessage(
            order_id = "d44cf37a-335d-4936-9336-4c7944cd00ec"
        ))

        await websocket.send(CancelAllOrdersMessage(
            order_ids = ["d44cf37a-335d-4936-9336-4c7944cd00ec"]
        ))

        await websocket.send(UpdateOrderMessage(
            amount = "1",
            order_id = "d44cf37a-335d-4936-9336-4c7944cd00ec"
        ))


async def run():
    api_key = os.environ['BITPANDAAPIKEY']

    client = CryptoXLib.create_bitpanda_client(api_key)

    # Bundle several subscriptions into a single websocket
    client.compose_subscriptions([
        AccountSubscription(callbacks = [account_update]),
        PricesSubscription([Pair("BTC", "EUR")]),
        OrderbookSubscription([Pair("BTC", "EUR")], "50", callbacks = [order_book_update]),
        CandlesticksSubscription([CandlesticksSubscriptionParams(Pair("BTC", "EUR"), TimeUnit.MINUTES, 1)]),
        MarketTickerSubscription([Pair("BTC", "EUR")])
    ])

    # Bundle another subscriptions into a separate websocket
    client.compose_subscriptions([
        OrderbookSubscription([Pair("ETH", "EUR")], "3", callbacks = [order_book_update]),
    ])

    # Bundle another subscriptions into a separate websocket
    client.compose_subscriptions([
        TradingSubscription(callbacks = [trading_update]),
        OrdersSubscription(callbacks = [orders_update]),
    ])

    # Execute all websockets asynchronously
    await client.start_websockets()

if __name__ == "__main__":
    async_run(run())
