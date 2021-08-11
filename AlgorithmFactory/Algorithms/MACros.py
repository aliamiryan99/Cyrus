
from ta.trend import ema_indicator
from ta.trend import sma_indicator
from ta.trend import wma_indicator
import pandas as pd
from AlgorithmFactory.AlgorithmTools.LocalExtermums import *


class MovingAverageCross:

    def __init__(self, symbol, data_history, window_size, ma_window_size, price_type, ma_type, extremum_window, extremum_mode, extremum_pivot):
        # Open, High, Low, Close
        self.symbol = symbol
        self.price_type = price_type
        self.extremum_window = extremum_window
        self.extremum_mode = extremum_mode
        self.extremum_pivot = extremum_pivot
        self.ma_window_size = ma_window_size
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
        self.window_size = window_size
        len_window = len(data_history)
        if len_window <= window_size:
            raise Exception("window len should be greater than window size")
        self.data_window = data_history[len_window-self.window_size-5:len_window]
        self.price = pd.Series([row[price_type] for row in self.data_window[:-1]])
        self.local_min_price, self.local_max_price = get_local_extermums(self.data_window[:-1], self.extremum_window, self.extremum_mode)
        self.ma = self.ma_indicator(self.price[:-1], self.ma_window_size).to_list()
        self.satisfaction = False
        self.candle_buy_submitted = False
        self.candle_sell_submitted = False

    def on_tick(self):
        if self.satisfaction == 1 and not self.candle_buy_submitted:
            if self.data_window[-1]['Close'] > self.ma[-1]:
                self.candle_buy_submitted = True
                return 1, self.data_window[-1]['Close']
        elif self.satisfaction == -1 and not self.candle_sell_submitted:
            if self.data_window[-1]['Close'] < self.ma[-1]:
                self.candle_sell_submitted = True
                return -1, self.data_window[-1]['Close']
        return 0, 0

    def on_data(self, candle, cash):
        self.candle_buy_submitted = False
        self.candle_sell_submitted = False
        self.price = pd.Series([row[self.price_type] for row in self.data_window])
        self.ma = self.ma_indicator(self.price, self.ma_window_size).to_list()
        self.update_local_extremum()
        self.satisfaction = self.is_satisfy()
        self.data_window.pop(0)
        self.data_window.append(candle)
        return 0, 0

    def update_local_extremum(self):
        self.local_min_price = update_local_extremum(self.local_min_price)
        self.local_max_price = update_local_extremum(self.local_max_price)

        window_size = self.extremum_window*4
        new_local_min_price_left, new_local_max_price_left = get_local_extermums(self.data_window[-window_size:], self.extremum_window, self.extremum_mode)

        self.local_min_price = update_new_local_extremum(self.local_min_price, new_local_min_price_left, len(self.data_window), window_size)
        self.local_max_price = update_new_local_extremum(self.local_max_price, new_local_max_price_left, len(self.data_window), window_size)

    def is_satisfy(self):
        detection = True
        for i in range(self.local_min_price[-self.extremum_pivot], len(self.data_window)):
            if self.data_window[i]['High'] > self.ma[i-1]:
                detection = False
        if detection:
            return 1
        detection = True
        for i in range(self.local_max_price[-self.extremum_pivot], len(self.data_window)):
            if self.data_window[i]['Low'] < self.ma[i-1]:
                detection = False
        if detection:
            return -1



