
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

    def __init__(self, name, type=SymbolType.SPOT):
        if "/" not in name:
            raise Exception("Symbol name must contain a /, e.g. BTC/USDT")
        self.name = name
        self.type = type