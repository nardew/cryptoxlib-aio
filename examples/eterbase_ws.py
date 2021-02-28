import logging
import os

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.clients.eterbase.EterbaseWebsocket import OrderbookSubscription, TradesSubscription, OHLCVSubscription, \
    AccountSubscription
from cryptoxlib.version_conversions import async_run

LOG = logging.getLogger("cryptoxlib")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

print(f"Available loggers: {[name for name in logging.root.manager.loggerDict]}\n")


async def order_book_update(response: dict) -> None:
    print(f"Callback order_book_update: [{response}]")


async def trades_update(response: dict) -> None:
    print(f"Callback trades_update: [{response}]")


async def ohlcv_update(response: dict) -> None:
    print(f"Callback ohlcv_update: [{response}]")


async def account_update(response: dict) -> None:
    print(f"Callback account_update: [{response}]")


def get_market_id(markets: dict, symbol: str) -> str:
    return next(filter(lambda x: x['symbol'] == symbol, markets['response']))['id']


async def run():
    api_key = os.environ['ETERBASEAPIKEY']
    sec_key = os.environ['ETERBASESECKEY']
    acct_key = os.environ['ETERBASEACCTKEY']

    client = CryptoXLib.create_eterbase_client(acct_key, api_key, sec_key)

    markets = await client.get_markets()
    ethusdt_id = get_market_id(markets, 'ETHUSDT')
    xbaseebase_id = get_market_id(markets, 'XBASEEBASE')

    # Bundle several subscriptions into a single websocket
    client.compose_subscriptions([
        OrderbookSubscription([ethusdt_id, xbaseebase_id], callbacks = [order_book_update]),
        TradesSubscription([ethusdt_id, xbaseebase_id], callbacks = [trades_update]),
        OHLCVSubscription([ethusdt_id, xbaseebase_id], callbacks = [ohlcv_update]),
    ])

    # Bundle another subscriptions into a separate websocket
    client.compose_subscriptions([
        AccountSubscription([ethusdt_id, xbaseebase_id], callbacks = [account_update]),
    ])

    # Execute all websockets asynchronously
    await client.start_websockets()

if __name__ == "__main__":
    async_run(run())
