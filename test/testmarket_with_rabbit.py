import os
import unittest

from marketticker.MQListener import MQListener
from marketticker.Symbol import Symbol
from marketticker.factory import CCXTMarketTickerFactory


class TestMarketWithRabbit(unittest.TestCase):

    def test_watch_with_rabbit(self):
        factory = CCXTMarketTickerFactory()
        factory.installRabbitQueue("localhost", 5672, os.environ.get("rabbit_user"), os.environ.get("rabbit_pwd"))
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

        listener = MQListener("localhost", 5672, os.environ.get("rabbit_user"),os.environ.get("rabbit_pwd"))
        listener.connect()

        listener2 = MQListener("localhost", 5672, os.environ.get("rabbit_user"),os.environ.get("rabbit_pwd"))
        listener2.connect()

        try:
            fetcher = fetchService.createFetcher(Symbol("BTC/USDT"), "1m")

            listener.followMarket("binance", Symbol("BTC/USDT"), "1m", YourListener())
            listener2.followMarket("binance", Symbol("BTC/USDT"), "1m", YourListener2())

            factory.run()
        except Exception as e:
            self.fail(e)


if __name__ == '__main__':
    unittest.main()
