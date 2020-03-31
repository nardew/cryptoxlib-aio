class Pair(object):
    def __init__(self, base: str, quote: str) -> None:
        self.base = base
        self.quote = quote

    def __str__(self):
        return self.base + '/' + self.quote

    def __repr__(self):
        return self.__str__()
