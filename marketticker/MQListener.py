import json
import random
import threading
import time
import logging

import amqpstorm
from amqpstorm import Connection
from amqpstorm.basic import Basic

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger()

from marketticker import MarketListener, AccountListener, Symbol
from marketticker.MarketListener import MarketData


class Consumer(object):
    def __init__(self, target, sub_id, exchange, listener):
        self.exchange = exchange
        self.listener = listener
        self.target = target
        # random id
        self._id = str(time.time()) + str(random.random()*1000)
        self.sub_id = sub_id
        self.channel = None
        self.active = False

    def id(self):
        return self._id

    def start(self, connection):
        self.channel = None
        try:
            self.channel = connection.channel()
            self.channel.basic.qos(1)
            queue = None
            while not queue:
                queue = self.channel.queue.declare("", auto_delete=True)
                time.sleep(0.1)
            self.active = True
            self.queue = queue["queue"]
            self.channel.queue.bind(exchange=self.exchange,
                                    routing_key=self.target,
                                    queue=self.queue)

            self.channel.basic.consume(self, self.queue, no_ack=False)
            self.channel.start_consuming()
            if not self.channel.consumer_tags:
                # Only close the channel if there is nothing consuming.
                # This is to allow messages that are still being processed
                # in __call__ to finish processing.
                self.channel.close()
        except amqpstorm.AMQPError as e:
            print("Error in Consumer.start", e)
        finally:
            self.active = False

    def stop(self):
        if self.channel:
            self.channel.stop_consuming()
            self.channel.close()

    def __call__(self, message):
        """Process the Payload.

        :param Message message:
        :return:
        """
        try:
            message.ack()
            if self.listener is not None:
                self.listener(message.body)
        except Exception as e:
            print("Error in Consumer.__call__", e)
            return


class MQListener:
    """"
    This Listener connects to a specific "exchange" and fetches all
    messages from the queue. The messages are then passed to the MarketListener callback class
    The queue is created if it doesn't exist yet named by the symbol name and interval.
    """
    first_connection = True
    consuming_started = False
    _consumers = {}
    max_retries = 10

    def __init__(self, host, port, username, password, exchange_prefix=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.exchange_prefix = exchange_prefix
        self._connection = None
        self._stopped = threading.Event()

    def connect(self):
        self.thread = threading.Thread(target=self.waitForConnection)
        self.thread.start()

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
                self.reconnectAllConsumers()
                break
            except amqpstorm.AMQPError as why:
                LOGGER.warning(why)
                if self.max_retries and attempts > self.max_retries:
                    raise Exception('max number of retries reached')
                time.sleep(min(attempts * 2, 30))
            except KeyboardInterrupt:
                break

    def reconnectAllConsumers(self):
        if self.first_connection:
            self.first_connection = False
            return
        for consumer in self._consumers.values():
            try:
                if consumer.active:
                    consumer.stop()
            except Exception:
                pass
            try:
                self._start_consumer(consumer)
            except Exception:
                pass

    def disconnect(self):
        self.running = False
        self._stopped.set()
        self._connection.close()

    def stop_consumer(self, consumer):
        """Stop a specific consumer
        :param consumer:
        :return:
        """
        if consumer.id() not in self._consumers:
            raise Exception('Consumer does not exist')
        self._consumers[consumer.id()].stop()
        del self._consumers[consumer.id()]

    def _start_consumer(self, consumer):
        """Start a consumer as a new Thread.

        :param Consumer consumer:
        :return:
        """
        thread = threading.Thread(target=consumer.start,
                                  args=(self._connection,))
        thread.daemon = True
        thread.start()


    def stop(self):
        self.disconnect()

    def waitUntilConnectionOpened(self):
        while not self._connection or not self._connection.is_open:
            time.sleep(1)

    def followMarket(self, brokerExchange :str, symbol: Symbol, interval,
                     market_listener: MarketListener):
        self.waitUntilConnectionOpened()
        id = brokerExchange + "_" + symbol.name + "_" + interval
        if id in self._consumers:
            return self._consumers[id+"_ticker"]

        if self.exchange_prefix is not None:
            exchange = self.exchange_prefix + "ccxt_market_ticker"
        else:
            exchange = "ccxt_market_ticker"

        c = Consumer(id, "_ticker", exchange,
                     lambda data: market_listener.onMarketTickerReceived(MarketData.from_json(data)))
        self._consumers[c.id()] = c
        self._start_consumer(c)

        if self.exchange_prefix is not None:
            exchange = self.exchange_prefix + "ccxt_market_data"
        else:
            exchange = "ccxt_market_data"
        c = Consumer(id, "_data", exchange, lambda data: market_listener.onMarketDataReceived(MarketData.from_json(data)))
        self._consumers[c.id()] = c
        self._start_consumer(c)
        print(self._consumers)