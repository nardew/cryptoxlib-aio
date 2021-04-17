import logging
import os
from datetime import datetime

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.clients.binance.BinanceWebsocket import AccountSubscription, OrderBookTickerSubscription, \
    TradeSubscription, OrderBookSymbolTickerSubscription, CandlestickSubscription
from cryptoxlib.clients.binance.enums import Interval
from cryptoxlib.Pair import Pair
from cryptoxlib.version_conversions import async_run

LOG = logging.getLogger("cryptoxlib")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

print(f"Available loggers: {[name for name in logging.root.manager.loggerDict]}\n")

async def account_update(response : dict) -> None:
    print(f"Callback account_update: [{response}]")

async def order_book_update(response : dict) -> None:
    print(f"Callback order_book_update: [{response}]")

async def candlestick_update(response : dict) -> None:
    print(f"Callback candlestick_update: [{response}]")

async def trade_update(response : dict) -> None:
    local_timestamp_ms = int(datetime.now().timestamp() * 1000)
    server_timestamp_ms = response['data']['E']
    print(f"Callback trade_update: trade update timestamp diff [ms]:"
          f" {local_timestamp_ms - server_timestamp_ms}")

async def orderbook_ticker_update(response : dict) -> None:
    print(f"Callback orderbook_ticker_update: [{response}]")

async def run():
    api_key = os.environ['BINANCETESTAPIKEY']
    sec_key = os.environ['BINANCETESTSECKEY']

    client = CryptoXLib.create_binance_testnet_client(api_key, sec_key)

    # Bundle several subscriptions into a single websocket
    client.compose_subscriptions([
        OrderBookTickerSubscription(callbacks = [orderbook_ticker_update]),
        OrderBookSymbolTickerSubscription(pair = Pair("BTC", "USDT"), callbacks = [orderbook_ticker_update]),
        TradeSubscription(pair = Pair('ETH', 'BTC'), callbacks = [trade_update]),
        CandlestickSubscription(Pair('BTC', 'USDT'), Interval.I_1MIN, callbacks = [candlestick_update])
    ])

    # Bundle another subscriptions into a separate websocket
    client.compose_subscriptions([
        AccountSubscription(callbacks = [account_update])
    ])

    # Execute all websockets asynchronously
    await client.start_websockets()

    await client.close()

if __name__ == "__main__":
    async_run(run())
