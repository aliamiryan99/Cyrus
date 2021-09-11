
from abc import abstractmethod


class Trailing:

    @abstractmethod
    def on_tick(self, history, entry_point, position_type, time):
        pass

    @abstractmethod
    def on_pre_tick(self):
        pass

    @abstractmethod
    def on_tick_end(self):
        pass

    @abstractmethod
    def on_data(self, history):
        pass
