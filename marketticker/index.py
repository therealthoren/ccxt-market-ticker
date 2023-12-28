import os

from gevent.pywsgi import WSGIServer

from marketticker.factory import CCXTMarketTickerFactory


def main():
    # when in environment "module" is "API" then start the API
    if os.getenv("MODULE") == "API":
        factory = CCXTMarketTickerFactory()
        service = factory.startApiService(os.environ.get("zookeeper_host"),
                                os.environ.get("zookeeper_port"),
                                os.environ.get("zookeeper_path"))

        http_server = WSGIServer(('', 4999), service)
        http_server.serve_forever()
    return None