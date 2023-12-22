import threading

import pika

from marketticker import MarketListener, AccountListener, Symbol
from marketticker.MarketListener import MarketData


class RabbitMQListener:
    """"
    This Listener connects to a specific "exchange" and fetches all
    messages from the queue. The messages are then passed to the MarketListener callback class
    The queue is created if it doesn't exist yet named by the symbol name and interval.
    """
    market_listeners = {}
    consuming_started = False

    def __init__(self, host, port, username, password, exchange_prefix=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.exchange_prefix = exchange_prefix
        self.connection = None
        self.channel = None
        self.market_listeners = {}

    def connect(self):
        credentials = pika.PlainCredentials(self.username, self.password)
        parameters = pika.ConnectionParameters(self.host, self.port, '/', credentials)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()


    def disconnect(self):
        self.connection.close()

    def followMarketTicker(self, brokerExchange :str, symbol: Symbol, interval, market_listener: MarketListener):
        if brokerExchange+"_"+symbol.name+"_"+interval not in self.market_listeners:
            self.market_listeners[brokerExchange+"_"+symbol.name+"_"+interval] = []
        self.market_listeners[brokerExchange + "_" + symbol.name + "_" + interval].append(market_listener)
        if len(self.market_listeners[brokerExchange+"_"+symbol.name+"_"+interval]) > 1:
            return
        if self.connection is None:
            self.connect()


        if self.exchange_prefix is not None:
            exchange = self.exchange_prefix + "ccxt_market_ticker"
        else:
            exchange = "ccxt_market_ticker"
        # declare a queue without a automatic name
        queue = self.channel.queue_declare(queue="", exclusive=True).method.queue

        # bind the queue self.exchange_prefix+"ccxt_market_ticker" to the exchange self.exchange_prefix+"ccxt_market_ticker" for all routing keys
        self.channel.queue_bind(exchange=exchange, queue=queue, routing_key=brokerExchange+"_"+symbol.name+"_"+interval)

        # start consuming the queue
        self.channel.basic_consume(queue=queue, on_message_callback=self.onMessage, auto_ack=True)
        # start consuming the queue in a separate thread
        self.start_consuming()

    def start_consuming(self):
        # when not already consuming, start consuming the queue
        if not self.consuming_started:
            thread = threading.Thread(target=self.channel.start_consuming)
            thread.start()
            self.consuming_started = True

    def onMessage(self, channel, method, properties, body):
        # parse the message body as json
        # call the onMarketTickerReceived method of the MarketListener
        # pass the parsed json as MarketData object
        data = MarketData.from_json(body)

        for listener in self.market_listeners[method.routing_key]:
            listener.onMarketTickerReceived(data)