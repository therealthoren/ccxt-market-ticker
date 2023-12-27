ccxt-market-ticker

---

Docker: https://hub.docker.com/r/donnercody/ccxt-market-ticker

```bash 
docker pull donnercody/ccxt-market-ticker
```


---

pyPi: https://pypi.org/project/ccxt-market-ticker/

This library can be used to use the ccxt library to get the ticker of all markets of an exchange.
The library also provides a function to get the ticker of all markets of all exchanges 
with MQListener and MQPublisher.

MQListener Example:

```python
from marketticker.MQListener import MQListener
from marketticker.Symbol import Symbol

listener = MQListener("localhost", 5672, "test", "test")
listener.connect()


class YourListener:
    def onMarketDataReceived(self, data):
        print("1: " + str(data))

    def onMarketTickerReceived(self, data):
        print("1: " + str(data))


listener.followMarket("binance", Symbol("BTC/USDT"), "1m", YourListener())
```



