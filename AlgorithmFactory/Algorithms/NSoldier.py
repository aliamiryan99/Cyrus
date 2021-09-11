

class NSoldier:

    def __init__(self, symbol, data_history, window):
        # Data window, moving average window
        self.window = window
        self.symbol = symbol
        len_window = len(data_history)
        if len_window <= self.window:
            raise Exception("window len should be greater than window size")
        self.data_window = data_history[-self.window-5:]

    def on_tick(self):
        return 0, 0

    def on_data(self, candle, cash):
        signal = self.sequence_find()
        self.data_window.pop(0)
        self.data_window.append(candle)
        return signal, self.data_window[-1]['Open']

    def sequence_find(self):

        cnt = 0
        if self.data_window[-self.window-1]['Close'] < self.data_window[-self.window-1]['Open']:
            for j in range(0, self.window):
                if self.data_window[-j-1]['Close'] > self.data_window[-j-1]['Open']:
                    cnt += 1
            if cnt == self.window:
                return 1

        cnt = 0
        if self.data_window[-self.window-1]['Close'] > self.data_window[-self.window-1]['Open']:
            for j in range(0, self.window):
                if self.data_window[-j-1]['Close'] < self.data_window[-j-1]['Open']:
                    cnt += 1
            if cnt == self.window:
                return -1

        return 0

