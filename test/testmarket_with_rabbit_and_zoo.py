import os
import unittest

from marketticker.MQListener import MQListener
from marketticker.Symbol import Symbol
from marketticker.factory import CCXTMarketTickerFactory


class TestMarketWithRabbitAndZoo(unittest.TestCase):

    def test_watch_with_rabbit_and_zoo(self):
        factory = CCXTMarketTickerFactory()
        factory.installRabbitQueue("localhost", 5672, os.environ.get("rabbit_user"), os.environ.get("rabbit_pwd"))


        class YourListener2:
            def onMarketDataReceived(self, data):
                print("2: "+str(data))

            def onMarketTickerReceived(self, data):
                print("2: "+str(data))

        listener = MQListener(os.environ.get("rabbit_host"), int(os.environ.get("rabbit_port")), os.environ.get("rabbit_user"),os.environ.get("rabbit_pwd"))
        listener.connect()

        try:

            fetcher = factory.startMarketDataZookeeperListener(os.environ.get("zookeeper_host"),
                                                               os.environ.get("zookeeper_port"),
                                                               os.environ.get("zookeeper_path"),
                                                     YourListener2())

            listener.followMarket("binance", Symbol("ETH/USDT"), "1m", YourListener2())

            factory.run()
        except Exception as e:
            self.fail(e)


if __name__ == '__main__':
    unittest.main()
