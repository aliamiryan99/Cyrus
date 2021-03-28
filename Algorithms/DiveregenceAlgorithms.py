
from Algorithms.Divergence import Divergence
from AlgorithmTools import LocalExtermums
from AlgorithmTools.HeikinCandle import HeikinConverter
import numpy as np
from pandas import Series
import copy
from ta.momentum import rsi

class DivergenceAlgorithm:

    def __init__(self, symbol, data_history, big_win, small_win, hidden_divergence_check_window, upper_line_tr, alpha):
        # Data window, moving average window
        self.data_window = data_history

        self.Open = np.array([d['Open'] for d in self.data_window[:-1]])
        self.High = np.array([d['High'] for d in self.data_window[:-1]])
        self.Low = np.array([d['Low'] for d in self.data_window[:-1]])
        self.Close = np.array([d['Close'] for d in self.data_window[:-1]])

        self.a = np.c_[self.Open, self.Close].max(1)
        self.b = np.c_[self.Open, self.Close].min(1)

        body_avg = np.mean(self.a - self.b)

        self.symbol = symbol
        self.pip_difference = body_avg * .2
        self.big_win = big_win
        self.small_win = small_win
        self.hidden_divergence_check_window = hidden_divergence_check_window
        self.upper_line_tr = upper_line_tr
        self.alpha = alpha

        self.heikin_converter1 = HeikinConverter(self.data_window[0])
        heikin_data = self.heikin_converter1.convert_many(self.data_window[1:-1])
        self.heikin_converter2 = HeikinConverter(heikin_data[0])
        self.heikin_data = self.heikin_converter2.convert_many(heikin_data[1:])

        self.indicator = np.array(list(Series(rsi(Series([item['Close'] for item in self.heikin_data]), 14))))

        self.local_min_left_stored, self.local_max_left_stored = [], []
        self.local_min_right_stored, self.local_max_right_stored = [], []

        self.local_min_indicator_left_stored, self.local_max_indicator_left_stored = [], []
        self.local_min_indicator_right_stored, self.local_max_indicator_right_stored = [], []

        self.local_min_price_left, self.local_max_price_left = LocalExtermums.get_local_extermums(self.data_window[:-1], self.big_win)
        self.local_min_price_right, self.local_max_price_right = LocalExtermums.get_local_extermums_asymetric(self.data_window[:-1], self.small_win, self.alpha)

        self.local_min_indicator_left, self.local_max_indicator_left = LocalExtermums.get_indicator_local_extermums(self.indicator, self.big_win)
        self.local_min_indicator_right, self.local_max_indicator_right = LocalExtermums.get_indicator_local_extermums_asymetric(self.indicator, self.small_win, self.alpha)


    def on_tick(self):
        return 0, 0

    def on_data(self, candle):
        self.update_history()
        self.update_indicator()
        self.update_local_extremums()
        self.data_window.pop(0)
        self.data_window.append(candle)
        signal = Divergence.divergence_predict(self.a, self.b, self.Low, self.High, self.indicator,
                                               self.local_min_price_left, self.local_min_price_right,
                                               self.local_max_price_left, self.local_max_price_right,
                                               self.local_min_indicator_left, self.local_min_indicator_right,
                                               self.local_max_indicator_left, self.local_max_indicator_right,
                                               self.hidden_divergence_check_window,
                                               self.pip_difference, self.upper_line_tr)
        return signal, self.data_window[-1]['Open']

    def update_history(self):
        self.a = self.a[1:]
        self.a = np.append(self.a, [max(self.data_window[-1]['Open'], self.data_window[-1]['Close'])])
        self.b = self.b[1:]
        self.b = np.append(self.b, [min(self.data_window[-1]['Open'], self.data_window[-1]['Close'])])
        self.High = self.High[1:]
        self.High = np.append(self.High, [self.data_window[-1]['High']])
        self.Low = self.Low[1:]
        self.Low = np.append(self.Low, [self.data_window[-1]['Low']])

    def update_indicator(self):
        self.update_heikin_data()
        last_indicator = list(rsi(Series([item['Close'] for item in self.heikin_data]), 14).dropna())
        self.indicator = self.indicator[1:]
        self.indicator = np.append(self.indicator, last_indicator[-1])

    def update_heikin_data(self):
        heikin_1 = self.heikin_converter1.on_data(self.data_window[-1])
        heikin_2 = self.heikin_converter2.on_data(heikin_1)
        self.heikin_data.pop(0)
        self.heikin_data.append(heikin_2)

    def update_local_extremums(self):
        self.local_min_price_left = self.update_local_extremum(self.local_min_price_left)
        self.local_max_price_left = self.update_local_extremum(self.local_max_price_left)
        self.local_min_price_right = self.update_local_extremum(self.local_min_price_right)
        self.local_max_price_right = self.update_local_extremum(self.local_max_price_right)
        self.local_min_indicator_left = self.update_local_extremum(self.local_min_indicator_left)
        self.local_max_indicator_left = self.update_local_extremum(self.local_max_indicator_left)
        self.local_min_indicator_right = self.update_local_extremum(self.local_min_indicator_right)
        self.local_max_indicator_right = self.update_local_extremum(self.local_max_indicator_right)

        window_size = max(self.big_win*4, self.small_win*4)
        new_local_min_price_left, new_local_max_price_left = LocalExtermums.get_local_extermums(self.data_window[-window_size:], self.big_win)
        new_local_min_price_right, new_local_max_price_right = LocalExtermums.get_local_extermums_asymetric(self.data_window[-window_size:], self.small_win, self.alpha)

        new_local_min_indicator_left, new_local_max_indicator_left = LocalExtermums.get_indicator_local_extermums(self.indicator[-window_size:], self.big_win)
        new_local_min_indicator_right, new_local_max_indicator_right = LocalExtermums.get_indicator_local_extermums_asymetric(self.indicator[-window_size:], self.small_win, self.alpha)

        self.local_min_price_left = self.update_new_lcoal_extremum(self.local_min_price_left, new_local_min_price_left, self.local_min_left_stored, len(self.data_window), window_size)
        self.local_max_price_left = self.update_new_lcoal_extremum(self.local_max_price_left, new_local_max_price_left, self.local_max_left_stored, len(self.data_window), window_size)
        self.local_min_price_right = self.update_new_lcoal_extremum(self.local_min_price_right, new_local_min_price_right, self.local_min_right_stored, len(self.data_window), window_size)
        self.local_max_price_right = self.update_new_lcoal_extremum(self.local_max_price_right, new_local_max_price_right, self.local_max_right_stored, len(self.data_window), window_size)
        self.local_min_indicator_left = self.update_new_lcoal_extremum(self.local_min_indicator_left, new_local_min_indicator_left, self.local_min_indicator_left_stored, len(self.indicator)+1, window_size)
        self.local_max_indicator_left = self.update_new_lcoal_extremum(self.local_max_indicator_left, new_local_max_indicator_left, self.local_max_indicator_left_stored, len(self.indicator)+1, window_size)
        self.local_min_indicator_right = self.update_new_lcoal_extremum(self.local_min_indicator_right, new_local_min_indicator_right, self.local_min_indicator_right_stored, len(self.indicator)+1, window_size)
        self.local_max_indicator_right = self.update_new_lcoal_extremum(self.local_max_indicator_right, new_local_max_indicator_right, self.local_max_indicator_right_stored, len(self.indicator)+1, window_size)


    def update_local_extremum(self, local_extremum):
        while local_extremum[0] <= 0:
            local_extremum = local_extremum[1:]
        for i in range(len(local_extremum)):
            local_extremum[i] -= 1
        return local_extremum

    def update_new_lcoal_extremum(self, pre_local_extremum, new_local_extremum, local_extremum_stored, total_window, local_window):
        for i in range(len(new_local_extremum)):
            new_local = new_local_extremum[i] + (total_window - local_window - 1)
            if not new_local in pre_local_extremum:
                pre_local_extremum = np.append(pre_local_extremum, [new_local])
                local_extremum_stored.append(self.data_window[new_local]['GMT'])
        return pre_local_extremum










