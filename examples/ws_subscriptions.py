import logging
import os

import asyncio

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.PeriodicChecker import PeriodicChecker
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.binance.BinanceClient import BinanceClient
from cryptoxlib.clients.binance.BinanceWebsocket import OrderBookSymbolTickerSubscription
from cryptoxlib.version_conversions import async_run

LOG = logging.getLogger("cryptoxlib")
LOG.setLevel(logging.INFO)
LOG.addHandler(logging.StreamHandler())

print(f"Available loggers: {[name for name in logging.root.manager.loggerDict]}\n")


async def order_book_update(response: dict) -> None:
    pass


class Subscriptions:
    def __init__(self):
        self.subscriptions = [
            [
                OrderBookSymbolTickerSubscription(Pair("BTC", "USDT"), callbacks = [self.call1]),
                OrderBookSymbolTickerSubscription(Pair("ETH", "USDT"), callbacks = [self.call1])
            ],
            [
                OrderBookSymbolTickerSubscription(Pair("BNB", "USDT"), callbacks = [self.call2]),
                OrderBookSymbolTickerSubscription(Pair("XRP", "USDT"), callbacks = [self.call2])
            ],
            [
                OrderBookSymbolTickerSubscription(Pair("ADA", "USDT"), callbacks = [self.call3]),
                OrderBookSymbolTickerSubscription(Pair("DOT", "USDT"), callbacks = [self.call3])
            ]
        ]
        self.subscription_set_ids = []
        self.timers = [
            PeriodicChecker(100),
            PeriodicChecker(100),
            PeriodicChecker(100)
        ]

    async def call1(self, response : dict):
        if self.timers[0].check():
            print(response)

    async def call2(self, response : dict):
        if self.timers[1].check():
            print(response)

    async def call3(self, response : dict):
        if self.timers[2].check():
            print(response)


# global container for various subscription compositions
sub = Subscriptions()


async def main_loop(client: BinanceClient) -> None:
    i = 0
    sleep_sec = 1
    while True:
        if i == 3:
            print("Unsubscribing BTC/USDT")
            await client.unsubscribe_subscriptions([sub.subscriptions[0][0]])

        if i == 6:
            print("Unsubscribing BNB/USDT")
            await client.unsubscribe_subscriptions([sub.subscriptions[1][0]])

        if i == 9:
            print("Unsubscribing ADA/USDT and DOT/USDT")
            await client.unsubscribe_subscription_set(sub.subscription_set_ids[2])

        if i == 12:
            print("Unsubscribing all")
            await client.unsubscribe_all()

        if i == 15:
            print("Subscribe BNB/BTC")
            await client.add_subscriptions(sub.subscription_set_ids[0],
                                           [OrderBookSymbolTickerSubscription(Pair("BNB", "BTC"), callbacks = [sub.call1])])

        if i == 18:
            print("Subscribe ETH/USDT again")
            await client.add_subscriptions(sub.subscription_set_ids[0],
                                           [OrderBookSymbolTickerSubscription(Pair("ETH", "USDT"), callbacks = [sub.call1])])

        if i == 21:
            print("Subscribe ADA/USDT and XRP/USDT again")
            await client.add_subscriptions(sub.subscription_set_ids[1],
                                           [OrderBookSymbolTickerSubscription(Pair("ADA", "USDT"), callbacks = [sub.call2]),
                                            OrderBookSymbolTickerSubscription(Pair("XRP", "USDT"), callbacks = [sub.call2])])

        if i == 24:
            print("Shutting down websockets.")
            await client.shutdown_websockets()

        if i == 27:
            print("Quitting the main loop.")
            break

        i += 1
        await asyncio.sleep(sleep_sec)


async def run():
    api_key = os.environ['APIKEY']
    sec_key = os.environ['SECKEY']

    client = CryptoXLib.create_binance_client(api_key, sec_key)

    # initialize three independent websockets
    sub.subscription_set_ids.append(client.compose_subscriptions(sub.subscriptions[0]))
    sub.subscription_set_ids.append(client.compose_subscriptions(sub.subscriptions[1]))
    sub.subscription_set_ids.append(client.compose_subscriptions(sub.subscriptions[2]))

    try:
        await asyncio.gather(*[
            client.start_websockets(),
            main_loop(client)
        ])
    except Exception as e:
        print(f"Out: {e}")

    await client.close()
    print("Exiting.")


if __name__ == "__main__":
    async_run(run())
