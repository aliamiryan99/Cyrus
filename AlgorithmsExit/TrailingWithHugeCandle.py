import numpy as np
from AlgorithmTools.LocalExtermums import *


class TrailingWithHugeCandle:
    def __init__(self, data_window, alpha, beta, mode, extremum_window, extremum_mode, extremum_pivot):
        self.data_window = data_window
        self.mode = mode
        self.alpha = alpha
        self.beta = beta
        self.extremum_window = extremum_window
        self.extremum_mode = extremum_mode
        self.extremum_pivot = extremum_pivot

        self.Open = np.array([d['Open'] for d in self.data_window[:-1]])
        self.High = np.array([d['High'] for d in self.data_window[:-1]])
        self.Low = np.array([d['Low'] for d in self.data_window[:-1]])
        self.Close = np.array([d['Close'] for d in self.data_window[:-1]])

        self.local_min_price, self.local_max_price = get_local_extermums(self.data_window[:-1], self.extremum_window, self.extremum_mode)

        self.is_huge_buy = False
        self.is_huge_sell = False

    def on_data(self, history):
        self.update_local_extremum()
        self.data_window.pop(0)
        self.data_window.append(history[-1])
        self.is_huge_buy = self.detect_huge_candle(self.local_max_price[-self.extremum_pivot])
        self.is_huge_sell = self.detect_huge_candle(self.local_min_price[-self.extremum_pivot])

    def detect_huge_candle(self, start_index):
        if self.mode == 1:
            max_candle = self.data_window[start_index]['High'] - self.data_window[start_index]['Low']
            for i in range(start_index + 1, len(self.data_window) - 2):
                max_candle = max(max_candle, self.data_window[i]['High'] - self.data_window[i]['Low'])
            if self.data_window[-2]['High'] - self.data_window[-2]['Low'] > self.beta * max_candle:
                return True
        elif self.mode == 2:
            max_candle = abs(self.data_window[start_index]['Close'] - self.data_window[start_index]['Open'])
            for i in range(start_index + 1, len(self.data_window) - 2):
                max_candle = max(max_candle, abs(self.data_window[i]['Close'] - self.data_window[i]['Open']))
            if abs(self.data_window[-2]['Close'] - self.data_window[-2]['Open']) > self.beta * max_candle:
                return True
        return False

    def on_tick(self, history, entry_point, position_type, time):
        old_candle = history[-2]
        if old_candle['Volume'] == 0:
            j = 3
            while history[-j]['Volume'] == 0:
                j += 1
            old_candle = history[-j]
        new_candle = history[-1]
        max_price = max(old_candle["Open"], old_candle["Close"])  # it can be replaced by  new_candle['Close']
        min_price = min(old_candle["Open"], old_candle["Close"])  # it can be replaced by  new_candle['Close']

        old_high = max(old_candle['High'], max_price)
        old_low = min(old_candle['Low'], min_price)

        if position_type == "buy":
            if self.is_huge_buy and (entry_point != -1):
                old_low = self.alpha * old_candle['Low'] + (1 - self.alpha) * old_candle['High']
            if new_candle['High'] > old_high and new_candle['Close'] < max_price:
                return True, max_price
            elif new_candle['Low'] < old_low:
                return True, old_low
        elif position_type == "sell":
            if self.is_huge_sell and (entry_point != -1):
                old_high = self.alpha * old_candle['High'] + (1 - self.alpha) * old_candle['Low']
            if new_candle['Low'] < old_low and new_candle['Close'] > min_price:
                return True, min_price
            elif new_candle['High'] > old_high:
                return True, old_high
        return False, 0

    def on_tick_reset(self):
        pass

    def update_local_extremum(self):
        self.local_min_price = update_local_extremum(self.local_min_price)
        self.local_max_price = update_local_extremum(self.local_max_price)

        window_size =self.extremum_window*4
        new_local_min_price_left, new_local_max_price_left = get_local_extermums(self.data_window[-window_size:], self.extremum_window, self.extremum_mode)

        self.local_min_price = update_new_local_extremum(self.local_min_price, new_local_min_price_left, len(self.data_window), window_size)
        self.local_max_price = update_new_local_extremum(self.local_max_price, new_local_max_price_left, len(self.data_window), window_size)

