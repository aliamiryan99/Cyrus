from ta.momentum import rsi
from pandas import Series
import numpy as np


class RSI:

    def __init__(self, data, window):
        self.window = window
        self.values = np.array(list(Series(rsi(Series([item['Close'] for item in data]), self.window))))

    def update(self, data):
        new_value = list(Series(rsi(Series([item['Close'] for item in data]), self.window)))[-1]
        self.values = np.append(self.values[1:], new_value)

