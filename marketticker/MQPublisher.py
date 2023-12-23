import json
import pika

from marketticker.MarketListener import MarketData


class RabbitQueuePublisher:
    exchange_prefix: str = ""
    def __init__(self, host, port, username, password, exchange_prefix=""):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.exchange_prefix = exchange_prefix
        self.connection = None
        self.channel = None

    def connect(self):
        credentials = pika.PlainCredentials(self.username, self.password)
        parameters = pika.ConnectionParameters(self.host, self.port, '/', credentials)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        self.createExchanges()

    def createExchanges(self):
        # create the exchange self.exchange_prefix+"ccxt_market_ticker" when it doesn't exist
        self.channel.exchange_declare(exchange=self.exchange_prefix+"ccxt_market_ticker", exchange_type='topic', durable=True)
        # create the exchange self.exchange_prefix+"ccxt_market_data" when it doesn't exist
        self.channel.exchange_declare(exchange=self.exchange_prefix+"ccxt_market_data", exchange_type='topic', durable=True)



    def disconnect(self):
        self.connection.close()

    def publish(self, exchange, routing_key, message, ttl=None):
        if self.connection is None:
            self.connect()
        if self.exchange_prefix is not None:
            exchange = self.exchange_prefix + exchange
        # publish the message to the exchange
        # publish it with a ttl of 1 hour

        self.channel.basic_publish(exchange=exchange, routing_key=routing_key, body=message, properties=pika.BasicProperties(expiration=str(ttl*1000) if ttl is not None else None))

    def publishMarketTicker(self, data: MarketData):
        self.publish("ccxt_market_ticker", data.symbol.exchange+"_"+data.symbol.name+"_"+data.interval, data.json())

    def publishMarketData(self, data: MarketData):
        self.publish("ccxt_market_data", data.symbol.exchange+"_"+data.symbol.name+"_"+data.interval, data.json(), ttl=60*60)