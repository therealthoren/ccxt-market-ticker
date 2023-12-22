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


class AccountDataConsumer:
    _is_canceled = False

    def __init__(self, manager, listener: MarketListener):
        self._manager = manager
        self._listener = listener


    def start(self):
        self._exchange = self.generateExchange()

        # start a Thread for "consumeMarketData" so that it runs async
        self._thread = Thread(target=self.consumeAccountDataLoop, args=(), daemon=True)
        self._thread.start()

        return self._thread

    def wait(self):
        return self._thread.join()

    def cancel(self):
        self._is_canceled = True

    def stop(self):
        self.cancel()

    def generateExchange(self):

        #exc = getattr(ccxt.pro, self._symbol.exchange)
        cxtpro = importlib.import_module("ccxt.pro." + self._manager.exchange.lower())
        exc = getattr(cxtpro, self._manager.exchange)
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

    def consumeAccountDataLoop(self):

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.loop.run_until_complete(self.consumAccountData())

    def convertAccountData(self, allticker):
        accountData = {}

        for key in allticker.keys():
            try:
                if key == "info":
                    continue

                if key == "timestamp":
                    accountData["timestamp"] = allticker[key]
                elif key == "datetime":
                    accountData["datetime"] = allticker[key]
                elif key == "total":
                    accountData["total"] = allticker[key]
                elif key == "free":
                    accountData["free"] = allticker[key]
                elif key == "used":
                    accountData["used"] = allticker[key]
                elif "free" in allticker[key]:
                    accountData[key] = {}
                    accountData[key]["free"] = allticker[key]["free"]
                    accountData[key]["used"] = allticker[key]["used"]
                    accountData[key]["total"] = allticker[key]["total"]
            except:
                pass

        return accountData

    async def consumAccountData(self):

        exchange = self._exchange
        lastTimestamp = 0
        lastSendData = 0

        while not self._canceled():
            # this can be any call instead of fetch_ticker, really
            try:

                allticker = await exchange.watch_balance()

                account = self.convertAccountData(allticker)

                self._listener.onAccountData(account)

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

