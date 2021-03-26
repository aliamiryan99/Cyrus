"""
class MAAlgorithm:
    methods:
        algorithm_init(data_history, window_size, ma_type)  # data_hitory should be greater than window size,
         price_type should be "open" or "high" or "low" or "close", ma_type should be "ema" or "sma" or "wma"
        on_data(candle)
"""


from ta.trend import ema_indicator
from ta.trend import sma_indicator
from ta.trend import wma_indicator
import pandas as pd


class MAAlgorithm:

    def __init__(self, symbol, data_history, window_size1, window_size2, price_type, ma_type):
        # Open, High, Low, Close
        self.symbol = symbol
        self.price_type = price_type

        # EMA, SMA, WMA
        if ma_type == "EMA":
            self.ma_indicator = ema_indicator
        elif ma_type == "SMA":
            self.ma_indicator = sma_indicator
        elif ma_type == "WMA":
            self.ma_indicator = wma_indicator
        else:
            raise Exception("moving average type doesn't exist")

        # Data window, moving average window
        self.window_size1 = window_size1
        self.window_size2 = window_size2
        self.window_size = max(window_size1, window_size2)
        len_window = len(data_history[price_type])
        if len_window <= window_size1 or len_window <= window_size2:
            raise Exception("window len should be greater than window size")
        self.data_window = data_history[price_type][len_window-self.window_size:len_window].to_list()
        self.ma_old1 = self.ma_indicator(data_history[price_type], window_size1).to_list()[-1]
        self.ma_old2 = self.ma_indicator(data_history[price_type], window_size2).to_list()[-1]

    def on_tick(self):
        return 0, 0

    def on_data(self, candle):
        self.data_window.pop(0)
        self.data_window.append(candle[self.price_type])
        ma_new1 = self.ma_indicator(pd.Series(self.data_window), self.window_size1).to_list()[-1]
        ma_new2 = self.ma_indicator(pd.Series(self.data_window), self.window_size2).to_list()[-1]
        signal = 0
        if self.ma_old1 < self.ma_old2 and ma_new1 > ma_new2:
            signal = 1
        elif self.ma_old1 > self.ma_old2 and ma_new1 < ma_new2:
            signal = -1
        self.ma_old1 = ma_new1
        self.ma_old2 = ma_new2
        return signal, self.data_window[-1]['Close']

