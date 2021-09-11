from AlgorithmFactory.AlgorithmTools import LocalExtermums
from AlgorithmFactory.AlgorithmTools.LocalExtermums import *
from AlgorithmFactory.AlgorithmTools import Trend
import numpy as np
from pandas import Series
from ta.momentum import rsi


class ConditionalDivergence:

    def __init__(self, symbol, data_history, extremum_mode, extremum_window, resistance_pivot, price_mode, trend_window):
        # Data window, moving average window
        self.data_window = data_history[1:]

        self.Open = np.array([d['Open'] for d in data_history[:-1]])
        self.High = np.array([d['High'] for d in data_history[:-1]])
        self.Low = np.array([d['Low'] for d in data_history[:-1]])
        self.Close = np.array([d['Close'] for d in data_history[:-1]])

        self.a = np.c_[self.Open, self.Close].max(1)
        self.b = np.c_[self.Open, self.Close].min(1)

        self.symbol = symbol
        self.resistance_pivot = resistance_pivot
        self.extremum_mode = extremum_mode
        self.extremum_window = extremum_window
        self.price_mode = price_mode
        self.trend_window = trend_window

        indicator = np.array(list(Series(rsi(Series([item['Close'] for item in data_history[:-1]]), 14))))
        #indicator = np.array(list(Series(stochrsi_k(Series([item['Close'] for item in data_history[:-1]]), 14))))

        self.max_indicator = indicator
        self.min_indicator = indicator

        # self.max_indicator = np.concatenate((np.array([len(data_history)+10]*15), self.max_indicator))
        # self.min_indicator = np.concatenate((np.array([len(data_history)+10]*15), self.min_indicator))

        self.local_min_left_stored, self.local_max_left_stored = [], []
        self.local_min_right_stored, self.local_max_right_stored = [], []

        self.local_min_indicator_left_stored, self.local_max_indicator_left_stored = [], []
        self.local_min_indicator_right_stored, self.local_max_indicator_right_stored = [], []


        self.local_min_indicator_left, self.local_max_indicator_left = LocalExtermums.get_indicator_local_extermums(self.max_indicator, self.min_indicator, self.extremum_window)

        self.buy_trigger = False
        self.sell_trigger = False
        self.candle_buy_submitted = False
        self.candle_sell_submitted = False
        self.candle_trend = 0

    def on_tick(self):
        if self.buy_trigger and not self.candle_buy_submitted and self.candle_trend == 1:
            price = 0
            if self.price_mode == 1:    # High Low
                price = self.data_window[-self.resistance_pivot-1]['High']
            elif self.price_mode == 2:   # Top Bottom
                price = max(self.data_window[-self.resistance_pivot-1]['Open'], self.data_window[-self.resistance_pivot-1]['Close'])
            if self.data_window[-1]['High'] >= price:
                self.candle_buy_submitted = True
                self.buy_trigger = False
                return 1, price
        if self.sell_trigger and not self.candle_sell_submitted and self.candle_trend == -1:
            price = 0
            if self.price_mode == 1:
                price = self.data_window[-self.resistance_pivot-1]['Low']
            elif self.price_mode == 2:
                price = min(self.data_window[-self.resistance_pivot-1]['Open'], self.data_window[-self.resistance_pivot-1]['Close'])
            if self.data_window[-1]['Low'] <= price:
                self.candle_sell_submitted = True
                self.sell_trigger = False
                return -1, price
        return 0, 0

    def on_data(self, candle, cash):
        self.candle_buy_submitted = False
        self.candle_sell_submitted = False
        self.update_history()
        self.update_indicator()
        self.update_local_extremums()
        self.candle_trend = Trend.candle_trend_detection(self.data_window, self.trend_window)
        if self.max_indicator[-1] >= self.max_indicator[self.local_max_indicator_left[-1]] and self.max_indicator[-1] > 50:
            self.sell_trigger = True
        if self.min_indicator[-1] <= self.min_indicator[self.local_min_indicator_left[-1]] and self.max_indicator[-1] < 50:
            self.buy_trigger = True
        self.data_window.pop(0)
        self.data_window.append(candle)
        return 0, 0

    def update_history(self):
        self.a = self.a[1:]
        self.a = np.append(self.a, [max(self.data_window[-1]['Open'], self.data_window[-1]['Close'])])
        self.b = self.b[1:]
        self.b = np.append(self.b, [min(self.data_window[-1]['Open'], self.data_window[-1]['Close'])])
        self.Open = self.Open[1:]
        self.Open = np.append(self.Open, [self.data_window[-1]['Open']])
        self.High = self.High[1:]
        self.High = np.append(self.High, [self.data_window[-1]['High']])
        self.Low = self.Low[1:]
        self.Low = np.append(self.Low, [self.data_window[-1]['Low']])
        self.Close = self.Close[1:]
        self.Close = np.append(self.Close, [self.data_window[-1]['Close']])

    def update_indicator(self):
        indicator = list(Series(rsi(Series([item['Close'] for item in self.data_window]), 14)))
        last_max_indicator = indicator
        last_min_indicator = indicator

        self.max_indicator = self.max_indicator[1:]
        self.max_indicator = np.append(self.max_indicator, last_max_indicator[-1])
        self.min_indicator = self.min_indicator[1:]
        self.min_indicator = np.append(self.min_indicator, last_min_indicator[-1])

    def update_local_extremums(self):
        self.local_min_indicator_left = update_local_extremum(self.local_min_indicator_left)
        self.local_max_indicator_left = update_local_extremum(self.local_max_indicator_left)

        window_size = self.extremum_window * 4

        new_local_min_indicator_left, new_local_max_indicator_left = LocalExtermums.get_indicator_local_extermums(self.max_indicator[-window_size:], self.min_indicator[-window_size:], self.extremum_window)

        self.local_min_indicator_left = update_new_local_extremum(self.local_min_indicator_left, new_local_min_indicator_left, len(self.min_indicator)+1, window_size)
        self.local_max_indicator_left = update_new_local_extremum(self.local_max_indicator_left, new_local_max_indicator_left, len(self.max_indicator)+1, window_size)









