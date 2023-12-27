import json
import random
import time
from threading import Thread, Timer

from kazoo.client import KazooClient
from kazoo.protocol.states import EventType
from kazoo.retry import KazooRetry

from marketticker.ThreadJob import ThreadJob
from marketticker.ZookeeperListener import ZookeeperListener


class ZookeeperManager:
    symbol_watchers = {}
    registration_running = False

    def __init__(self, host, port, path, callbackClass: ZookeeperListener):
        self.host = host
        self.port = port
        self.path = path
        self.callbackClass = callbackClass

    def start(self, factory):

        zkr = KazooRetry(max_tries=-1)
        self.zk = KazooClient(hosts=self.host + ':' + str(self.port), connection_retry=zkr)
        self.zk.start()
        self.zk.ensure_path(self.path)
        self.running = True
        self.thread = ThreadJob(self.runKarooChildrenWatcher, 30+(random.random()*30))
        self.runKarooChildrenWatcher()
        self.thread.start()

        # create a async python timer that runs every 2 minutes and calls "runKarooChildrenWatcher"
        self.consumerTimer = ThreadJob(self.runConsumerRegistration, 10)
        self.consumerTimerEvent = self.consumerTimer.start()

    def runConsumerRegistration(self):
        to_delete = []
        for sk in self.symbol_watchers:
            try:
                self.registerConsumer(self.symbol_watchers[sk])
                ttl = self.symbol_watchers[sk]["ttl"]
                if ttl is not None:
                    if time.time() - self.symbol_watchers[sk]["ttl"] > 20:
                        to_delete.append(sk)
            except Exception as e:
                print("ZookeeperManager: runConsumerRegistration: exception: " + str(e))
                continue

        for sk in to_delete:
            del self.symbol_watchers[sk]

    def registerConsumer(self, symbol_watchers):
        self.registration_running = True
        exchange = symbol_watchers["exchange"]
        symboldir = symbol_watchers["symboldir"]
        path = self.path + "/broker/" + exchange + "/" + symboldir + "/" + "consumer"
        symbol_watchers["last_timestamp"] = time.time()
        symbol_watchers["ttl"] = time.time()
        symbol_watchers["symbol"] = symbol_watchers["name"]
        if self.zk.exists(path):
            self.zk.set(path, value=json.dumps(symbol_watchers).encode("UTF-8"))
        else:
            self.zk.create(path, value=json.dumps(symbol_watchers).encode("UTF-8"), ephemeral=True)
        self.symbol_watchers[symbol_watchers["exchange"] + "_" + symbol_watchers["symboldir"]] = symbol_watchers
        self.registration_running = False

    def getRecursiveChildren(self, path):
        data = {}
        children = self.zk.get_children(path, include_data=True)
        for child in children[0]:
            try:
                node_content = self.zk.get(path + "/" + child)
                data[child] = {}
                if node_content[0] is not None and len(node_content[0]) > 0:
                    try:
                        data[child]["data"] = json.loads(node_content[0].decode('utf-8'))
                    except Exception as e:
                        print("ZookeeperManager: getRecursiveChildren: exception: " + str(e))
                data[child]["children"] = self.getRecursiveChildren(path+"/"+child)
            except Exception as e:
                print("ZookeeperManager: getRecursiveChildren: exception: " + str(e))

        return data

    def getSymbolDir(self, symbol):
        return symbol.replace("/", "").upper()

    def getWatcher(self, exchange, symbol):
        symbol = self.getSymbolDir(symbol)
        for e in self.symbol_watchers:
            if self.symbol_watchers[e]["exchange"] == exchange and self.symbol_watchers[e]["symboldir"] == symbol:
                return self.symbol_watchers[e]
        return None

    def registerDataReceivedForSymbol(self, exchange, symbol, interval):
        watcher = self.getWatcher(exchange, symbol)
        if watcher is None:
            raise Exception("Symbol not found: " + exchange + " " + symbol)
        watcher["ttl"] = time.time()


    def runKarooChildrenWatcher(self):

            brokerTree = self.getRecursiveChildren(self.path+"/broker")

            self.onBrokerTreeReceived(brokerTree)


    def has_symbol_consumer(self, symbol):
        if len(symbol["children"]) <= 0:
            return False

        if "consumer" in symbol["children"]:
            data = symbol["children"]["consumer"]["data"]
            if "last_timestamp" in data:
                time_diff = time.time() - data["last_timestamp"]
                if time_diff < 30:
                    return True

        return False

    def onBrokerTreeReceived(self, data):
        for exchange in data:
            dataInfo = data[exchange]["data"]
            for symboldir in data[exchange]["children"]:
                symbol = data[exchange]["children"][symboldir]
                if not self.has_symbol_consumer(symbol):
                    newSymbol = {
                        "exchange": exchange,
                        "symboldir": symboldir
                    }
                    newSymbol.update(symbol["data"])
                    self.callbackClass.on_new_symbol_follow_found(newSymbol)
                    break


    def wait(self):
       self.thread.join()

    def close(self):
        self.zk.stop()
        self.zk.close()
        self.consumerTimer.cancel()
        self.thread.cancel()