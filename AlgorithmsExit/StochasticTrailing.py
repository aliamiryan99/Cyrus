import numpy as np
from AlgorithmTools.LocalExtermums import *

from ta.momentum import stochrsi_k
from pandas import Series


class StochasticTrailing:
    def __init__(self, data_window,upper_band, lower_band, stoch_window):
        self.data_window = data_window
        self.upper_band = upper_band
        self.lower_band = lower_band
        self.stoch_window = stoch_window

        self.Open = np.array([d['Open'] for d in self.data_window[:-1]])
        self.High = np.array([d['High'] for d in self.data_window[:-1]])
        self.Low = np.array([d['Low'] for d in self.data_window[:-1]])
        self.Close = np.array([d['Close'] for d in self.data_window[:-1]])

        self.indicator = np.array(list(Series(stochrsi_k(Series([item['Close'] for item in data_window[:-1]]), stoch_window))))

        self.is_huge_buy = False
        self.is_huge_sell = False

    def on_data(self, history):
        self.update_indicator()
        self.data_window.pop(0)
        self.data_window.append(history[-1])

    def on_tick(self, history, entry_point, position_type, time):
        if position_type == 'buy':
            if self.indicator[-1] > self.upper_band:
                return True, history[-1]['Close']
        elif position_type == 'sell':
            if self.indicator[-1] < self.lower_band:
                return True, history[-1]['Close']
        return False, 0

    def update_indicator(self):
        #indicator = list(Series(rsi(Series([item['Close'] for item in self.data_window]), 14)))
        indicator = list(Series(stochrsi_k(Series([item['Close'] for item in self.data_window]), self.stoch_window)))

        self.indicator = self.indicator[1:]
        self.indicator = np.append(self.indicator, indicator[-1])