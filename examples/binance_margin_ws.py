import logging
import os

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.clients.binance.BinanceWebsocket import AccountCrossMarginSubscription, AccountIsolatedMarginSubscription,\
    CandlestickSubscription
from cryptoxlib.clients.binance.enums import Interval
from cryptoxlib.Pair import Pair
from cryptoxlib.version_conversions import async_run

LOG = logging.getLogger("cryptoxlib")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

print(f"Available loggers: {[name for name in logging.root.manager.loggerDict]}\n")


async def account_update(response : dict) -> None:
    print(f"Callback account_update: [{response}]")


async def candlestick_update(response : dict) -> None:
    print(f"Callback candlestick_update: [{response}]")


async def run():
    api_key = os.environ['APIKEY']
    sec_key = os.environ['SECKEY']

    client = CryptoXLib.create_binance_client(api_key, sec_key)

    # Bundle several subscriptions into a single websocket
    client.compose_subscriptions([
        CandlestickSubscription(Pair('BTC', 'USDT'), Interval.I_1MIN, callbacks = [candlestick_update])
    ])

    # Bundle another subscriptions into a separate websocket
    client.compose_subscriptions([
        # uncomment if isolated margin account is setup
        #AccountIsolatedMarginSubscription(pair = Pair('BTC', 'USDT'), callbacks = [account_update]),
        AccountCrossMarginSubscription(callbacks = [account_update])
    ])

    # Execute all websockets asynchronously
    await client.start_websockets()

    await client.close()

if __name__ == "__main__":
    async_run(run())
