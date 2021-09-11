
from AlgorithmFactory.AlgorithmsOfExit.Trailings.Trailing import Trailing


class ReverseSignalTrailing(Trailing):

    def __init__(self, algorithm):
        self.algorithm = algorithm

        self.signal = 0

    def on_data(self, history):
        signal, price = self.algorithm.on_data(history[-1], 0)
        if signal != 0:
            self.signal, self.price = signal, price

    def on_pre_tick(self):
        signal, price = self.algorithm.on_tick()
        if signal != 0:
            self.signal, self.price = signal, price

    def on_tick(self, history, entry_point, position_type, time):
        if position_type == 'Buy':
            if self.signal == -1:
                return True, self.price
        elif position_type == 'Sell':
            if self.signal == 1:
                return True, self.price
        return False, 0

    def on_tick_end(self):
        pass
