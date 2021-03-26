
from Algorithms.Divergence import Divergence
from AlgorithmTools import LocalExtermums
from AlgorithmTools.HeikinCandle import HeikinConverter
import numpy as np
from ta.momentum import rsi

class SIAlgorithm:

    def __init__(self, symbol, data_history, big_win, small_win, hidden_divergence_check_window, upper_line_tr, alpha):
        # Data window, moving average window
        self.data_window = data_history

        self.Open = np.array([d['Open'] for d in self.data_window])
        self.High = np.array([d['High'] for d in self.data_window])
        self.Low = np.array([d['Low'] for d in self.data_window])
        self.Close = np.array([d['Close'] for d in self.data_window])

        self.a = np.c_[self.Open, self.Close].max(1)
        self.b = np.c_[self.Open, self.Close].min(1)

        body_avg = np.mean(self.a - self.b)

        self.heikin_converter1 = HeikinConverter(self.data_window[0])
        heikin_data = self.heikin_converter1.convert_many(self.data_window[1:])
        self.heikin_converter2 = HeikinConverter(heikin_data[0])
        self.heikin_data = self.heikin_converter2.convert_many(heikin_data[1:])

        self.indicator = rsi(self.heikin_data, 14)

        self.local_min_price_left, self.local_max_price_left = LocalExtermums.get_last_local_extermum(self.data_window, self.big_win)
        self.local_min_price_right, self.local_max_price_right = LocalExtermums.get_local_extermums_asymetric(self.data_window, self.small_win, self.alpha)

        self.local_min_indicator_left, self.local_max_indicator_left = LocalExtermums.get_last_local_extermum(self.data_window, self.big_win)
        self.local_min_indicator_right, self.local_max_indicator_right = LocalExtermums.get_local_extermums_asymetric(self.data_window, self.small_win, self.alpha)

        self.symbol = symbol
        self.pip_difference = body_avg * .2
        self.big_win = big_win
        self.small_win = small_win
        self.hidden_divergence_check_window = hidden_divergence_check_window
        self.upper_line_tr = upper_line_tr
        self.alpha = alpha

    def on_tick(self):
        return 0, 0

    def on_data(self, candle):
        signal = Divergence.divergence_predict(self.a, self.b, self.High, self.Low, self.indicator, self.local_min_price_left, self.local_min_price_right,
                                               self.local_max_price_left, self.local_max_price_right, self.local_min_indicator_left, self.local_min_indicator_right,
                                               self.local_max_indicator_left, self.local_max_indicator_right, self.hidden_divergence_check_window,
                                               self.pip_difference, self.upper_line_tr)
        self.data_window.pop(0)
        self.data_window.append(candle)
        return signal, self.data_window[-1]['Open']



