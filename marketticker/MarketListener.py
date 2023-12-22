####
# Interface for market listeners
####

import abc
import json
import logging

from marketticker.Symbol import Symbol


class MarketData:
    exchange: str
    symbol: Symbol
    open: float
    high: float
    low: float
    close: float
    volume: float

    last: float = None
    final: bool
    interval: str

    def __init__(self):
        pass

    def __str__(self):
        return f"MarketData(final={self.final} exchange={self.exchange}, symbol={self.symbol.name}, open={self.open}, high={self.high}, low={self.low}, close={self.close}, volume={self.volume})"

    @staticmethod
    def from_json(json_str):
        d = json.loads(json_str)
        return MarketData.from_dict(d)

    @staticmethod
    def from_dict(d):
        m = MarketData()
        m.exchange = d["exchange"]
        m.symbol = Symbol(d["symbol"])
        m.open = d["open"]
        m.high = d["high"]
        m.low = d["low"]
        m.close = d["close"]
        m.volume = d["volume"]
        m.last = d["last"]
        m.final = d["final"]
        return m

    def json(self):
        return json.dumps(self.__dict__())

    def __dict__(self):
        return {
            "exchange": self.exchange,
            "symbol": self.symbol.name,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "last": self.last if self.last is not None else self.close,
            "final": self.final
        }

    pass

class MarketListener(abc.ABC):
    @abc.abstractmethod
    def onMarketDataReceived(self, data: MarketData):
        raise NotImplementedError

    @abc.abstractmethod
    def onMarketTickerReceived(self, data: MarketData):
        raise NotImplementedError

