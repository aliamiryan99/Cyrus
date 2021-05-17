from AlgorithmPackages.Divergence import DivergencePkg
from AlgorithmTools import LocalExtermums
from AlgorithmTools.HeikinCandle import HeikinConverter
from AlgorithmTools.LocalExtermums import *
from AlgorithmTools.CandleTools import *

from pandas import Series

from Indicators.KDJ import KDJ
from Indicators.RSI import RSI


class Divergence:

    def __init__(self, symbol, data_history, big_win, small_win, hidden_divergence_check_window, upper_line_tr, alpha, extremum_mode):
        # Data window, moving average window
        self.data_window = data_history[1:]

        self.open, self.high, self.low, self.close = get_ohlc(data_history[:-1])

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
        self.extremum_mode = extremum_mode

        self.heikin_converter1 = HeikinConverter(data_history[0])
        self.heikin_data = self.heikin_converter1.convert_many(data_history[1:-1])
        self.heikin_converter2 = HeikinConverter(self.heikin_data[0])
        self.heikin_data = self.heikin_converter2.convert_many(self.heikin_data[1:])

        self.open_hk, self.high_hk, self.low_hk, self.close_hk = get_ohlc(self.heikin_data)

        # self.indicator = KDJ(data_history[:-1], 13, 3)
        # k_value, d_value, j_value = self.indicator.get_values()

        # values = np.array([k_value, d_value, j_value])
        #
        # self.max_indicator = np.max(values, axis=0)
        # self.min_indicator = np.min(values, axis=0)

        # self.max_indicator = np.concatenate((np.array([len(data_history) + 10] * 15), self.max_indicator))
        # self.min_indicator = np.concatenate((np.array([len(data_history) + 10] * 15), self.min_indicator))

        self.indicator = RSI(self.heikin_data, 14)
        self.max_indicator = self.indicator.values
        self.min_indicator = self.indicator.values

        self.local_min_left_stored, self.local_max_left_stored = [], []
        self.local_min_right_stored, self.local_max_right_stored = [], []

        self.local_min_indicator_left_stored, self.local_max_indicator_left_stored = [], []
        self.local_min_indicator_right_stored, self.local_max_indicator_right_stored = [], []

        self.local_min_price_left, self.local_max_price_left = LocalExtermums.get_local_extermums(data_history[:-1], self.big_win, self.extremum_mode)
        self.local_min_price_right, self.local_max_price_right = LocalExtermums.get_local_extermums_asymetric(data_history[:-1], self.small_win, self.alpha, self.extremum_mode)

        self.local_min_indicator_left, self.local_max_indicator_left = LocalExtermums.get_indicator_local_extermums(self.max_indicator, self.min_indicator, self.big_win)
        self.local_min_indicator_right, self.local_max_indicator_right = LocalExtermums.get_indicator_local_extermums_asymetric(self.max_indicator, self.min_indicator, self.small_win, self.alpha)

        self.buy_trigger = False
        self.sell_trigger = False
        self.buy_limit_price = 0
        self.sell_limit_price = 0
        self.candle_buy_submitted = False
        self.candle_sell_submitted = False

    def on_tick(self):
        if self.buy_trigger and not self.candle_buy_submitted:
            if self.data_window[-1]['High'] > self.buy_limit_price:
                self.candle_buy_submitted = True
                return 1, self.buy_limit_price
        if self.sell_trigger and not self.candle_sell_submitted:
            if self.data_window[-1]['Low'] < self.sell_limit_price:
                self.candle_sell_submitted = True
                return -1, self.sell_limit_price
        return 0, 0

    def on_data(self, candle, cash):
        self.candle_buy_submitted = False
        self.candle_sell_submitted = False
        self.buy_trigger = False
        self.sell_trigger = False
        self.update_history()
        self.update_indicator()
        self.update_local_extremums()
        signal = DivergencePkg.divergence_predict(self.a, self.b, self.low, self.high, self.max_indicator, self.min_indicator,
                                                  self.local_min_price_left, self.local_min_price_right,
                                                  self.local_max_price_left, self.local_max_price_right,
                                                  self.local_min_indicator_left, self.local_min_indicator_right,
                                                  self.local_max_indicator_left, self.local_max_indicator_right,
                                                  self.hidden_divergence_check_window,
                                                  self.pip_difference, self.upper_line_tr)
        if signal == 1:
            self.buy_trigger = True
            self.buy_limit_price = self.data_window[-1]['High']
        elif signal == -1:
            self.sell_trigger = True
            self.sell_limit_price = self.data_window[-1]['Low']
        self.data_window.pop(0)
        self.data_window.append(candle)
        return 0, 0

    def update_history(self):
        self.a = self.a[1:]
        self.a = np.append(self.a, [max(self.data_window[-1]['Open'], self.data_window[-1]['Close'])])
        self.b = self.b[1:]
        self.b = np.append(self.b, [min(self.data_window[-1]['Open'], self.data_window[-1]['Close'])])
        self.open = self.open[1:]
        self.open = np.append(self.open, [self.data_window[-1]['Open']])
        self.high = self.high[1:]
        self.high = np.append(self.high, [self.data_window[-1]['High']])
        self.low = self.low[1:]
        self.low = np.append(self.low, [self.data_window[-1]['Low']])
        self.close = self.close[1:]
        self.close = np.append(self.close, [self.data_window[-1]['Close']])

    def update_indicator(self):
        self.update_heikin_data()
        # k_value, d_value, j_value = kdj(self.High, self.Low, self.Close, 13, 3)
        # values = np.array([k_value, d_value, j_value])
        # last_max_indicator = np.max(values, axis=0)
        # last_min_indicator = np.min(values, axis=0)
        self.indicator.update(self.heikin_data)
        last_max_indicator = self.indicator.values
        last_min_indicator = self.indicator.values

        self.max_indicator = self.max_indicator[1:]
        self.max_indicator = np.append(self.max_indicator, last_max_indicator[-1])
        self.min_indicator = self.min_indicator[1:]
        self.min_indicator = np.append(self.min_indicator, last_min_indicator[-1])

    def update_heikin_data(self):
        heikin_1 = self.heikin_converter1.on_data(self.data_window[-1])
        heikin_2 = self.heikin_converter2.on_data(heikin_1)
        self.heikin_data.pop(0)
        self.heikin_data.append(heikin_2)

    def update_local_extremums(self):
        self.local_min_price_left = update_local_extremum(self.local_min_price_left)
        self.local_max_price_left = update_local_extremum(self.local_max_price_left)
        self.local_min_price_right = update_local_extremum(self.local_min_price_right)
        self.local_max_price_right = update_local_extremum(self.local_max_price_right)
        self.local_min_indicator_left = update_local_extremum(self.local_min_indicator_left)
        self.local_max_indicator_left = update_local_extremum(self.local_max_indicator_left)
        self.local_min_indicator_right = update_local_extremum(self.local_min_indicator_right)
        self.local_max_indicator_right = update_local_extremum(self.local_max_indicator_right)

        window_size = max(self.big_win*4, self.small_win*4)
        new_local_min_price_left, new_local_max_price_left = LocalExtermums.get_local_extermums(self.data_window[-window_size:], self.big_win, self.extremum_mode)
        new_local_min_price_right, new_local_max_price_right = LocalExtermums.get_local_extermums_asymetric(self.data_window[-window_size:], self.small_win, self.alpha, self.extremum_mode)

        new_local_min_indicator_left, new_local_max_indicator_left = LocalExtermums.get_indicator_local_extermums(self.max_indicator[-window_size:], self.min_indicator[-window_size:], self.big_win)
        new_local_min_indicator_right, new_local_max_indicator_right = LocalExtermums.get_indicator_local_extermums_asymetric(self.max_indicator[-window_size:], self.min_indicator[-window_size:], self.small_win, self.alpha)

        self.local_min_price_left = update_new_local_extremum(self.local_min_price_left, new_local_min_price_left, len(self.data_window)+1, window_size)
        self.local_max_price_left = update_new_local_extremum(self.local_max_price_left, new_local_max_price_left, len(self.data_window)+1, window_size)
        self.local_min_price_right = update_new_local_extremum(self.local_min_price_right, new_local_min_price_right, len(self.data_window)+1, window_size)
        self.local_max_price_right = update_new_local_extremum(self.local_max_price_right, new_local_max_price_right, len(self.data_window)+1, window_size)
        self.local_min_indicator_left = update_new_local_extremum(self.local_min_indicator_left, new_local_min_indicator_left, len(self.min_indicator)+1, window_size)
        self.local_max_indicator_left = update_new_local_extremum(self.local_max_indicator_left, new_local_max_indicator_left, len(self.max_indicator)+1, window_size)
        self.local_min_indicator_right = update_new_local_extremum(self.local_min_indicator_right, new_local_min_indicator_right, len(self.min_indicator)+1, window_size)
        self.local_max_indicator_right = update_new_local_extremum(self.local_max_indicator_right, new_local_max_indicator_right, len(self.max_indicator)+1, window_size)









