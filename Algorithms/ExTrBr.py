
from AlgorithmTools.LocalExtermums import *


class ExtremumTrendBreak:

    def __init__(self, symbol, data_history, window_size, extremum_window, extremum_mode, is_last_candle_check):
        # Open, High, Low, Close
        self.symbol = symbol
        self.extremum_window = extremum_window
        self.extremum_mode = extremum_mode
        self.is_last_candle_check = is_last_candle_check
        # Data window, moving average window
        self.window_size = window_size
        len_window = len(data_history)
        if len_window <= window_size:
            raise Exception("window len should be greater than window size")
        self.data_window = data_history[len_window-self.window_size-5:len_window]

        self.local_min_price, self.local_max_price = get_local_extermums(self.data_window[:-1], self.extremum_window, self.extremum_mode)
        self.buy_satisfaction = False
        self.sell_satisfaction = False
        self.candle_buy_submitted = False
        self.candle_sell_submitted = False
        self.last_buy_line_value = 0
        self.last_sell_line_value = 0

    def on_tick(self):
        if self.buy_satisfaction and not self.candle_buy_submitted:
            if self.data_window[-1]['High'] > self.last_buy_line_value:
                self.candle_buy_submitted = True
                return 1, self.data_window[-1]['Close']
        if self.sell_satisfaction and not self.candle_sell_submitted:
            if self.data_window[-1]['Low'] < self.last_sell_line_value:
                self.candle_sell_submitted = True
                return -1, self.data_window[-1]['Close']
        return 0, 0

    def on_data(self, candle, cash):
        self.candle_buy_submitted = False
        self.candle_sell_submitted = False
        self.update_local_extremum()
        self.data_window.pop(0)
        self.data_window.append(candle)
        self.check_satisfy()
        return 0, 0

    def update_local_extremum(self):
        self.local_min_price = update_local_extremum(self.local_min_price)
        self.local_max_price = update_local_extremum(self.local_max_price)

        window_size = self.extremum_window*4
        new_local_min_price_left, new_local_max_price_left = get_local_extermums(self.data_window[-window_size:], self.extremum_window, self.extremum_mode)

        self.local_min_price = update_new_local_extremum(self.local_min_price, new_local_min_price_left, len(self.data_window), window_size)
        self.local_max_price = update_new_local_extremum(self.local_max_price, new_local_max_price_left, len(self.data_window), window_size)

    def check_satisfy(self):
        shift = 2
        if self.data_window[self.local_max_price[-2]]['High'] > self.data_window[self.local_max_price[-1]]['High']:
            line = np.polyfit([self.local_max_price[-2], self.local_max_price[-1]], [self.data_window[self.local_max_price[-2]]['High'], self.data_window[self.local_max_price[-1]]['High']], 1)
            line_val = np.polyval(line, np.arange(self.local_max_price[-1], len(self.data_window)))
            self.last_buy_line_value = line_val[-1]
            self.buy_satisfaction = True
            is_last_candle = 1
            if self.is_last_candle_check:
                is_last_candle = 0
            for i in range(self.local_max_price[-1]+shift, len(self.data_window) - is_last_candle):
                if self.data_window[i]['High'] > line_val[i-self.local_max_price[-1]]:
                    self.buy_satisfaction = False

        if self.data_window[self.local_min_price[-2]]['Low'] < self.data_window[self.local_min_price[-1]]['Low']:
            line = np.polyfit([self.local_min_price[-2], self.local_min_price[-1]], [self.data_window[self.local_min_price[-2]]['Low'], self.data_window[self.local_min_price[-1]]['Low']], 1)
            line_val = np.polyval(line, np.arange(self.local_min_price[-1], len(self.data_window)))
            self.last_sell_line_value = line_val[-1]
            self.sell_satisfaction = True
            is_last_candle = 1
            if self.is_last_candle_check:
                is_last_candle = 0
            for i in range(self.local_min_price[-1]+shift, len(self.data_window) - is_last_candle):
                if self.data_window[i]['Low'] < line_val[i - self.local_min_price[-1]]:
                    self.sell_satisfaction = False





