
from Algorithms.Divergence import Divergence
from AlgorithmTools import LocalExtermums
from AlgorithmTools.HeikinCandle import HeikinConverter
from AlgorithmTools.LocalExtermums import *
from AlgorithmTools import Trend
import numpy as np
from pandas import Series
import copy
from ta.momentum import rsi
from ta.momentum import stochrsi_k
from Indicators.KDJ import kdj


class StochasticAlgorithm:

    def __init__(self, symbol, data_history, upper_band_indicator, lower_band_indicator, price_mode, stoch_window):
        # Data window, moving average window
        self.data_window = data_history[1:]

        self.Open = np.array([d['Open'] for d in data_history[:-1]])
        self.High = np.array([d['High'] for d in data_history[:-1]])
        self.Low = np.array([d['Low'] for d in data_history[:-1]])
        self.Close = np.array([d['Close'] for d in data_history[:-1]])

        self.a = np.c_[self.Open, self.Close].max(1)
        self.b = np.c_[self.Open, self.Close].min(1)

        self.symbol = symbol
        self.price_mode = price_mode
        self.upper_band = upper_band_indicator
        self.lower_band = lower_band_indicator
        self.stoch_window = stoch_window

        # indicator = np.array(list(Series(rsi(Series([item['Close'] for item in data_history[:-1]]), 14))))
        indicator = np.array(list(Series(stochrsi_k(Series([item['Close'] for item in data_history[:-1]]), self.stoch_window))))

        self.max_indicator = indicator
        self.min_indicator = indicator

        # self.max_indicator = np.concatenate((np.array([len(data_history)+10]*15), self.max_indicator))
        # self.min_indicator = np.concatenate((np.array([len(data_history)+10]*15), self.min_indicator))

        self.buy_trigger = False
        self.sell_trigger = False
        self.candle_buy_submitted = False
        self.candle_sell_submitted = False
        self.candle_trend = 0

    def on_tick(self):
        if self.buy_trigger and not self.candle_buy_submitted:
            price = 0
            if self.price_mode == 1:    # High Low
                price = self.data_window[-2]['High']
            elif self.price_mode == 2:   # Top Bottom
                price = max(self.data_window[-2]['Open'], self.data_window[-2]['Close'])
            if self.data_window[-1]['High'] >= price:
                self.candle_buy_submitted = True
                self.buy_trigger = False
                return 1, price
        if self.sell_trigger and not self.candle_sell_submitted:
            price = 0
            if self.price_mode == 1:
                price = self.data_window[-2]['Low']
            elif self.price_mode == 2:
                price = min(self.data_window[-2]['Open'], self.data_window[-2]['Close'])
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
        if self.max_indicator[-1] >= self.upper_band:
            self.sell_trigger = True
        if self.min_indicator[-1] <= self.lower_band:
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
        #indicator = list(Series(rsi(Series([item['Close'] for item in self.data_window]), 14)))
        indicator = list(Series(stochrsi_k(Series([item['Close'] for item in self.data_window]), self.stoch_window)))
        last_max_indicator = indicator
        last_min_indicator = indicator

        self.max_indicator = self.max_indicator[1:]
        self.max_indicator = np.append(self.max_indicator, last_max_indicator[-1])
        self.min_indicator = self.min_indicator[1:]
        self.min_indicator = np.append(self.min_indicator, last_min_indicator[-1])




