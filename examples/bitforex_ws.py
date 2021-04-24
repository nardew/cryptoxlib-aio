import logging
import os

from cryptoxlib.version_conversions import async_run
from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.clients.bitforex import enums
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.bitforex.BitforexWebsocket import OrderBookSubscription, TradeSubscription, TickerSubscription, \
    Ticker24hSubscription
from cryptoxlib.version_conversions import async_run

LOG = logging.getLogger("cryptoxlib")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

print(f"Available loggers: {[name for name in logging.root.manager.loggerDict]}\n")

async def trade_update(response : dict) -> None:
    print(f"Callback trade_update: [{response}]")


async def order_book_update(response : dict) -> None:
    print(f"Callback order_book_update: [{response}]")


async def order_book_update2(response : dict) -> None:
    print(f"Callback order_book_update2: [{response}]")


async def ticker_update(response : dict) -> None:
    print(f"Callback ticker_update: [{response}]")


async def ticker24_update(response : dict) -> None:
    print(f"Callback ticker24_update: [{response}]")


async def run():
    # to retrieve your API/SEC key go to your bitforex account, create the keys and store them in
    # BITFOREXAPIKEY/BITFOREXSECKEY environment variables
    api_key = os.environ['BITFOREXAPIKEY']
    sec_key = os.environ['BITFOREXSECKEY']

    bitforex = CryptoXLib.create_bitforex_client(api_key, sec_key)

    # Bundle several subscriptions into a single websocket
    bitforex.compose_subscriptions([
        OrderBookSubscription(pair = Pair('ETH', 'BTC'), depth = "0", callbacks = [order_book_update]),
        OrderBookSubscription(pair = Pair('ETH', 'USDT'), depth = "0", callbacks = [order_book_update2]),
        TradeSubscription(pair = Pair('ETH', 'BTC'), size = "2", callbacks = [trade_update]),
    ])

    # Bundle subscriptions into a separate websocket
    bitforex.compose_subscriptions([
        TickerSubscription(pair = Pair('BTC', 'USDT'), size = "2", interval = enums.CandlestickInterval.I_1MIN,
                           callbacks = [ticker_update]),
        Ticker24hSubscription(pair = Pair('BTC', 'USDT'), callbacks = [ticker24_update])
    ])

    # Execute all websockets asynchronously
    await bitforex.start_websockets()

    await bitforex.close()

if __name__ == "__main__":
    async_run(run())
