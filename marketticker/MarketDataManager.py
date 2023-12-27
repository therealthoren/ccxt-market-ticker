from marketticker.MarketDataConsumer import MarketDataConsumer
from marketticker.MarketListener import MarketListener, MarketData
from marketticker.Symbol import Symbol


class MarketDataManager:
    exchange = None
    api_key = None
    api_secret = None
    publisher = None
    marketListener = None
    loop = None

    def __init__(self, exchange, api_key, api_secret, loop=None):
        self.exchange = exchange
        self.api_key = api_key
        self.api_secret = api_secret
        self.loop = loop

    def onMarketDataReceived(self, data: MarketData):
        if self.publisher is not None:
            try:
                self.publisher.publishMarketData(data)
            except Exception as e:
                print(e)
        if self.marketListener is not None:
            self.marketListener.onMarketDataReceived(data)

    def onMarketTickerReceived(self, data: MarketData):
        if self.publisher is not None:
            try:
                self.publisher.publishMarketTicker(data)
            except Exception as e:
                print(e)
        if self.marketListener is not None:
            self.marketListener.onMarketTickerReceived(data)

    def createFetcher(self, symbol: Symbol,  interval="1h", marketListener: MarketListener=None,):
        symbol.exchange = self.exchange
        if self.publisher is not None:
            self.marketListener = marketListener
            marketListener = self
        c = MarketDataConsumer(self, marketListener, symbol, interval, self.loop)
        c.start()

        return c

    def setRabbitQueuePublisher(self, rabbitQueuePublisher):
        self.publisher = rabbitQueuePublisher

    def stop(self):
        self.publisher.stop()