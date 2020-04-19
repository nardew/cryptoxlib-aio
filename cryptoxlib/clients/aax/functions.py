from cryptoxlib.Pair import Pair


def map_pair(pair: Pair) -> str:
    return f"{pair.base}{pair.quote}"
