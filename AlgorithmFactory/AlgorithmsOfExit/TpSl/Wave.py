
from AlgorithmFactory.AlgorithmTools.LocalExtermums import *


class Wave:
    def __init__(self, data, extremum_window, extremum_mode, alpha, beta):
        self.data_window = data
        self.extremum_window = extremum_window
        self.extremum_mode = extremum_mode
        self.alpha = alpha
        self.beta = beta

        self.local_min_price, self.local_max_price = get_local_extermums(self.data_window[:-1], self.extremum_window,
                                                                         self.extremum_mode)

    def on_data(self, candle):
        self.update_local_extremum()
        self.data_window.pop(0)
        self.data_window.append(candle)

    def on_tick(self, data, position_type):    # position_type : (buy or sell)

        max_to_min = []
        min_to_max = []

        min_len = len(self.local_min_price)
        max_len = len(self.local_max_price)
        i, j = 0, 0
        while i < max_len and j < min_len:
            while j < min_len and self.local_min_price[j] < self.local_max_price[i]:
                j += 1
            if j == min_len:
                break
            while i < max_len-1 and self.local_min_price[j] > self.local_max_price[i+1]:
                i += 1
            if i == max_len:
                break
            max_to_min.append(abs(data[self.local_max_price[i]]['High']-data[self.local_min_price[j]]['Low']))
            i, j = i+1, j+1

        i, j = 0, 0
        while i < min_len and j < max_len:
            while j < max_len and self.local_max_price[j] < self.local_min_price[i]:
                j += 1
            if j == max_len:
                break
            while i < min_len-1 and self.local_max_price[j] > self.local_min_price[i + 1]:
                i += 1
            if i == min_len:
                break
            min_to_max.append(abs(data[self.local_min_price[i]]['Low'] - data[self.local_max_price[j]]['High']))
            i, j = i + 1, j + 1

        #find TP and SL with exponential weighting
        weights_max_to_min = np.exp(np.linspace(-1., 0., len(max_to_min)))
        weights_min_to_max = np.exp(np.linspace(-1., 0., len(min_to_max)))

        tp, sl = 0, 0
        if position_type == 'Buy':
            sl = -np.average(max_to_min, weights=weights_max_to_min)
            tp = np.average(min_to_max, weights=weights_min_to_max)
        elif position_type == 'Sell':
            tp = -np.average(max_to_min, weights=weights_max_to_min)
            sl = np.average(min_to_max, weights=weights_min_to_max)

        # return alpha * Mean
        tp *= self.alpha
        sl *= self.beta
        return [tp, sl]

    def update_local_extremum(self):
        self.local_min_price, self.local_max_price = update_local_extremum_list(self.data_window, self.local_min_price,
                                                                                self.local_max_price,
                                                                                self.extremum_window, self.extremum_mode)