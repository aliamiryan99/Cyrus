
from abc import abstractmethod


class Algorithm:

    @abstractmethod
    def on_tick(self):
        pass

    @abstractmethod
    def on_data(self, candle, equity):
        pass