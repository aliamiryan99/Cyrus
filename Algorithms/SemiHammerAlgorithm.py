
from Algorithms.SemiHammer import SemiHammer


class SemiHammerAlgorithm:

    def __init__(self, symbol, data_history, window_size, alpha, detect_mode, trigger_threshold):
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

    def on_tick(self):
        if self.trigger_signal == 1:
            if self.data_window[-1]['Close'] > self.data_window[-self.trigger_cnt-1]['High']:
                return 1, self.data_window[-self.trigger_cnt-1]['High']
        elif self.trigger_signal == -1:
            if self.data_window[-1]['Close'] < self.data_window[-self.trigger_cnt-1]['Low']:
                return -1, self.data_window[-self.trigger_cnt-1]['Low']
        return 0, 0

    def on_data(self, candle, cash):
        trigger = SemiHammer.semi_hammer_detect(self.data_window, self.detect_mode, self.alpha)
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



