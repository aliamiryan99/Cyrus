
from Algorithms.MinMaxTrend import MinMaxPredict


class MinMaxAlgorithm:

    def __init__(self, symbol, data_history, window_exteremum, window_trend, mode_trend):
        # Data window, moving average window
        self.symbol = symbol
        self.window_extermum = window_exteremum
        self.window_trend = window_trend
        self.mode_trend = mode_trend
        self.data_window = data_history

    def on_tick(self, candle):
        return 0, 0

    def on_data(self, candle):
        signal = 0
        if candle['Volume'] != 0:
            signal = MinMaxPredict.predict(self.data_window, self.window_extermum, self.window_trend, self.mode_trend)
            self.data_window.pop(0)
            self.data_window.append(candle)
        return signal, self.data_window[-1]['Open']

