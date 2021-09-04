from abc import abstractmethod
from Market.Market import Market


class Strategy:

    def __init__(self, market: Market):
        self.market = market

    @abstractmethod
    def on_tick(self):
        pass

    @abstractmethod
    def on_data(self):
        pass
