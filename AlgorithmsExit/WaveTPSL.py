

class WaveTPSL:
    def __init__(self, win, alpha, beta):
        self.win = win
        self.alpha = alpha
        self.beta = beta

    def on_data(self, candle):
        pass

    def on_tick(self, data, position_type):    # position_type : (buy or sell)
        from statistics import mean
        import numpy as np

        localMin = [0] * len(data)
        localMax = [0] * len(data)

        for i in range(0, len(data)):
            lb = i - self.win  # lower Band
            if lb < 0:
                lb = 0
            up = i + self.win + 1  # Upper Band
            if up >= len(data):
                up = len(data)
            if data[i]['Low'] <= min([d['Low'] for d in data[lb: up]]):
                localMin[i] = i

            if data[i]['High'] >= max([d['High'] for d in data[lb: up]]):
                localMax[i] = i

        localMax = list(filter(lambda num: num != 0, localMax))
        localMin = list(filter(lambda num: num != 0, localMin))

        max_to_min = []
        min_to_max = []

        max_len = len(localMax)
        min_len = len(localMin)
        i, j = 0, 0
        while (i<max_len and j<min_len):
            while j < min_len and localMin[j] < localMax[i]:
                j += 1
            if j == min_len:
                break
            while i<max_len-1 and localMin[j] > localMax[i+1]:
                i += 1
            if i == max_len:
                break
            max_to_min.append(abs(data[localMax[i]]['High']-data[localMin[j]]['Low']))
            i, j = i+1, j+1

        i, j = 0, 0
        while (i < min_len and j < max_len):
            while j < max_len and localMax[j] < localMin[i]:
                j += 1
            if j == max_len:
                break
            while i < min_len-1 and localMax[j] > localMin[i + 1]:
                i += 1
            if i == min_len:
                break
            min_to_max.append(abs(data[localMin[i]]['Low'] - data[localMax[j]]['High']))
            i, j = i + 1, j + 1

        #find TP and SL with exponential weighting
        weights_max_to_min = np.exp(np.linspace(-1., 0., len(max_to_min)))
        weights_min_to_max = np.exp(np.linspace(-1., 0., len(min_to_max)))

        tp, sl = 0, 0
        if position_type == 'buy':
            sl = -np.average(max_to_min, weights=weights_max_to_min)
            tp = np.average(min_to_max, weights=weights_min_to_max)
        elif position_type == 'sell':
            tp = -np.average(max_to_min, weights=weights_max_to_min)
            sl = np.average(min_to_max, weights=weights_min_to_max)
        # find PreLocalMax
        prelocalMax = [0] * len(data)
        # tp = mean([d['High'] for d in Data]) - mean([d['Low'] for d in Data])
        # sl = mean([d['High'] for d in Data]) - mean([d['Low'] for d in Data])
        # for i in range(0, len(localMax)):
            # Data.High[localMax[i]]
            # a = localMin
            # prelocalMax[i] = [val for val in a if val > localMax[i]]

        # return alpha * Mean
        tp *= self.alpha
        sl *= self.beta
        return [tp, sl]

