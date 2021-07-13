

from ta.momentum import rsi
from ta.trend import ema_indicator
from pandas import Series
import numpy as np


class AMA:

    def __init__(self, price, period, period_sf):
        self.period = period
        self.period_sf = period_sf
        self.price = price
        self.values = Series(rsi(Series(price), self.period))
        self.values = np.array(list(ema_indicator(self.values, self.period_sf)))

    def update(self, value):
        self.price = np.append(self.price[1:], value)
        new_values = list(Series(rsi(Series(self.price),
                                     self.period)))
        new_value = ema_indicator(new_values, self.period_sf)[-1]
        self.values = np.append(self.values[1:], new_value)

    def get_values(self):
        return self.values

