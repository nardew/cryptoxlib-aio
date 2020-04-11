class CryptoXLibException(Exception):
    pass


class WebsocketReconnectionException(CryptoXLibException):
    pass


class WebsocketError(CryptoXLibException):
    pass


class WebsocketClosed(CryptoXLibException):
    pass