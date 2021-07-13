from ta.momentum import rsi
from pandas import Series
import numpy as np


class RSI:

    def __init__(self, price, window):
        self.price = price
        self.window = window
        self.values = np.array(list(Series(rsi(Series(price), self.window))))

    def update(self, value):
        self.price.pop(0)
        self.price.append(value)
        new_value = list(Series(rsi(Series([self.price]), self.window)))[-1]
        self.values = np.append(self.values[1:], new_value)

    def get_values(self):
        return self.values

