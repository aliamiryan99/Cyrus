

class HighLowBreakAlgorithm:

    def __init__(self, symbol, data_history, window_size, pivot):
        # Data window, moving average window
        self.window_size = window_size
        self.pivot = pivot
        len_window = len(data_history)
        if len_window <= self.window_size:
            raise Exception("window len should be greater than window size")
        self.data_window = data_history[-self.window_size-5:]
        self.trigger_signal = 0
        self.signal_triggered_buy = False
        self.signal_triggered_sell = False
        self.candle_buy_submitted = False
        self.candle_sell_submitted = False

    def on_tick(self):
        if self.signal_triggered_buy == 1 and not self.candle_buy_submitted:
            if self.data_window[-1]['Close'] > self.data_window[-self.pivot - 1]['High']:
                self.candle_buy_submitted = True
                return 1, self.data_window[-1]['Close']
        if self.signal_triggered_sell == -1 and not self.candle_sell_submitted:
            if self.data_window[-1]['Close'] < self.data_window[-self.pivot - 1]['Low']:
                self.candle_sell_submitted = True
                return -1, self.data_window[-1]['Close']
        return 0, 0

    def on_data(self, candle, cash):
        self.candle_sell_submitted = False
        self.candle_buy_submitted = False
        self.signal_triggered_buy = self.detect_pattern('buy')
        self.signal_triggered_sell = self.detect_pattern('sell')
        self.data_window.pop(0)
        self.data_window.append(candle)
        return 0, 0

    def detect_pattern(self, type):
        if type == 'buy':
            detection = 1
            for i in range(1, self.window_size+1):
                if self.data_window[-i]['High'] >= self.data_window[-i-1]['High']:
                    detection = 0
                    break
            return detection
        elif type == 'sell':
            detection = -1
            for i in range(1, self.window_size+1):
                if self.data_window[-i]['Low'] <= self.data_window[-i-1]['Low']:
                    detection = 0
                    break
            return detection



