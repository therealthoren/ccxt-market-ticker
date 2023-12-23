import unittest

from marketticker.Symbol import Symbol
from marketticker.factory import CCXTMarketTickerFactory


class TestMarketData(unittest.TestCase):

    def test_creation(self):
        factory = CCXTMarketTickerFactory()
        fetchService = factory.createBasicMarketDataManager(
            "binance",
            "",
            ""
        )
        if fetchService is None:
            self.fail("fetchService is None")

        fetcher = None
        class YourListener:
            tickerReceived = False
            dataReceived = False
            def onMarketTickerReceived(self, ticker):
                # get the tickerReceived and dataReceived variables from the outer scope
                self.tickerReceived = True
                if self.dataReceived:
                    fetcher.stop()

            def onMarketDataReceived(self, data):
                self.dataReceived = True
                if self.tickerReceived:
                    fetcher.stop()

        yourListener = YourListener()
        try:
            symbol = Symbol("BTC/USDT")
            fetcher = fetchService.createFetcher(symbol, "1m", yourListener)


            fetcher.wait()
        except Exception as e:
            self.fail(e)



if __name__ == '__main__':
    unittest.main()
