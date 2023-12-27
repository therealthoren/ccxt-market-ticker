from marketticker.AccountDataManager import AccountDataManager
from marketticker.MarketDataManager import MarketDataManager
from marketticker.MQPublisher import MQPublisher
from marketticker.MarketListener import MarketListener
from marketticker.Symbol import Symbol
from marketticker.ZookeeperListener import ZookeeperListener
import asyncio
from marketticker.ZookeeperManager import ZookeeperManager

class CCXTMarketTickerFactory(ZookeeperListener, MarketListener):
    rabbitQueuePublisher = None
    fetcher : {str: MarketDataManager} = {}
    loop = None

    def __init__(self, loop=None):
        if loop is None:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        self.loop = loop

    def on_new_symbol_follow_found(self, symbol_info):

        self.z.registerConsumer(symbol_info)
        if symbol_info["exchange"] not in self.fetcher:
            self.fetcher[symbol_info["exchange"]] = self.createBasicMarketDataManager(symbol_info["exchange"],
                                                                                      symbol_info["api_key"] if "api_key" in symbol_info else None,
                                                                                      symbol_info["api_secret"] if "api_secret" in symbol_info else None)
        # when symbol_info["interval"] is not an array, we convert it to an array
        if not isinstance(symbol_info["interval"], list):
            symbol_info["interval"] = [symbol_info["interval"]]
        for interval in symbol_info["interval"]:
            self.fetcher[symbol_info["exchange"]].\
                createFetcher(Symbol(symbol_info["symbol"],
                               type=Symbol.typeFromStr(symbol_info["type"]),
                               exchange=symbol_info["exchange"]), interval=interval, marketListener=self)

    def on_new_symbol_follow_lost(self, symbol_info):
        pass

    def onMarketDataReceived(self, data):
        pass

    def onMarketTickerReceived(self, data):
        symbol = data.symbol
        print("Ticker: "+str(data))
        self.z.registerDataReceivedForSymbol(symbol.exchange, symbol.name, data.interval)


    def installRabbitQueue(self, host, port, username, password, exchange_prefix=""):
        self.rabbit_host = host
        self.rabbit_port = port
        self.rabbit_username = username
        self.rabbit_password = password
        self.rabbit_exchange_prefix = exchange_prefix


    def createBasicMarketDataManager(self, exchange, api_key, api_secret):
        m = MarketDataManager(exchange, api_key, api_secret, self.loop)
        if self.rabbit_host is not None:
            publisher = MQPublisher(self.rabbit_host, self.rabbit_port,
                                    self.rabbit_username, self.rabbit_password, self.rabbit_exchange_prefix)
            publisher.connect()
            m.setRabbitQueuePublisher(publisher)
        return m

    def createAccountDataManager(self, param, param1, param2):
        a = AccountDataManager(param, param1, param2, self.loop)
        if self.rabbit_host is not None:
            publisher = MQPublisher(self.rabbit_host, self.rabbit_port,
                                    self.rabbit_username, self.rabbit_password, self.rabbit_exchange_prefix)
            publisher.connect()
            a.setRabbitQueuePublisher(publisher)
        return a

    def startMarketDataZookeeperListener(self, zookeeperHost, zookeeperPort,
                                         zookeeperPath, marketListener: MarketListener):
        self.marketListener = marketListener

        self.z = ZookeeperManager(zookeeperHost, zookeeperPort, zookeeperPath, self)
        self.z.start(self)
        return self.z

    def run(self):
        self.loop.run_forever()