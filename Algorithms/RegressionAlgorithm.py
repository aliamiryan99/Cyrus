
from Algorithms.RegressionLine import RegressionPredict


class RegressionAlgorithm:

    def __init__(self, symbol, data_history, alpha, beta, window_exteremum):
        # Data window, moving average window
        self.symbol = symbol
        self.alpha = alpha
        self.beta = beta
        self.window_extermum = window_exteremum
        self.data_window = data_history

    def on_tick(self):
        return 0, 0

    def on_data(self, candle, cash):
        signal = 0
        if candle['Volume'] != 0:
            signal = RegressionPredict.predict(self.data_window, self.alpha, self.beta, self.window_extermum)
            self.data_window.pop(0)
            self.data_window.append(candle)
        return signal, self.data_window[-1]['Open']

