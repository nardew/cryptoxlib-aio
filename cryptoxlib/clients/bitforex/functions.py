from cryptoxlib.Pair import Pair


def map_pair(pair: Pair) -> str:
    return f"coin-{pair.quote.lower()}-{pair.base.lower()}"
