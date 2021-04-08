

class HighLowBreakAlgorithm:

    def __init__(self, symbol, data_history, window_size):
        # Data window, moving average window
        self.window_size = window_size
        len_window = len(data_history)
        if len_window <= self.window_size:
            raise Exception("window len should be greater than window size")
        self.data_window = data_history[-self.window_size-5:]
        self.trigger_signal = 0
        self.signal_triggered = False

    def on_tick(self):
        if not self.signal_triggered:
            if self.data_window[-1]['Close'] > self.data_window[-2]['High']:
                self.signal_triggered = True
                return 1, self.data_window[-1]['Close']
            if self.data_window[-1]['Close'] < self.data_window[-2]['Low']:
                self.signal_triggered = True
                return -1, self.data_window[-1]['Close']
        return 0, 0

    def on_data(self, candle):
        self.signal_triggered = False
        self.data_window.pop(0)
        self.data_window.append(candle)
        return 0, 0



