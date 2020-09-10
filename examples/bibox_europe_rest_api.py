import logging

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.bibox_europe import enums
from cryptoxlib.clients.bibox_europe.exceptions import BiboxEuropeException
from cryptoxlib.version_conversions import async_run

LOG = logging.getLogger("cryptoxlib")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

print(f"Available loggers: {[name for name in logging.root.manager.loggerDict]}")


async def run():
    #api_key = os.environ['BIBOXEUROPEAPIKEY']
    #sec_key = os.environ['BIBOXEUROPESECKEY']
    api_key = ""
    sec_key = ""

    bibox_europe = CryptoXLib.create_bibox_europe_client(api_key, sec_key)

    print("Ping:")
    await bibox_europe.get_ping()

    print("Pair list:")
    await bibox_europe.get_pairs()

    print("Exchange info:")
    await bibox_europe.get_exchange_info()

    print("User assets:")
    await bibox_europe.get_spot_assets(full = True)

    print("Create order:")
    try:
        await bibox_europe.create_order(pair = Pair('ETH', 'BTC'), order_type = enums.OrderType.LIMIT,
                                 order_side = enums.OrderSide.BUY, price = "1", quantity = "1")
    except BiboxEuropeException as e:
        print(e)

    print("Cancel order:")
    await bibox_europe.cancel_order(order_id = "1234567890")

    await bibox_europe.close()

if __name__ == "__main__":
    async_run(run())
