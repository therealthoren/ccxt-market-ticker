import os
import unittest

from marketticker.Symbol import Symbol
from marketticker.factory import CCXTMarketTickerFactory
from gevent.pywsgi import WSGIServer


class TestAPI(unittest.TestCase):

    def test_creation(self):
        factory = CCXTMarketTickerFactory()

        try:
            service = factory.startApiService(os.environ.get("zookeeper_host"),
                                                               os.environ.get("zookeeper_port"),
                                                               os.environ.get("zookeeper_path"))


            service.run(port=4999)
        except Exception as e:
            self.fail(e)



if __name__ == '__main__':
    unittest.main()
