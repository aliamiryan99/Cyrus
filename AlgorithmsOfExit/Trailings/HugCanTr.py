
from AlgorithmTools.LocalExtermums import *


class HugeCandleTrailing:
    def __init__(self, data_window, alpha, beta, mode, extremum_window, extremum_mode, extremum_pivot):
        self.data_window = data_window
        self.mode = mode
        self.alpha = alpha
        self.beta = beta
        self.extremum_window = extremum_window
        self.extremum_mode = extremum_mode
        self.extremum_pivot = extremum_pivot

        self.local_min_price, self.local_max_price = get_local_extermums(self.data_window[:-1], self.extremum_window, self.extremum_mode)

        self.is_huge_buy = False
        self.is_huge_sell = False

    def on_data(self, history):
        self.update_local_extremum()
        self.data_window.pop(0)
        self.data_window.append(history[-1])
        self.is_huge_buy = self.detect_huge_candle(self.local_max_price[-self.extremum_pivot])
        self.is_huge_sell = self.detect_huge_candle(self.local_min_price[-self.extremum_pivot])

    def on_tick(self, history, entry_point, position_type, time):
        old_candle = history[-2]
        new_candle = history[-1]

        max_price = max(old_candle["Open"], old_candle["Close"])  # it can be replaced by  new_candle['Close']
        min_price = min(old_candle["Open"], old_candle["Close"])  # it can be replaced by  new_candle['Close']

        old_high = old_candle['High']
        old_low = old_candle['Low']

        if position_type == "Buy":
            if self.is_huge_buy and (entry_point != -1):
                old_low = self.alpha * old_candle['Low'] + (1 - self.alpha) * old_candle['High']
            if new_candle['High'] > old_high and new_candle['Close'] < max_price:
                return True, max_price
            elif new_candle['Low'] < old_low:
                return True, old_low
        elif position_type == "Sell":
            if self.is_huge_sell and (entry_point != -1):
                old_high = self.alpha * old_candle['High'] + (1 - self.alpha) * old_candle['Low']
            if new_candle['Low'] < old_low and new_candle['Close'] > min_price:
                return True, min_price
            elif new_candle['High'] > old_high:
                return True, old_high
        return False, 0

    def on_tick_reset(self):
        pass

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

    def update_local_extremum(self):
        self.local_min_price, self.local_max_price = update_local_extremum_list(self.data_window, self.local_min_price,
                                                                                self.local_max_price,
                                                                                self.extremum_window, self.extremum_mode)

