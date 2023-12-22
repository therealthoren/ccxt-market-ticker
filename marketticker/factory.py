from marketticker.AccountDataManager import AccountDataManager
from marketticker.MarketDataManager import MarketDataManager
from marketticker.RabbitQueuePublisher import RabbitQueuePublisher


class CCXTMarketTickerFactory:
    rabbitQueuePublisher = None

    def installRabbitQueue(self, host, port, username, password, exchange_prefix=""):
        self.rabbitQueuePublisher = RabbitQueuePublisher(host, port, username, password, exchange_prefix)
        self.rabbitQueuePublisher.connect()

    def createBasicMarketDataManager(self, exchange, api_key, api_secret):
        m = MarketDataManager(exchange, api_key, api_secret)
        if self.rabbitQueuePublisher is not None:
            m.setRabbitQueuePublisher(self.rabbitQueuePublisher)
        return m

    def createAccountDataManager(self, param, param1, param2):
        a = AccountDataManager(param, param1, param2)
        if self.rabbitQueuePublisher is not None:
            a.setRabbitQueuePublisher(self.rabbitQueuePublisher)
        return a

    def startMarketDataZookeeperListener(self, zookeeperHost, zookeeperPort, zookeeperPath, marketDataManager):
        pass