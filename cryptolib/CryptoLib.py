from cryptolib.clients.bitforex.BitforexClient import BitforexClient
from cryptolib.clients.liquid.LiquidClient import LiquidClient
from cryptolib.clients.bibox.BiboxClient import BiboxClient
from cryptolib.clients.bibox_europe.BiboxEuropeClient import BiboxEuropeClient
from cryptolib.clients.bitpanda.BitpandaClient import BitpandaClient
from cryptolib.clients.binance.BinanceClient import BinanceClient


class CryptoLib(object):
    @staticmethod
    def create_bitforex_client(api_key: str, sec_key: str) -> BitforexClient:
        return BitforexClient(api_key, sec_key)

    @staticmethod
    def create_liquid_client(api_key: str, sec_key: str) -> LiquidClient:
        return LiquidClient(api_key, sec_key)

    @staticmethod
    def create_bibox_client(api_key: str, sec_key: str) -> BiboxClient:
        return BiboxClient(api_key, sec_key)

    @staticmethod
    def create_bibox_europe_client(api_key: str, sec_key: str) -> BiboxEuropeClient:
        return BiboxEuropeClient(api_key, sec_key)

    @staticmethod
    def create_bitpanda_client(api_key: str) -> BitpandaClient:
        return BitpandaClient(api_key)

    @staticmethod
    def create_binance_client(api_key: str, sec_key: str) -> BinanceClient:
        return BinanceClient(api_key, sec_key)