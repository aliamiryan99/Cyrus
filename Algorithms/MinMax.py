
from AlgorithmPackages.MinMaxTrend import MinMaxTrend
from AlgorithmTools.CandleTools import *
from AlgorithmTools.LocalExtermums import *


class MinMax:

    def __init__(self, symbol, data_history, extremum_window, extremum_mode):
        # Data window, moving average window
        self.symbol = symbol
        self.extremum_window = extremum_window
        self.extremum_mode = extremum_mode
        self.data_window = data_history

        self.open, self.high, self.low, self.close = get_ohlc(self.data_window[:-1])
        self.top, self.bottom = get_bottom_top(self.data_window[:-1])
        self.local_min, self.local_max = get_local_extermums(self.data_window[:-1], self.extremum_window,
                                                             self.extremum_mode)

    def on_tick(self):
        return 0, 0

    def on_data(self, candle, cash):
        self.open, self.high, self.low, self.close = update_ohlc(self.open, self.high, self.low,
                                                                 self.close, self.data_window[-1])
        self.top, self.bottom = update_top_bottom(self.top, self.bottom, self.data_window[-1])
        self.local_min, self.local_max = update_local_extremum_list(self.data_window, self.local_min, self.local_max,
                                                                    self.extremum_window, self.extremum_mode)

        signal = MinMaxTrend.min_max_trend_detect(self.open, self.high, self.low, self.close, self.top, self.bottom,
                                                  self.local_min, self.local_max, False)
        self.data_window.pop(0)
        self.data_window.append(candle)
        return signal, self.data_window[-1]['Open']

