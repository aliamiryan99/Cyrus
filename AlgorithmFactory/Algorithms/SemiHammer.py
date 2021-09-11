
from AlgorithmFactory.AlgorithmTools.CandleTools import *


class SemiHammer:

    def __init__(self, data_history, window_size, alpha, detect_mode, trigger_threshold):
        # Data window, moving average window
        self.alpha = alpha
        self.detect_mode = detect_mode
        self.trigger_threshold = trigger_threshold
        self.window_size = window_size
        len_window = len(data_history)
        if len_window <= self.window_size:
            raise Exception("window len should be greater than window size")
        self.data_window = data_history[-self.window_size-5:]

        self.trigger_signal = 0
        self.trigger_cnt = 0
        self.candle_buy_submitted = False
        self.candle_sell_submitted = False

    def on_tick(self):
        if self.trigger_signal == 1:
            if self.data_window[-1]['Close'] > self.data_window[-self.trigger_cnt-1]['High']:
                self.candle_buy_submitted = True
                self.trigger_signal = 0
                self.trigger_cnt = 0
                return 1, self.data_window[-self.trigger_cnt-1]['High']
        elif self.trigger_signal == -1:
            if self.data_window[-1]['Close'] < self.data_window[-self.trigger_cnt-1]['Low']:
                self.candle_sell_submitted = True
                self.trigger_signal = 0
                self.trigger_cnt = 0
                return -1, self.data_window[-self.trigger_cnt-1]['Low']
        return 0, 0

    def on_data(self, candle, cash):
        self.candle_buy_submitted = False
        self.candle_sell_submitted = False
        trigger = self.semi_hammer_detect()
        if trigger != 0:
            self.trigger_signal = trigger
            self.trigger_cnt = 1
        else:
            if self.trigger_cnt == self.trigger_threshold:
                self.trigger_signal = 0
            elif self.trigger_signal != 0:
                self.trigger_cnt += 1
        self.data_window.pop(0)
        self.data_window.append(candle)
        return 0, 0

    def semi_hammer_detect(self):  # detect mode : 1, ...
        data = self.data_window

        bottom_candle, top_candle = get_bottom_top(self.data_window)

        if self.detect_mode == 1:
            if bottom_candle[-1] - data[-1]['Low'] > self.alpha * abs(data[-1]['Close'] - data[-1]['Open']):
                if data[-2]['Close'] < data[-2]['Open']:
                    return 1

            if data[-1]['High'] - top_candle[-1] > self.alpha * abs(data[-1]['Close'] - data[-1]['Open']):
                if data[-2]['Close'] > data[-2]['Open']:
                    return -1

        return 0
