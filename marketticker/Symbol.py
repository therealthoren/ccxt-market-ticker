
from enum import Enum

class SymbolType(Enum):
    SPOT = 1
    FUTURES = 2
    OPTIONS = 3
    PERPETUAL = 4
    INDEX = 5


class Symbol:
    name = None
    exchange = None
    type = SymbolType.SPOT

    def __init__(self, name, exchange=None, type=SymbolType.SPOT):
        if "/" not in name:
            raise Exception("Symbol name must contain a /, e.g. BTC/USDT")
        if exchange is not None:
            self.exchange = exchange
        self.name = name
        self.type = type

    @classmethod
    def typeFromStr(cls, param):
        if param == "spot":
            return SymbolType.SPOT
        elif param == "futures":
            return SymbolType.FUTURES
        elif param == "options":
            return SymbolType.OPTIONS
        elif param == "perpetual":
            return SymbolType.PERPETUAL
        elif param == "index":
            return SymbolType.INDEX
        else:
            raise Exception("Unknown symbol type: "+param)
