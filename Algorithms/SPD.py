
from AlgorithmTools.CandleTools import get_body_mean


class SharpPointDetection:

    def __init__(self, data_history, mean_alpha, candle_bound):
        self.mean_alpha = mean_alpha
        self.data_window = data_history
        self.candle_bound = candle_bound
        self.body_mean = get_body_mean(self.data_window[:-1], len(self.data_window)-1)

    def on_tick(self):
        return 0, 0

    def on_data(self, candle, cash):
        self.body_mean -= abs(self.data_window[0]['Open'] - self.data_window[0]['Close']) / (len(self.data_window) - 1)
        self.body_mean += abs(self.data_window[-1]['Open'] - self.data_window[-1]['Close']) / (len(self.data_window) - 1)
        signal = self.pattern_detect()
        self.data_window.pop(0)
        self.data_window.append(candle)
        return signal, self.data_window[-1]['Open']

    def pattern_detect(self):
        if self.data_window[-1]['Close'] > self.data_window[-1]['Open']:
            n = -1
            for i in range(2, len(self.data_window)):
                if self.data_window[-i]['Close'] > self.data_window[-1]['Close']:
                    n = i
                    break
            if n > self.candle_bound:
                min_price = self.data_window[-1]['Low']
                for i in range(n+1):
                    if self.data_window[-i]['Low'] < min_price:
                        min_price = self.data_window[-i]['Low']
                diff_price = abs(self.data_window[-1]['Close'] - min_price)
                diff_ratio = diff_price / n
                if diff_ratio >= self.body_mean * self.mean_alpha:
                    return 1
        if self.data_window[-1]['Close'] < self.data_window[-1]['Open']:
            n = -1
            for i in range(2, len(self.data_window)):
                if self.data_window[-i]['Close'] < self.data_window[-1]['Close']:
                    n = i
                    break
            if n > self.candle_bound:
                max_price = self.data_window[-1]['High']
                for i in range(n + 1):
                    if self.data_window[-i]['High'] > max_price:
                        max_price = self.data_window[-i]['High']
                diff_price = abs(self.data_window[-1]['Close'] - max_price)
                diff_ratio = diff_price / n
                if diff_ratio >= self.body_mean * self.mean_alpha:
                    return -1






