
import numpy as np
from pandas import Series
from ta.momentum import stochrsi_k


class Stochastic:

    def __init__(self, symbol, data_history, upper_band_indicator, lower_band_indicator, price_mode, stoch_window):
        # Data window, moving average window
        self.data_window = data_history[1:]

        self.symbol = symbol
        self.price_mode = price_mode
        self.upper_band = upper_band_indicator
        self.lower_band = lower_band_indicator
        self.stoch_window = stoch_window

        indicator = np.array(list(Series(stochrsi_k(Series([item['Close'] for item in data_history[:-1]]), self.stoch_window))))

        self.max_indicator = indicator
        self.min_indicator = indicator

        self.buy_trigger = False
        self.sell_trigger = False
        self.candle_buy_submitted = False
        self.candle_sell_submitted = False
        self.candle_trend = 0

    def on_tick(self):
        if self.buy_trigger and not self.candle_buy_submitted:
            price = 0
            if self.price_mode == 1:    # High Low
                price = self.data_window[-2]['High']
            elif self.price_mode == 2:   # Top Bottom
                price = max(self.data_window[-2]['Open'], self.data_window[-2]['Close'])
            if self.data_window[-1]['High'] >= price:
                self.candle_buy_submitted = True
                self.buy_trigger = False
                return 1, price
        if self.sell_trigger and not self.candle_sell_submitted:
            price = 0
            if self.price_mode == 1:
                price = self.data_window[-2]['Low']
            elif self.price_mode == 2:
                price = min(self.data_window[-2]['Open'], self.data_window[-2]['Close'])
            if self.data_window[-1]['Low'] <= price:
                self.candle_sell_submitted = True
                self.sell_trigger = False
                return -1, price
        return 0, 0

    def on_data(self, candle, cash):
        self.candle_buy_submitted = False
        self.candle_sell_submitted = False
        self.update_indicator()
        if self.max_indicator[-1] >= self.upper_band:
            self.sell_trigger = True
        if self.min_indicator[-1] <= self.lower_band:
            self.buy_trigger = True
        self.data_window.pop(0)
        self.data_window.append(candle)
        return 0, 0

    def update_indicator(self):
        indicator = list(Series(stochrsi_k(Series([item['Close'] for item in self.data_window]), self.stoch_window)))
        last_max_indicator = indicator
        last_min_indicator = indicator

        self.max_indicator = self.max_indicator[1:]
        self.max_indicator = np.append(self.max_indicator, last_max_indicator[-1])
        self.min_indicator = self.min_indicator[1:]
        self.min_indicator = np.append(self.min_indicator, last_min_indicator[-1])




