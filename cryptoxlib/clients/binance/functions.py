from cryptoxlib.Pair import Pair
from cryptoxlib.clients.binance.exceptions import BinanceException


def map_pair(pair: Pair) -> str:
    return f"{pair.base}{pair.quote}"


def map_ws_pair(pair: Pair) -> str:
    return f"{pair.base.lower()}{pair.quote.lower()}"


def get_ws_symbol(pair: Pair = None, symbol: str = None) -> str:
    if pair is None and symbol is None:
        raise BinanceException("One of pair and symbol must be provided.")

    if pair is not None and symbol is not None:
        raise BinanceException(f"Only one of pair [{pair}] or symbol [{symbol}] can be provided.")

    if pair is not None:
        return map_ws_pair(pair)
    else:
        return symbol.lower()