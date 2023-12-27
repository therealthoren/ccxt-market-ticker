from abc import abstractmethod


class ZookeeperListener:
    @abstractmethod
    def on_new_symbol_follow_found(self, symbol_info):
        pass

    @abstractmethod
    def on_new_symbol_follow_lost(self, symbol_info):
        pass