
from Algorithms.RefinementOfSimpleIdea import RefinementSI


class RSIAlgorithm:

    def __init__(self, symbol, data_history, win_inc, win_dec, pivot):
        # Data window, moving average window
        self.win_inc = win_inc
        self.win_dec = win_dec
        self.window_size = max(win_inc, win_dec)
        self.symbol = symbol
        self.pivot = pivot
        self.signal_triggered = False
        len_window = len(data_history)
        if len_window <= self.window_size:
            raise Exception("window len should be greater than window size")
        self.data_window = data_history[-self.window_size-5:]

    def on_tick(self):
        signal, price = 0, 0
        if not self.signal_triggered:
            signal, price = RefinementSI.refinement_si(self.data_window, self.win_inc, self.win_dec, self.pivot)
            if signal != 0:
                self.signal_triggered = True
        return signal, price

    def on_data(self, candle):
        self.data_window.pop(0)
        self.data_window.append(candle)
        self.signal_triggered = False
        signal, price = RefinementSI.refinement_si(self.data_window, self.win_inc, self.win_dec, self.pivot)
        if signal != 0:
            self.signal_triggered = True
        return signal, price



