
from AlgorithmTools.LocalExtermums import *


class LocalExtremumTrailing:
    def __init__(self, data_window, extremum_window, extremum_mode, extremum_pivot):
        self.data_window = data_window
        self.extremum_window = extremum_window
        self.extremum_mode = extremum_mode
        self.extremum_pivot = extremum_pivot

        self.local_min_price, self.local_max_price = get_local_extermums(self.data_window[:-1], self.extremum_window,
                                                                         self.extremum_mode)

    def on_data(self, history):
        self.update_local_extremum()
        self.data_window.pop(0)
        self.data_window.append(history[-1])

    def on_tick(self, history, entry_point, position_type, time):
        new_candle = history[-1]

        old_high = history[self.local_max_price[-1]]['High']

        old_low = history[self.local_min_price[-1]]['Low']

        if position_type == "Buy":
            if new_candle['Low'] < old_low:
                return True, old_low
        elif position_type == "Sell":
            if new_candle['High'] > old_high:
                return True, old_high
        return False, 0

    def on_tick_end(self):
        pass

    def update_local_extremum(self):
        self.local_min_price, self.local_max_price = update_local_extremum_list(self.data_window, self.local_min_price,
                                                                                self.local_max_price,
                                                                                self.extremum_window, self.extremum_mode)

