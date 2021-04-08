
from Algorithms.SimpleTrendLineBreak import SimpleTrendLineBreak


class SimpleTrendLineBreakAlgorithm:

    def __init__(self, data_history, window_size):
        # Data window, moving average window
        self.window_size = window_size
        len_window = len(data_history)
        if len_window <= self.window_size:
            raise Exception("window len should be greater than window size")
        self.data_window = data_history[-self.window_size-5:]
        self.trend_detection = 0
        self.line_value = 0
        self.is_buy_trade = False
        self.is_sell_trade = False

    def on_tick(self):
        if self.trend_detection == 1 and not self.is_buy_trade:
            if self.data_window[-1]['Low'] < self.line_value and self.data_window[-1]['Close'] >= self.data_window[-1]['Open']:
                self.is_buy_trade = True
                return 1, self.data_window[-1]['Open']
        elif self.trend_detection == -1 and not self.is_sell_trade:
            if self.data_window[-1]['High'] > self.line_value and self.data_window[-1]['Close'] <= self.data_window[-1]['Open']:
                self.is_sell_trade = True
                return -1, self.data_window[-1]['Open']
        return 0, 0

    def on_data(self, candle):
        self.trend_detection = SimpleTrendLineBreak.simple_trend_detect(self.data_window)
        if self.trend_detection == 1:
            self.line_value = SimpleTrendLineBreak.get_ascending_line_value(self.data_window)
        elif self.trend_detection == -1:
            self.line_value = SimpleTrendLineBreak.get_descending_line_value(self.data_window)
        self.is_buy_trade = False
        self.is_sell_trade = False
        self.data_window.pop(0)
        self.data_window.append(candle)
        return 0, 0

