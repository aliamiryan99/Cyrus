
from AlgorithmPackages.HarmonicPattern import HarmonicDetection
from AlgorithmTools.CandleTools import *
from AlgorithmTools.LocalExtermums import *


class Harmonic:

    def __init__(self, data_history, harmonic_name, extremum_window, extremum_mode, time_range, price_range_alpha):
        # Data window, moving average window
        self.extremum_window = extremum_window
        self.extremum_mode = extremum_mode
        self.data_window = data_history
        self.harmonic_name = harmonic_name
        self.time_range = time_range
        self.price_range_alpha = price_range_alpha

        self.open, self.high, self.low, self.close = get_ohlc(self.data_window[:-1])
        self.top, self.bottom = get_bottom_top(self.data_window[:-1])
        self.middle = get_middle(self.data_window[:-1])
        self.local_min, self.local_max = get_local_extermums(self.data_window[:-1], self.extremum_window,
                                                             self.extremum_mode)

    def on_tick(self):
        return 0, 0

    def on_data(self, candle, cash):
        self.open, self.high, self.low, self.close = update_ohlc(self.open, self.high, self.low,
                                                                 self.close, self.data_window[-1])
        self.top, self.bottom = update_top_bottom(self.top, self.bottom, self.data_window[-1])
        self.middle = update_middle(self.middle, self.data_window[-1])
        self.local_min, self.local_max = update_local_extremum_list(self.data_window, self.local_min, self.local_max,
                                                                    self.extremum_window, self.extremum_mode)
        price_range = self.price_range_alpha * (self.high - self.low).mean()
        local_min_area, local_max_area = get_local_extremum_area(self.data_window, self.local_min, self.local_max,
                                                                 self.time_range, price_range)

        bullish_signal = HarmonicDetection.harmonic_pattern(self.high, self.low, self.middle, local_min_area,
                                                            local_max_area, self.harmonic_name, "Bullish", False)
        bearish_signal = HarmonicDetection.harmonic_pattern(self.high, self.low, self.middle, local_min_area,
                                                            local_max_area, self.harmonic_name, "Bearish", False)
        signal = 0
        if bullish_signal:
            signal = 1
        if bearish_signal:
            signal = -1
        self.data_window.pop(0)
        self.data_window.append(candle)
        return signal, self.data_window[-1]['Open']

