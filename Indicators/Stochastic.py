from ta.momentum import stochrsi_k
from ta.momentum import stochrsi_d
from pandas import Series
import numpy as np


class Stochastic:

    def __init__(self, data, window, smooth1, smooth2, type):
        self.window = window
        self.smooth1, self.smooth2 = smooth1, smooth2
        self.type = type
        if type == 'K':
            self.values = np.array(list(Series(stochrsi_k(Series([item['Close'] for item in data]), self.window, self.smooth1, self.smooth2))))
        elif type == 'D':
            self.values = np.array(list(Series(stochrsi_d(Series([item['Close'] for item in data]), self.window, self.smooth1, self.smooth2))))

    def update(self, data):
        new_value = 0
        if self.type == 'K':
            new_value = list(Series(stochrsi_k(Series([item['Close'] for item in data]), self.window)))[-1]
        elif self.type == 'D':
            new_value = list(Series(stochrsi_k(Series([item['Close'] for item in data]), self.window)))[-1]
        self.values = np.append(self.values[1:], new_value)

