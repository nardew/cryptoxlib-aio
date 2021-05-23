from cryptoxlib.Pair import Pair
from cryptoxlib.clients.binance.types import PairSymbolType
from cryptoxlib.clients.binance.exceptions import BinanceException


def map_pair(pair: Pair) -> str:
    return f"{pair.base}{pair.quote}"


def map_ws_pair(pair: Pair) -> str:
    return map_pair(pair).lower()


def extract_symbol(symbol: PairSymbolType) -> str:
    if isinstance(symbol, str):
        return symbol
    elif isinstance(symbol, Pair):
        return map_pair(symbol)

    raise BinanceException(f"Symbol [{symbol}] is neither string not Pair.")


def extract_ws_symbol(symbol: PairSymbolType) -> str:
    return extract_symbol(symbol).lower()
