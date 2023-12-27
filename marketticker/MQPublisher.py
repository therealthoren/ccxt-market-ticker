import json
import threading
import time
import logging

import amqpstorm
from amqpstorm import Connection
from amqpstorm.basic import Basic

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger()

from marketticker.MarketListener import MarketData


class MQPublisher:
    running = True
    exchange_prefix: str = ""
    max_retries = 10
    def __init__(self, host, port, username, password, exchange_prefix=""):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.exchange_prefix = exchange_prefix
        self._connection = None
        self._stopped = threading.Event()
        self.thread = threading.Thread(target=self.waitForConnection)
        self.thread.start()

    def connect(self):
        pass

    def waitForConnection(self):
        self._stopped.clear()
        if not self._connection or self._connection.is_closed:
            self._create_connection()
        while not self._stopped.is_set():
            try:
                # Check our connection for errors.
                self._connection.check_for_errors()
                if not self._connection.is_open:
                    raise amqpstorm.AMQPConnectionError('connection closed')
            except amqpstorm.AMQPError as why:
                # If an error occurs, re-connect and let update_consumers
                # re-open the channels.
                LOGGER.warning(why)
                self._create_connection()
            time.sleep(1)


    def _create_connection(self):
        """Create a connection.

        :return:
        """
        attempts = 0
        while True:
            attempts += 1
            if self._stopped.is_set():
                break
            try:
                self._connection = Connection(self.host,
                                              self.username,
                                              self.password, heartbeat=10)
                self._channel = self._connection.channel()
                self.createExchanges()
                break
            except amqpstorm.AMQPError as why:
                LOGGER.warning(why)
                if self.max_retries and attempts > self.max_retries:
                    raise Exception('max number of retries reached')
                time.sleep(min(attempts * 2, 30))
            except KeyboardInterrupt:
                break

    def createExchanges(self):
        # create the exchange self.exchange_prefix+"ccxt_market_ticker" when it doesn't exist
        self._channel.exchange.declare(exchange=self.exchange_prefix+"ccxt_market_ticker",
                                       exchange_type='topic', durable=True)
        # create the exchange self.exchange_prefix+"ccxt_market_data" when it doesn't exist
        self._channel.exchange.declare(exchange=self.exchange_prefix+"ccxt_market_data",
                                       exchange_type='topic', durable=True)



    def disconnect(self):
        self.running = False
        self._stopped.set()
        self._connection.close()

    def stop(self):
        self.disconnect()

    def publish(self, exchange, routing_key, message, ttl=None):
        if self.exchange_prefix is not None:
            exchange = self.exchange_prefix + exchange
        # publish the message to the exchange
        # publish it with a ttl of 1 hour

        Basic(self._channel).publish(exchange=exchange, routing_key=routing_key, body=message)

    def publishMarketTicker(self, data: MarketData):
        self.publish("ccxt_market_ticker", data.symbol.exchange+"_"+data.symbol.name+"_"+data.interval, data.json())

    def publishMarketData(self, data: MarketData):
        self.publish("ccxt_market_data", data.symbol.exchange+"_"+data.symbol.name+"_"+data.interval, data.json(), ttl=60*60)