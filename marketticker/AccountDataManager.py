from marketticker.AccountDataConsumer import AccountDataConsumer
from marketticker.AccountListener import AccountListener
from marketticker.MarketDataConsumer import MarketDataConsumer
from marketticker.MarketListener import MarketListener
from marketticker.Symbol import Symbol




class AccountDataManager:
    exchange = None
    api_key = None
    publisher = None
    api_secret = None

    def __init__(self, exchange, api_key, api_secret):
        self.exchange = exchange
        self.api_key = api_key
        self.api_secret = api_secret

    def createFetcher(self, accountListener: AccountListener=None):
        c = AccountDataConsumer(self, accountListener)
        c.start()

        return c

    def setRabbitQueuePublisher(self, rabbitQueuePublisher):
        self.publisher = rabbitQueuePublisher