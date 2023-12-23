from marketticker.MQListener import MQListener
from marketticker.Symbol import Symbol

listener = MQListener("localhost", 5672, "test", "test")
listener.connect()


class YourListener:
    def onMarketDataReceived(self, data):
        print("1: " + str(data))

    def onMarketTickerReceived(self, data):
        print("1: " + str(data))

listener.followMarketTicker("binance", Symbol("BTC/USDT"), "1m", YourListener())