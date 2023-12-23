import unittest

from marketticker.RabbitMQListener import RabbitMQListener
from marketticker.Symbol import Symbol
from marketticker.factory import CCXTMarketTickerFactory


class TestMarketWithRabbit(unittest.TestCase):

    def test_watch_with_rabbit(self):
        factory = CCXTMarketTickerFactory()
        factory.installRabbitQueue("localhost", 5672, "test", "test")
        fetchService = factory.createBasicMarketDataManager(
            "binance",
            "",
            ""
        )
        if fetchService is None:
            self.fail("fetchService is None")

        fetcher = None

        class YourListener2:
            def onMarketDataReceived(self, data):
                print("2: "+str(data))

            def onMarketTickerReceived(self, data):
                print("2: "+str(data))

        class YourListener:
            def onMarketDataReceived(self, data):
                print("1: "+str(data))

            def onMarketTickerReceived(self, data):
                print("1: "+str(data))

        listener = RabbitMQListener("localhost", 5672, "test", "test")
        listener.connect()

        listener2 = RabbitMQListener("localhost", 5672, "test", "test")
        listener2.connect()

        try:
            fetcher = fetchService.createFetcher(Symbol("BTC/USDT"), "1m")

            listener.followMarketTicker("binance", Symbol("BTC/USDT"), "1m", YourListener())
            listener2.followMarketTicker("binance", Symbol("BTC/USDT"), "1m", YourListener2())

            fetcher.wait()
        except Exception as e:
            self.fail(e)


if __name__ == '__main__':
    unittest.main()
