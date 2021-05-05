
from Algorithms.SimpleIdea import SimpleIdea
from AlgorithmTools.LocalExtermums import *
from Simulation.Config import Config

class SSIAlgorithm:

    def __init__(self, symbol, data_history, win_inc, win_dec, shadow_threshold, body_threshold, mode, mean_window, extremum_window, extremum_mode, huge_detection_window, alpha, gap_threshold):
        # Data window, moving average window
        self.win_inc = win_inc
        self.win_dec = win_dec
        self.mode = mode
        self.mean_window = mean_window
        self.extremum_window = extremum_window
        self.extremum_mode = extremum_mode
        self.huge_detection_window = huge_detection_window
        self.alpha = alpha
        self.window_size = max(win_inc, win_dec)
        self.symbol = symbol
        self.shadow_threshold = shadow_threshold
        self.body_threshold = body_threshold
        self.gap_threshold = gap_threshold * 10 ** -Config.symbols_pip[symbol]
        len_window = len(data_history)
        if len_window <= self.window_size:
            raise Exception("window len should be greater than window size")
        self.data_window = data_history[:-1]

        self.local_min_price, self.local_max_price = get_local_extermums(self.data_window[:-1], self.extremum_window,
                                                                         self.extremum_mode)

    def on_tick(self):
        return 0, 0

    def on_data(self, candle, cash):
        self.update_local_extremum()
        signal = SimpleIdea.simpleIdea(self.symbol, self.data_window, self.win_inc, self.win_dec,
                                       self.shadow_threshold, self.body_threshold, self.mode, self.mean_window)
        has_huge = False
        if signal == 1:
            has_huge = self.huge_detection('buy')
        elif signal == -1:
            has_huge = self.huge_detection('sell')
        if not has_huge:
            signal = 0
        self.data_window.pop(0)
        self.data_window.append(candle)
        if abs(self.data_window[-1]['Open'] - self.data_window[-2]['Close']) > self.gap_threshold:
            signal = 0
        return signal, self.data_window[-1]['Open']

    def update_local_extremum(self):
        self.local_min_price = update_local_extremum(self.local_min_price)
        self.local_max_price = update_local_extremum(self.local_max_price)

        window_size = self.extremum_window*4
        new_local_min_price_left, new_local_max_price_left = get_local_extermums(self.data_window[-window_size:], self.extremum_window, self.extremum_mode)

        self.local_min_price = update_new_local_extremum(self.local_min_price, new_local_min_price_left, len(self.data_window), window_size)
        self.local_max_price = update_new_local_extremum(self.local_max_price, new_local_max_price_left, len(self.data_window), window_size)

    def huge_detection(self, type):
        huge_detected = False
        if type == 'buy':
            local_extremum = self.local_max_price
        else:
            local_extremum = self.local_min_price
        for i in range(local_extremum[-1], len(self.data_window)):
            if (type == 'buy' and self.data_window[i]['Close'] - self.data_window[i]['Open'] < 0) or (type == 'sell' and self.data_window[i]['Close'] - self.data_window[i]['Open'] > 0):
                is_huge = True
                for j in range(i - self.huge_detection_window, i):
                    if abs(self.data_window[j]['Close'] - self.data_window[j]['Open']) > self.alpha * abs(self.data_window[i]['Close'] - self.data_window[i]['Open']):
                        is_huge = False
                        break
                if is_huge:
                    huge_detected = True
                    break
        return huge_detected
