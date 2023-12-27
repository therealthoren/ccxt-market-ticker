import asyncio
import datetime
import importlib
from threading import Thread

import ccxt
import pytz

from marketticker.MarketListener import MarketListener, MarketData
from marketticker.Symbol import Symbol, SymbolType


def convertTimeframesBack(coindeckTf):
    if coindeckTf.endswith("SEC"):
        return coindeckTf.replace("SEC", "s")
    if coindeckTf.endswith("HRS"):
        return coindeckTf.replace("HRS", "h")
    if coindeckTf.endswith("MIN"):
        return coindeckTf.replace("MIN", "m")
    if coindeckTf.endswith("DAY"):
        return coindeckTf.replace("DAY", "d")
    if coindeckTf.endswith("MTH"):
        return coindeckTf.replace("MTH", "M")
    if coindeckTf.endswith("YRS"):
        return coindeckTf.replace("YRS", "Y")

    return coindeckTf

def convertTimeframes(coindeckTf):
    if coindeckTf.endswith("s"):
        return coindeckTf.replace("s", "SEC")
    if coindeckTf.endswith("h"):
        return coindeckTf.replace("h", "HRS")
    if coindeckTf.endswith("m"):
        return coindeckTf.replace("m", "MIN")
    if coindeckTf.endswith("d"):
        return coindeckTf.replace("d", "DAY")
    if coindeckTf.endswith("M"):
        return coindeckTf.replace("M", "MTH")
    if coindeckTf.endswith("Y"):
        return coindeckTf.replace("Y", "YRS")
    if coindeckTf.endswith("y"):
        return coindeckTf.replace("y", "YRS")

    return coindeckTf

def periodInSeconds(period):
    if period.endswith("m"):
        return float(period.replace("m", "")) * 60
    if period.endswith("h"):
        return float(period.replace("h", "")) * 60 * 60
    if period.endswith("d"):
        return float(period.replace("d", "")) * 60 * 60 * 24
    if period.endswith("M"):
        return float(period.replace("M", "")) * 60 * 60 * 24 * 30
    if period.endswith("Y"):
        return float(period.replace("Y", "")) * 60 * 60 * 24 * 365
    return 60

def reconvertContractType(type):
    if type == SymbolType.FUTURES:
        return "futures"
    return "default"


class MarketDataConsumer:
    _is_canceled = False

    def __init__(self, manager, listener: MarketListener, symbol: Symbol, interval, loop=None):
        self._manager = manager
        self._listener = listener
        self._symbol = symbol
        self._interval = interval
        if loop is None:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        self.loop = loop


    def start(self):
        self._exchange = self.generateExchange()
        self._fetch_exchange = self.generateExchange()
        self.apiInfo = self.extractApiInformation()

        self.loop.create_task(self.waitForFinalCandle())
        self.loop.create_task(self.consumeMarketData())


    async def waitForFinalCandle(self):
        # get the current time
        now = datetime.datetime.now(pytz.utc)
        # get the current time in milliseconds
        now = int(now.timestamp() * 1000)
        lastCandleTime = None
        lastTimestamp = now
        while True:
            if self._is_canceled:
                return
            await asyncio.sleep(1)

            # get the current time
            now = datetime.datetime.now(pytz.utc)
            # get the current time in milliseconds
            now = int(now.timestamp() * 1000)

            # calculate the next candle time based on the current time
            # and the interval
            intervalInSeconds = periodInSeconds(self._interval)
            nextCandleTime = (now - (now % (intervalInSeconds * 1000))) + intervalInSeconds * 1000

            if lastCandleTime is None:
                lastCandleTime = nextCandleTime

            # here we want to calculate if we have reached the next candle
            # if so, we want to send the last candle to the listener
            # and reset the last candle
            if lastCandleTime is not None and lastCandleTime != nextCandleTime:
                candle = await self._fetch_exchange.fetch_ohlcv(self._symbol.name, self._interval, limit=2)
                data = MarketData()
                data.symbol = self._symbol
                data.timeframe = convertTimeframesBack(self._interval)
                data.interval = self._interval
                data.exchange = self._symbol.exchange
                data.timestamp = candle[0][0]
                data.open = candle[0][1]
                data.final = True
                data.high = candle[0][2]
                data.low = candle[0][3]
                data.close = candle[0][4]
                data.volume = candle[0][5]


                data.symbol = self._symbol
                data.interval = self._interval
                data.exchange = self._symbol.exchange
                # we have reached the next candle
                # send the last candle to the listener
                # and reset the last candle
                # check if onMarketDataReceived is implemented
                try:
                    if "onMarketDataReceived" in dir(self._listener):
                        self._listener.onMarketDataReceived(data)
                except Exception as e:
                    print("Error in onMarketDataReceived: " + str(e))
                    pass

                lastCandleTime = nextCandleTime



    def wait(self):
        return self._thread.join()

    def cancel(self):
        self._is_canceled = True

    def stop(self):
        self.cancel()

    def extractApiInformation(self):
        self._markets = self._exchange.load_markets()
        self._fetch_exchange.load_markets()


    def generateExchange(self):

        #exc = getattr(ccxt.pro, self._symbol.exchange)
        cxtpro = importlib.import_module("ccxt.pro." + self._symbol.exchange.lower())
        exc = getattr(cxtpro, self._symbol.exchange)
        if type == SymbolType.FUTURES:
            exchange = exc({
                'apiKey': self._manager.api_key,
                'secret': self._manager.api_secret,
                'adjustForTimeDifference': True,
                'options': {
                        'defaultType': reconvertContractType(type),
                        'adjustForTimeDifference': True,
                    }})
        else:
            exchange = exc({
                'apiKey': self._manager.api_key,
                'secret': self._manager.api_secret,
                'adjustForTimeDifference': True,
                'options': {
                    'adjustForTimeDifference': True,
                }
            })

        return exchange

    def _canceled(self):
        return self._is_canceled

    def consumeMarketDataLoop(self):


        self.loop.create_task(self.consumeMarketData())

    async def consumeMarketData(self):

        exchange = self._exchange
        lastTimestamp = 0
        lastSendData = 0

        while not self._canceled():
            # this can be any call instead of fetch_ticker, really
            try:

                allticker = await exchange.watch_ohlcv(self._symbol.name,self._interval)
                ticker = allticker[0]
                timestamp = datetime.datetime.fromtimestamp(ticker[0]/1000, tz=datetime.timezone.utc)
                t = MarketData()
                t.open = ticker[1]
                t.high = ticker[2]
                t.low = ticker[3]
                t.close = ticker[4]
                t.volume = ticker[5]
                t.last = ticker[4]

                t.trades = -1
                t.final = False
                t.closeTime = datetime.datetime.strftime(timestamp, "%Y-%m-%dT%H:%M:%S.%f%Z")
                t.datetime = datetime.datetime.strftime(datetime.datetime.now(pytz.utc), "%Y-%m-%dT%H:%M:%S.%f%Z")



                t.symbol = self._symbol
                t.interval = self._interval
                t.exchange = self._symbol.exchange

                t.final = False
                try:
                    self._listener.onMarketTickerReceived(t)
                except Exception as e:
                    print("Error in onMarketTickerReceived: " + str(e))
                    pass

            except ccxt.RequestTimeout as e:
                print('[' + type(e).__name__ + ']')
                print(str(e)[0:200])
                # will retry
            except ccxt.DDoSProtection as e:
                print('[' + type(e).__name__ + ']')
                print(str(e.args)[0:200])
                # will retry
            except ccxt.ExchangeNotAvailable as e:
                print('[' + type(e).__name__ + ']')
                print(str(e.args)[0:200])
                # will retry
            except ccxt.ExchangeError as e:
                print('[' + type(e).__name__ + ']')
                print(str(e)[0:200])
                break  # won't retry
            except Exception as e:
                print(e)
                break

