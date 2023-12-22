
import abc

class AccountListener(abc.ABC):
    @abc.abstractmethod
    def onAccountBalanceReceived(self, data):
        raise NotImplementedError

    @abc.abstractmethod
    def onTradesReceived(self, data):
        raise NotImplementedError

    def onPositionsReceived(self, data):
        raise NotImplementedError
