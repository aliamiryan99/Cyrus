from AlgorithmPackages.SimpleIdea import SimpleIdeaPkg
from AlgorithmTools.LocalExtermums import *
from Shared.Variables import Variables


class SimpleIdea:

    def __init__(self, symbol, data_history, win_inc, win_dec, shadow_threshold, body_threshold, mode, mean_window, extremum_window, extremum_mode, alpha, impulse_threshold):
        # Data window, moving average window
        self.win_inc = win_inc
        self.win_dec = win_dec
        self.mode = mode
        self.mean_window = mean_window
        self.window_size = max(win_inc, win_dec)
        self.symbol = symbol
        self.shadow_threshold = shadow_threshold
        self.body_threshold = body_threshold
        self.extremum_window = extremum_window
        self.extremum_mode = extremum_mode
        self.alpha = alpha
        self.impulse_threshold = impulse_threshold * 10 ** -Variables.config.symbols_pip[symbol]
        len_window = len(data_history)
        if len_window <= self.window_size:
            raise Exception("window len should be greater than window size")
        self.data_window = data_history
        self.local_min_price, self.local_max_price = get_local_extermums(self.data_window[:-1], self.extremum_window,
                                                                         self.extremum_mode)

    def on_tick(self):
        return 0, 0

    def on_data(self, candle, cash):
        self.local_min_price, self.local_max_price = update_local_extremum_list(self.data_window, self.local_min_price, self.local_max_price, self.extremum_window, self.extremum_mode)
        signal = SimpleIdeaPkg.simple_idea(self.symbol, self.data_window, self.win_inc, self.win_dec,
                                           self.shadow_threshold, self.body_threshold, self.mode, self.mean_window)
        if self.mode == 3:
            if signal == 1:
                if self.data_window[self.local_max_price[-1]]['High'] - self.data_window[-1]['Close'] < self.impulse_threshold:
                    signal = 0
            elif signal == -1:
                if self.data_window[-1]['Close'] - self.data_window[self.local_min_price[-1]]['Low'] < self.impulse_threshold:
                    signal = 0

        self.data_window.pop(0)
        self.data_window.append(candle)
        return signal, self.data_window[-1]['Open']



