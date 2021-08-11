
from ta import trend
from pandas import Series
import numpy as np

from AlgorithmFactory.AlgorithmTools.CandleTools import get_ohlc


class MovingAverage:

    def __init__(self, data, ma_type, price_type, window):
        self.ma_type = ma_type
        self.price_type = price_type
        self.window = window
        self.price = self.get_price(data, self.price_type)
        self.values = self.get_ma(self.price, self.ma_type, self.window)

    def update(self, data):
        price = self.get_price(data, self.price_type)
        new_value = self.get_ma(price, self.ma_type, self.window)[-1]
        self.values = np.append(self.values[1:], new_value)

    def get_values(self):
        return self.values

    @staticmethod
    def get_price(data, price_type):
        open, high, low, close = get_ohlc(data)
        price = None
        if price_type == 'Open':
            price = open
        if price_type == 'High':
            price = high
        if price_type == 'Low':
            price = low
        if price_type == 'Close':
            price = close
        return price

    @staticmethod
    def get_ma(price, ma_type, window):
        values = None
        price = Series(price)
        if ma_type == 'EMA':
            values = trend.ema_indicator(price, window)
        if ma_type == 'SMA':
            values = trend.sma_indicator(price, window)
        values = np.array(list(Series(values)))
        return values
