from cryptoxlib.clients.bitforex.BitforexClient import BitforexClient
from cryptoxlib.clients.liquid.LiquidClient import LiquidClient
from cryptoxlib.clients.bibox.BiboxClient import BiboxClient
from cryptoxlib.clients.bibox_europe.BiboxEuropeClient import BiboxEuropeClient
from cryptoxlib.clients.bitpanda.BitpandaClient import BitpandaClient
from cryptoxlib.clients.binance.BinanceClient import BinanceClient, BinanceTestnetClient
from cryptoxlib.clients.binance.BinanceFuturesClient import BinanceUSDSMFuturesClient, BinanceUSDSMFuturesTestnetClient, \
    BinanceCOINMFuturesClient, BinanceCOINMFuturesTestnetClient
from cryptoxlib.clients.binance import enums as binance_enums
from cryptoxlib.clients.bitvavo.BitvavoClient import BitvavoClient
from cryptoxlib.clients.btse.BtseClient import BtseClient
from cryptoxlib.clients.aax.AAXClient import AAXClient
from cryptoxlib.clients.hitbtc.HitbtcClient import HitbtcClient
from cryptoxlib.clients.eterbase.EterbaseClient import EterbaseClient


class CryptoXLib(object):
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
    def create_binance_client(api_key: str, sec_key: str,
                              api_cluster: binance_enums.APICluster = binance_enums.APICluster.CLUSTER_DEFAULT) -> BinanceClient:
        return BinanceClient(api_key, sec_key, api_cluster = api_cluster)

    @staticmethod
    def create_binance_testnet_client(api_key: str, sec_key: str) -> BinanceTestnetClient:
        return BinanceTestnetClient(api_key, sec_key)

    @staticmethod
    def create_binance_usds_m_futures_client(api_key: str, sec_key: str) -> BinanceUSDSMFuturesClient:
        return BinanceUSDSMFuturesClient(api_key, sec_key)

    @staticmethod
    def create_binance_usds_m_futures_testnet_client(api_key: str, sec_key: str) -> BinanceUSDSMFuturesTestnetClient:
        return BinanceUSDSMFuturesTestnetClient(api_key, sec_key)

    @staticmethod
    def create_binance_coin_m_futures_client(api_key: str, sec_key: str) -> BinanceCOINMFuturesClient:
        return BinanceCOINMFuturesClient(api_key, sec_key)

    @staticmethod
    def create_binance_coin_m_futures_testnet_client(api_key: str, sec_key: str) -> BinanceCOINMFuturesTestnetClient:
        return BinanceCOINMFuturesTestnetClient(api_key, sec_key)

    @staticmethod
    def create_bitvavo_client(api_key: str, sec_key: str) -> BitvavoClient:
        return BitvavoClient(api_key, sec_key)

    @staticmethod
    def create_btse_client(api_key: str, sec_key: str) -> BtseClient:
        return BtseClient(api_key, sec_key)

    @staticmethod
    def create_aax_client(api_key: str, sec_key: str) -> AAXClient:
        return AAXClient(api_key, sec_key)

    @staticmethod
    def create_hitbtc_client(api_key: str, sec_key: str) -> HitbtcClient:
        return HitbtcClient(api_key, sec_key)

    @staticmethod
    def create_eterbase_client(account_id: str, api_key: str, sec_key: str) -> EterbaseClient:
        return EterbaseClient(account_id, api_key, sec_key)