
from AlgorithmFactory.AlgorithmTools.LocalExtermums import *


class Extremum:
    def __init__(self, data, symbol, extremum_window, extremum_mode, extremum_pivot, alpha):
        self.symbol = symbol
        self.extremum_window = extremum_window
        self.extremum_mode = extremum_mode
        self.extremum_pivot = extremum_pivot
        self.alpha = alpha
        self.data_window = data

        self.local_min_price, self.local_max_price = get_local_extermums(self.data_window[:-1], self.extremum_window,
                                                                         self.extremum_mode)

    def on_data(self, candle):
        self.update_local_extremum()
        self.data_window.pop(0)
        self.data_window.append(candle)

    def on_tick(self, data, position_type):    # position_type : (buy or sell)
        tp, sl = 0, 0
        if position_type == 'Buy':
            min_value = self.data_window[-1]['Low']
            for i in range(self.local_max_price[-1], len(self.data_window)):
                min_value = min(self.data_window[i]['Low'], min_value)
            sl = min_value - data[-1]['Close']
            tp = self.alpha * (data[-1]['Close'] - min_value)
        elif position_type == 'Sell':
            max_value = self.data_window[-1]['High']
            for i in range(self.local_min_price[-1], len(self.data_window)):
                max_value = max(self.data_window[i]['High'], max_value)
            sl = max_value - data[-1]['Close']
            tp = self.alpha * (data[-1]['Close'] - max_value)
        return tp, sl

    def update_local_extremum(self):
        self.local_min_price, self.local_max_price = update_local_extremum_list(self.data_window, self.local_min_price, self.local_max_price,
                                                                                self.extremum_window, self.extremum_mode)
