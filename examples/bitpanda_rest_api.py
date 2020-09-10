import logging
import datetime
import os

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.bitpanda.exceptions import BitpandaException
from cryptoxlib.clients.bitpanda.enums import OrderSide, TimeUnit
from cryptoxlib.version_conversions import async_run

LOG = logging.getLogger("cryptoxlib")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

print(f"Available loggers: {[name for name in logging.root.manager.loggerDict]}")


async def order_book_update(response: dict) -> None:
    print(f"Callback order_book_update: [{response}]")

async def run():
    api_key = os.environ['BITPANDAAPIKEY']

    client = CryptoXLib.create_bitpanda_client(api_key)

    print("Time:")
    response = await client.get_time()
    print(f"Headers: {response['headers']}")

    print("Account balance:")
    await client.get_account_balances()

    print("Account orders:")
    await client.get_account_orders()

    print("Account order:")
    try:
        await client.get_account_order("1")
    except BitpandaException as e:
        print(e)

    print("Create market order:")
    try:
        await client.create_market_order(Pair("BTC", "EUR"), OrderSide.BUY, "10000")
    except BitpandaException as e:
        print(e)

    print("Create limit order:")
    try:
        await client.create_limit_order(Pair("BTC", "EUR"), OrderSide.BUY, "10000", "1")
    except BitpandaException as e:
        print(e)

    print("Create stop loss order:")
    try:
        await client.create_stop_limit_order(Pair("BTC", "EUR"), OrderSide.BUY, "10000", "1", "1")
    except BitpandaException as e:
        print(e)

    print("Delete order:")
    try:
        await client.delete_account_order("1")
    except BitpandaException as e:
        print(e)

    print("Order trades:")
    try:
        await client.get_account_order_trades("1")
    except BitpandaException as e:
        print(e)

    print("Trades:")
    await client.get_account_trades()

    print("Trade:")
    try:
        await client.get_account_trade("1")
    except BitpandaException as e:
        print(e)

    print("Trading volume:")
    await client.get_account_trading_volume()

    print("Currencies:")
    await client.get_currencies()

    print("Candlesticks:")
    await client.get_candlesticks(Pair("BTC", "EUR"), TimeUnit.DAYS, "1",
                                  datetime.datetime.now() - datetime.timedelta(days = 7), datetime.datetime.now())

    print("Fees:")
    await client.get_account_fees()

    print("Instruments:")
    await client.get_instruments()

    print("Order book:")
    await client.get_order_book(Pair("BTC", "EUR"))

    await client.close()


if __name__ == "__main__":
    async_run(run())
