from cryptoxlib.Pair import Pair


def map_pair(pair: Pair) -> str:
    return f"{pair.base}{pair.quote}"


def map_ws_pair(pair: Pair) -> str:
    return f"{pair.base.lower()}{pair.quote.lower()}"