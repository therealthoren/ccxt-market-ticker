import importlib

import asyncio
import ccxt

from marketticker.MarketDataConsumer import reconvertContractType
from marketticker.Symbol import SymbolType


class ExchangeService:
    def __init__(self, exchangeData, loop):
        self.name = exchangeData["name"]
        self.api_key = exchangeData["api_key"]
        self.api_secret = exchangeData["api_secret"]
        self.exchange = self.generateExchange()
        if loop is None:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        self.loop = loop

    def getAllSymbols(self):

        return self.exchange.markets

    def generateExchange(self):

        exc = getattr(ccxt, self.name)
        t = None
        if t == SymbolType.FUTURES:
            exchange = exc({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'adjustForTimeDifference': True,
                'options': {
                        'defaultType': reconvertContractType(t),
                        'adjustForTimeDifference': True,
                    }})
        else:
            exchange = exc({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'adjustForTimeDifference': True,
                'options': {
                    'adjustForTimeDifference': True,
                }
            })

        exchange.load_markets()
        return exchange

    def getHistoricalData(self, symbol, timeframe, from_date, to_date):
        # convert dateto timestamp
        since = int(from_date.timestamp() * 1000)
        limit = None
        if to_date is not None:
            limit = int((from_date - to_date).timestamp() * 1000)

        symbols = self.exchange.fetch_ohlcv(symbol, timeframe, since, limit)
        if limit is None:
            # remove last element
            symbols.pop()
        return symbols