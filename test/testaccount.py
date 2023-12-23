import unittest

from marketticker.Symbol import Symbol
from marketticker.factory import CCXTMarketTickerFactory


class TestAccountData(unittest.TestCase):

    def test_watch_account_data(self):
        factory = CCXTMarketTickerFactory()
        fetchService = factory.createAccountDataManager(
            "binance",
            "",
            ""
        )
        if fetchService is None:
            self.fail("fetchService is None")

        fetcher = None
        class YourListener:
            def onAccountBalanceReceived(self, data):
                print(data)
                fetcher.stop()

            def onTradesReceived(self, data):
                print(data)
                fetcher.stop()

            def onPositionsReceived(self, data):
                print(data)
                fetcher.stop()

        try:
            fetcher = fetchService.createFetcher(YourListener())

            fetcher.wait()
        except Exception as e:
            self.fail(e)


if __name__ == '__main__':
    unittest.main()
