import asyncio
import logging
import os

from cryptolib.CryptoLib import CryptoLib
from cryptolib.clients.bitforex import enums
from cryptolib.Pair import Pair
from cryptolib.clients.bitforex.exceptions import BitforexException
from cryptolib.clients.bitforex.BitforexWebsocket import OrderBookSubscription, TradeSubscription, TickerSubscription, \
    Ticker24hSubscription

LOG = logging.getLogger("cryptolib")
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

    bitforex = CryptoLib.create_bitforex_client(api_key, sec_key)

    print("\nExchange info:")
    await bitforex.get_exchange_info()

    print("\nOrder book:")
    await bitforex.get_order_book(pair = Pair('ETH', 'BTC'), depth = "1")

    print("\nTicker:")
    await bitforex.get_ticker(pair = Pair('ETH', 'BTC'))

    print("\nSingle fund:")
    await bitforex.get_single_fund(currency = "NOBS")

    print("\nFunds:")
    await bitforex.get_funds()

    print("\nTrades:")
    await bitforex.get_trades(pair = Pair('ETH', 'BTC'), size = "1")

    print("\nCandelsticks:")
    await bitforex.get_candlesticks(pair = Pair('ETH', 'BTC'), interval = enums.CandelstickInterval.I_1W, size = "5")

    print("\nCreate order:")
    try:
        await bitforex.create_order(Pair("ETH", "BTC"), side = enums.OrderSide.SELL, quantity = "1", price = "1")
    except BitforexException as e:
        print(e)

    print("\nCreate multiple orders:")
    await bitforex.create_multi_order(Pair("ETH", "BTC"),
                                      orders = [("1", "1", enums.OrderSide.SELL), ("2", "1", enums.OrderSide.SELL)])

    print("\nCancel order:")
    await bitforex.cancel_order(pair = Pair('ETH', 'BTC'), order_id = "10")

    print("\nCancel multiple orders:")
    await bitforex.cancel_multi_order(pair = Pair('ETH', 'BTC'), order_ids = ["10", "20"])

    print("\nCancel all orders:")
    await bitforex.cancel_all_orders(pair = Pair('ETH', 'BTC'))

    print("\nGet order:")
    try:
        await bitforex.get_order(pair = Pair('ETH', 'BTC'), order_id = "1")
    except BitforexException as e:
        print(e)

    print("\nGet orders:")
    await bitforex.get_orders(pair = Pair('ETH', 'BTC'), order_ids = ["1", "2"])

    print("\nFind orders:")
    await bitforex.find_order(pair = Pair('ETH', 'BTC'), state = enums.OrderState.PENDING)

    # Bundle several subscriptions into a single websocket
    bitforex.compose_subscriptions([
        OrderBookSubscription(pair = Pair('ETH', 'BTC'), depth = "0", callbacks = [order_book_update]),
        OrderBookSubscription(pair = Pair('ETH', 'USDT'), depth = "0", callbacks = [order_book_update2]),
        TradeSubscription(pair = Pair('ETH', 'BTC'), size = "2", callbacks = [trade_update]),
    ])

    # Bundle subscriptions into a separate websocket
    bitforex.compose_subscriptions([
        TickerSubscription(pair = Pair('BTC', 'USDT'), size = "2", interval = enums.CandelstickInterval.I_1MIN,
                           callbacks = [ticker_update]),
        Ticker24hSubscription(pair = Pair('BTC', 'USDT'), callbacks = [ticker24_update])
    ])

    # Execute all websockets asynchronously
    await bitforex.start_websockets()

    await bitforex.close()

if __name__ == "__main__":
    asyncio.run(run())
