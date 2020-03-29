import asyncio
import logging
import os
from datetime import datetime

from cryptolib.CryptoLib import CryptoLib
from cryptolib.clients.binance.BinanceWebsocket import AccountSubscription, BestOrderBookTickerSubscription, \
    TradeSubscription, BestOrderBookSymbolTickerSubscription
from cryptolib.Pair import Pair

LOG = logging.getLogger("cryptolib")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

print(f"Available loggers: {[name for name in logging.root.manager.loggerDict]}\n")

async def account_update(response : dict) -> None:
    print(f"Callback account_update: [{response}]")

async def order_book_update(response : dict) -> None:
    print(f"Callback order_book_update: [{response}]")

async def trade_update(response : dict) -> None:
    local_timestamp_ms = int(datetime.now().timestamp() * 1000)
    server_timestamp_ms = response['data']['E']
    print(f"Callback trade_update: trade update timestamp diff [ms]:"
          f" {local_timestamp_ms - server_timestamp_ms}")

async def orderbook_ticker_update(response : dict) -> None:
    print(f"Callback orderbook_ticker_update: [{response}]")

async def run():
    api_key = os.environ['APIKEY']
    sec_key = os.environ['SECKEY']

    client = CryptoLib.create_binance_client(api_key, sec_key)

    # Bundle several subscriptions into a single websocket
    client.compose_subscriptions([
        BestOrderBookTickerSubscription(callbacks = [orderbook_ticker_update]),
        BestOrderBookSymbolTickerSubscription(pair = Pair("BTC", "USDT"), callbacks = [orderbook_ticker_update]),
        TradeSubscription(pair = Pair('ETH', 'BTC'), callbacks = [trade_update])
    ])

    # Bundle another subscriptions into a separate websocket
    client.compose_subscriptions([
        AccountSubscription(callbacks = [account_update])
    ])

    # Execute all websockets asynchronously
    await client.start_websockets()

    await client.close()

if __name__ == "__main__":
    asyncio.run(run())
