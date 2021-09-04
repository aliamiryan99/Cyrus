
from AlgorithmFactory.AlgorithmTools.LocalExtermums import *
from AlgorithmFactory.AlgorithmTools.CandleTools import get_bottom_top


class MonotoneExtremum:

    def __init__(self, symbol, data_history, window_size, extremum_window, extremum_mode, extremum_level, extremum_pivot, monotone_mode):   # monotone_mode ; 1 : limit price is taken from last extremum price , 2 : limit price is taken from last candle
        # Open, High, Low, Close
        self.symbol = symbol
        self.extremum_window = extremum_window
        self.extremum_mode = extremum_mode
        self.extremum_pivot = extremum_pivot
        self.extremum_level = extremum_level
        self.monoton_mode = monotone_mode
        # Data window, moving average window
        self.window_size = window_size
        len_window = len(data_history)
        if len_window <= window_size:
            raise Exception("window len should be greater than window size")

        self.data_window = data_history[len_window-self.window_size-5:]

        bottom_candle, top_candle = get_bottom_top(self.data_window[:-1])

        self.price_up = [row['High'] for row in self.data_window[:-1]]
        self.price_down = [row['Low'] for row in self.data_window[:-1]]

        if self.extremum_mode == 2:
            self.price_up = top_candle
            self.price_down = bottom_candle

        self.local_min_price, self.local_max_price = get_local_extermums(self.data_window[:-1], self.extremum_window, self.extremum_mode)

        self.buy_satisfaction = False
        self.sell_satisfaction = False
        self.candle_buy_submitted = False
        self.candle_sell_submitted = False

    def on_tick(self):
        if self.buy_satisfaction and not self.candle_buy_submitted:
            if self.monoton_mode == 1:
                if self.data_window[-1]['Close'] > self.price_up[self.local_max_price[-self.extremum_pivot]]:
                    self.candle_buy_submitted = True
                    return 1, self.price_up[self.local_max_price[-self.extremum_pivot]]
            elif self.monoton_mode == 2:
                if self.data_window[-1]['Close'] > self.price_up[-1]:
                    self.candle_buy_submitted = True
                    return 1, self.price_up[-1]
        if self.sell_satisfaction and not self.candle_sell_submitted:
            if self.monoton_mode == 1:
                if self.data_window[-1]['Close'] < self.price_down[self.local_min_price[-self.extremum_pivot]]:
                    self.candle_sell_submitted = True
                    return -1, self.price_down[self.local_min_price[-self.extremum_pivot]]
            elif self.monoton_mode == 2:
                if self.data_window[-1]['Close'] < self.price_down[-1]:
                    self.candle_sell_submitted = True
                    return -1, self.price_down[-1]
        return 0, 0

    def on_data(self, candle, cash):
        self.data_window.pop(0)

        self.candle_buy_submitted = False
        self.candle_sell_submitted = False
        self.local_min_price, self.local_max_price = update_local_extremum_list(self.data_window, self.local_min_price,
                                   self.local_max_price, self.extremum_window, self.extremum_mode)
        self.price_up.pop(0)
        self.price_down.pop(0)
        if self.extremum_mode == 1:
            self.price_up.append(self.data_window[-1]['High'])
            self.price_down.append(self.data_window[-1]['Low'])
        elif self.extremum_mode == 2:
            self.price_up.append(max(self.data_window[-1]['Open'], self.data_window[-1]['Close']))
            self.price_down.append(min(self.data_window[-1]['Open'], self.data_window[-1]['Close']))

        self.data_window.append(candle)

        self.check_satisfy()
        return 0, 0

    def check_satisfy(self):
        self.buy_satisfaction = True
        for i in range(self.local_max_price[-1]+1, len(self.price_up)):
            if self.price_up[self.local_max_price[-1]] < self.price_up[i]:
                self.buy_satisfaction = False
                break

        for i in range(len(self.local_max_price)-self.extremum_level, len(self.local_max_price)):
            if self.price_up[self.local_max_price[i-1]] < self.price_up[self.local_max_price[i]]:
                self.buy_satisfaction = False
                break

        self.sell_satisfaction = True
        for i in range(self.local_min_price[-1]+1, len(self.price_down)):
            if self.price_down[self.local_min_price[-1]] > self.price_down[i]:
                self.sell_satisfaction = False
                break
        for i in range(len(self.local_min_price) - self.extremum_level, len(self.local_min_price)):
            if self.price_down[self.local_min_price[i - 1]] > self.price_down[self.local_min_price[i]]:
                self.sell_satisfaction = False
                break


