from marketticker.MarketDataConsumer import MarketDataConsumer
from marketticker.MarketListener import MarketListener, MarketData
from marketticker.Symbol import Symbol


class MarketDataManager:
    exchange = None
    api_key = None
    api_secret = None
    publisher = None

    def __init__(self, exchange, api_key, api_secret):
        self.exchange = exchange
        self.api_key = api_key
        self.api_secret = api_secret

    def onMarketDataReceived(self, data: MarketData):
        if self.publisher is not None:
            self.publisher.publishMarketData(data)

    def onMarketTickerReceived(self, data: MarketData):
        if self.publisher is not None:
            self.publisher.publishMarketTicker(data)

    def createFetcher(self, symbol: Symbol,  interval="1h", marketListener: MarketListener=None,):
        symbol.exchange = self.exchange
        if self.publisher is not None:
            marketListener = self
        c = MarketDataConsumer(self, marketListener, symbol, interval)
        c.start()

        return c

    def setRabbitQueuePublisher(self, rabbitQueuePublisher):
        self.publisher = rabbitQueuePublisher