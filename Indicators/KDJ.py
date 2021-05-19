
from AlgorithmTools.CandleTools import get_ohlc


class KDJ:

    def __init__(self, data, k_periods, d_periods):
        self.data = data
        self.k_periods, self.d_periods = k_periods, d_periods
        self.open, self.high, self.low, self.close = get_ohlc(data)
        self.k_values, self.d_values, self.j_values = self.calc()

    def update(self, data):
        self.open, self.high, self.low, self.close = get_ohlc(data)
        self.k_values, self.d_values, self.j_values = self.calc()

    def get_values(self):
        return self.k_values, self.d_values, self.j_values

    def calc(self):
        y = 0
        # k_periods are 14 array start from 0 index
        array_highest = []
        for x in range(0, self.high.size - self.k_periods):
            z = self.high[y]
            for j in range(0, self.k_periods):
                if z < self.high[y + 1]:
                    z = self.high[y + 1]
                y = y + 1
            # creating list highest of k periods
            array_highest.append(z)
            y = y - (self.k_periods - 1)
        y = 0
        array_lowest = []
        for x in range(0, self.low.size - self.k_periods):
            z = self.low[y]
            for j in range(0, self.k_periods):
                if z > self.low[y + 1]:
                    z = self.low[y + 1]
                y = y + 1
            # creating list lowest of k periods
            array_lowest.append(z)
            y = y - (self.k_periods - 1)

        # KDJ (K line, D line, J line)
        k_value = []
        for x in range(self.k_periods, self.close.size):
            k = ((self.close[x] - array_lowest[x - self.k_periods]) * 100 / (
                        array_highest[x - self.k_periods] - array_lowest[x - self.k_periods]))
            k_value.append(k)
        y = 0
        # d_periods for calculate d values
        d_value = [None, None]
        for x in range(0, len(k_value) - self.d_periods + 1):
            sum = 0
            for j in range(0, self.d_periods):
                sum = k_value[y] + sum
                y = y + 1
            mean = sum / self.d_periods
            # d values for %d line
            d_value.append(mean)
            y = y - (self.d_periods - 1)

        j_value = [None, None]
        for x in range(0, len(d_value) - self.d_periods + 1):
            j = (d_value[x + 2] * 3) - (k_value[x + 2] * 2)
            # j values for %j line
            j_value.append(j)

        k_value = k_value[2:]
        d_value = d_value[2:]
        j_value = j_value[2:]

        return k_value, d_value, j_value



