import logging
import uuid
import os

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.eterbase.exceptions import EterbaseException
from cryptoxlib.clients.eterbase import enums
from cryptoxlib.version_conversions import async_run

LOG = logging.getLogger("cryptoxlib")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

print(f"Available loggers: {[name for name in logging.root.manager.loggerDict]}")


def get_market_id(markets: dict, symbol: str) -> str:
    return next(filter(lambda x: x['symbol'] == symbol, markets['response']))['id']


async def order_book_update(response: dict) -> None:
    print(f"Callback order_book_update: [{response}]")


async def run():
    api_key = os.environ['ETERBASEAPIKEY']
    sec_key = os.environ['ETERBASESECKEY']
    acct_key = os.environ['ETERBASEACCTKEY']

    client = CryptoXLib.create_eterbase_client(acct_key, api_key, sec_key)

    print("Time:")
    response = await client.get_ping()
    print(f"Headers: {response['headers']}")

    print("Currencies:")
    await client.get_currencies()

    print("Markets:")
    markets = await client.get_markets()

    print("Balances:")
    try:
        await client.get_balances()
    except EterbaseException as e:
        print(e)

    print("Create market order:")
    try:
        await client.create_order(pair_id = get_market_id(markets, 'ETHUSDT'), side = enums.OrderSide.BUY,
                                       type = enums.OrderType.LIMIT, amount = "100000", price = "1",
                                       time_in_force = enums.TimeInForce.GOOD_TILL_CANCELLED)
    except EterbaseException as e:
        print(e)

    print("Cancel order:")
    try:
        await client.cancel_order(order_id = str(uuid.uuid4()))
    except EterbaseException as e:
        print(e)

    await client.close()


if __name__ == "__main__":
    async_run(run())
