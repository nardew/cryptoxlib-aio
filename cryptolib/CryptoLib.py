from cryptolib.clients.bitforex.BitforexClient import BitforexClient


class CryptoLib(object):
    @staticmethod
    def create_bitforex_client(api_key: str, sec_key: str) -> BitforexClient:
        return BitforexClient(api_key, sec_key)