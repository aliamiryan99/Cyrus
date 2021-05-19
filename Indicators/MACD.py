from ta.trend import macd
from ta.trend import macd_signal
from pandas import Series
import numpy as np


class MACD:

    def __init__(self, data, window_slow, window_fast):
        self.window_slow = window_slow
        self.window_fast = window_fast
        self.macd_values = np.array(list(Series(macd(Series([item['Close'] for item in data]),
                                                self.window_slow, self.window_fast))))
        self.signal_values = np.array(list(Series(macd_signal(Series([item['Close'] for item in data]),
                                                     self.window_slow, self.window_fast))))

    def update(self, data):
        new_value = list(Series(macd(Series([item['Close'] for item in data]),
                                     self.window_slow, self.window_fast)))[-1]
        self.macd_values = np.append(self.macd_values[1:], new_value)
        new_value = list(Series(macd_signal(Series([item['Close'] for item in data]),
                                            self.window_slow, self.window_fast)))[-1]
        self.signal_values = np.append(self.signal_values[1:], new_value)

