import asyncio
import datetime

from flask import Flask, jsonify, request

from marketticker.AccountDataConsumer import periodInSeconds
from marketticker.ExchangeService import ExchangeService
from marketticker.ZookeeperManager import ZookeeperManager
from flask import Flask


class APIServer():
    zookeeper: ZookeeperManager
    exchanges: {str: ExchangeService} = {}
    def __init__(self, zookeeper, loop=None):
        self.zookeeper = zookeeper
        self._app = self.createRestServer()
        if loop is None:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        self.loop = loop

    def app(self):
        return self._app

    def run(self):
        return self._app.run()

    def getOrCreateExchangeService(self, exchange):
        if exchange in self.exchanges:
            return self.exchanges[exchange]

        edata = self.zookeeper.getExchangeData(exchange)
        if edata is None:
            raise Exception("Exchange not found")
        e = ExchangeService(edata, self.loop)
        self.exchanges[exchange] = e
        return e

    def createRestServer(self):
        """ Create a REST server to handle requests from the frontend with PORT 5000
            get: /exchanges - returns a list of exchanges
            get: /symbol/<exchange> - returns a list of symbols for the exchange
            get: /symbol/<exchange>/<symbol>/<interval>?from=date&to=date - returns the historical data for the symbol
        """
        app = Flask(__name__)

        @app.route('/')
        def index():
            return "API of ccxt-market-ticker is ready!"

        @app.route('/exchanges', methods=['GET'])
        def get_exchanges():
            try:
                exchanges = self.zookeeper.getAllExchanges()
                return jsonify(exchanges)
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @app.route('/symbols/<exchange>', methods=['GET'])
        def get_symbols(exchange):
            try:
                e = self.getOrCreateExchangeService(exchange)
                s = e.getAllSymbols()

                return jsonify(s)
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @app.route('/symbol/<exchange>/<base>/<quote>/<interval>', methods=['GET'])
        def get_symbol(exchange, base, quote, interval):
            try:
                # from date or last 100xinterval
                default_from_date = None
                interval_in_seconds = periodInSeconds(interval)
                default_from_date = datetime.datetime.now() - datetime.timedelta(seconds=100*interval_in_seconds)
                from_date = request.args.get('from') if request.args.get('from') else default_from_date
                to_date = request.args.get('to') or None
                symbol = base + "/" + quote
                e = self.getOrCreateExchangeService(exchange)
                s = e.getHistoricalData(symbol, interval, from_date, to_date)

                return jsonify(s)
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        return app
