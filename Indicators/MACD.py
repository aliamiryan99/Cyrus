from ta.trend import macd
from ta.trend import macd_signal
from pandas import Series
import numpy as np


class MACD:

    def __init__(self, price, window_slow, window_fast):
        self.window_slow = window_slow
        self.window_fast = window_fast
        self.price = price
        self.macd_values = np.array(list(Series(macd(Series(price),
                                                self.window_slow, self.window_fast))))
        self.signal_values = np.array(list(Series(macd_signal(Series(price),
                                                     self.window_slow, self.window_fast))))

    def update(self, value):
        self.price.pop(0)
        self.price.append(value)
        new_value = list(Series(macd(Series(self.price),
                                     self.window_slow, self.window_fast)))[-1]
        self.macd_values = np.append(self.macd_values[1:], new_value)
        new_value = list(Series(macd_signal(Series(self.price),
                                            self.window_slow, self.window_fast)))[-1]
        self.signal_values = np.append(self.signal_values[1:], new_value)

    def get_values(self):
        return self.macd_values, self.signal_values

