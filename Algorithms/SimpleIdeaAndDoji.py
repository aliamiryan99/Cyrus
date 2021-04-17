
from Algorithms.SimpleIdea import SimpleIdea
from Algorithms.Doji import Doji


class SIAndDojiAlgorithm:

    def __init__(self, symbol, data_history, win_inc, win_dec, shadow_threshold, body_threshold, doji_win, doji_detect_mode, doji_candle_mode):
        # Data window, moving average window
        self.win_inc = win_inc
        self.win_dec = win_dec
        self.window_size = max(win_inc, win_dec)
        self.symbol = symbol
        self.shadow_threshold = shadow_threshold
        self.body_threshold = body_threshold
        self.win = doji_win
        self.detect_mode = doji_detect_mode
        self.candle_mode = doji_candle_mode
        len_window = len(data_history)
        if len_window <= self.window_size:
            raise Exception("window len should be greater than window size")
        self.data_window = data_history[-self.window_size-5:]
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

    def on_data(self, candle, cash):
        self.doji_trigger = Doji.doji_detect(self.data_window, self.win, self.detect_mode, self.candle_mode)
        signal = SimpleIdea.simpleIdea(self.symbol, self.data_window, self.win_inc, self.win_dec,
                                       self.shadow_threshold, self.body_threshold)
        self.data_window.pop(0)
        self.data_window.append(candle)
        return signal, self.data_window[-1]['Open']



