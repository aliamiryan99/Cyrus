
from Algorithms.Doji import Doji


class DojiAlgorithm:

    def __init__(self, data_history, win, detect_mode, candle_mode):
        # Data window, moving average window
        self.win = win
        self.detect_mode = detect_mode
        self.candle_mode = candle_mode
        len_window = len(data_history)
        if len_window <= self.win:
            raise Exception("window len should be greater than window size")
        self.data_window = data_history[-self.win-5:]
        self.doji_trigger = 0

    def on_tick(self):
        if self.doji_trigger == 1:
            if self.data_window[-1]['High'] > self.data_window[-2]['High']:
                self.doji_trigger = 0
                return 1, self.data_window[-2]['High']
        elif self.doji_trigger == -1:
            if self.data_window[-1]['Low'] < self.data_window[-2]["Low"]:
                self.doji_trigger = 0
                return -1, self.data_window[-2]['Low']
        return 0, 0

    def on_data(self, candle):
        self.doji_trigger = Doji.doji_detect(self.data_window, self.win, self.detect_mode, self.candle_mode)
        self.data_window.pop(0)
        self.data_window.append(candle)
        return 0, 0

