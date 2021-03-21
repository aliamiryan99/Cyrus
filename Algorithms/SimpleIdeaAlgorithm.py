
from Algorithms.SimpleIdea import SimpleIdea


class SIAlgorithm:

    def __init__(self, symbol, data_history, win_inc, win_dec, shadow_threshold, body_threshold):
        # Data window, moving average window
        self.win_inc = win_inc
        self.win_dec = win_dec
        self.window_size = max(win_inc, win_dec)
        self.symbol = symbol
        self.shadow_threshold = shadow_threshold
        self.body_threshold = body_threshold
        len_window = len(data_history)
        if len_window <= self.window_size:
            raise Exception("window len should be greater than window size")
        self.data_window = data_history[-self.window_size-5:]

    def on_tick(self, candle):
        return 0, 0

    def on_data(self, candle):
        signal = SimpleIdea.simpleIdea(self.symbol, self.data_window, self.win_inc, self.win_dec,
                                       self.shadow_threshold, self.body_threshold)
        self.data_window.pop(0)
        self.data_window.append(candle)
        return signal, self.data_window[-1]['Open']



