
from Indicators.Stochastic import Stochastic


class StochasticTrailing:
    def __init__(self, data_window, upper_band, lower_band, stoch_window):
        self.data_window = data_window
        self.upper_band = upper_band
        self.lower_band = lower_band
        self.stoch_window = stoch_window

        price = [d['Close'] for d in data_window[:-1]]
        self.indicator = Stochastic(price, stoch_window, 3, 3, 'K')

        self.is_huge_buy = False
        self.is_huge_sell = False

    def on_data(self, history):
        self.indicator.update(history)
        self.data_window.append(history[-1])

    def on_tick(self, history, entry_point, position_type, time):
        if position_type == 'Buy':
            if self.indicator.values[-1] > self.upper_band:
                return True, history[-1]['Close']
        elif position_type == 'Sell':
            if self.indicator.values[-1] < self.lower_band:
                return True, history[-1]['Close']
        return False, 0

    def on_tick_end(self):
        pass
