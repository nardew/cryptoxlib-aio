from typing import List

from cryptoxlib.Pair import Pair


def map_pair(pair: Pair) -> str:
    return f"{pair.base}_{pair.quote}"


def map_multiple_pairs(pairs : List[Pair], sort = False) -> List[str]:
    pairs = [pair.base + "_" + pair.quote for pair in pairs]

    if sort:
        return sorted(pairs)
    else:
        return pairs