import logging
import os
import json

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.clients.liquid import enums
from cryptoxlib.clients.liquid.exceptions import LiquidException
from cryptoxlib.version_conversions import async_run

LOG = logging.getLogger("cryptoxlib")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

print(f"Available loggers: {[name for name in logging.root.manager.loggerDict]}")


async def run():
    api_key = os.environ['LIQUIDAPIKEY']
    sec_key = os.environ['LIQUIDSECKEY']

    liquid = CryptoXLib.create_liquid_client(api_key, sec_key)

    print("Products:")
    products = await liquid.get_products()
    for product in products['response']:
        if product['currency_pair_code'] == 'ETHBTC':
            print(json.dumps(product, indent = 4, sort_keys = True))

    print("Product:")
    product = await liquid.get_product(product_id = "1")
    print(json.dumps(product['response'], indent = 4, sort_keys = True))

    print("Orderbook:")
    await liquid.get_order_book("1")

    print("Order:")
    try:
        await liquid.get_order("1")
    except LiquidException as e:
        print(e)

    print("Create order:")
    try:
        await liquid.create_order(product_id = "1", order_side = enums.OrderSide.BUY, order_type = enums.OrderType.LIMIT, quantity = "0",
                                  price = "1")
    except LiquidException as e:
        print(e)

    print("Cancel order:")
    try:
        await liquid.cancel_order(order_id = "1")
    except LiquidException as e:
        print(e)

    print("Crypto accounts:")
    await liquid.get_crypto_accounts()

    print("Fiat accounts:")
    await liquid.get_fiat_accounts()

    print("Account details:")
    await liquid.get_account_details(currency = "BTC")

    print("Currencies:")
    currencies = await liquid.get_currencies()
    for currency in currencies['response']:
        if currency['currency'] in ['BTC', 'ETH', 'USD', 'QASH']:
            print(json.dumps(currency, indent = 4))

    await liquid.close()

if __name__ == "__main__":
    async_run(run())
