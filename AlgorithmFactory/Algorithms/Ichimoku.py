
from AlgorithmFactory.Algorithms.Algorithm import Algorithm
from Indicators.Ichimoku import Ichimoku


class IchimokuAlgorithm(Algorithm):

    def __init__(self, data):
        self.data = data

        self.ichimoku = Ichimoku(self.data)
        self.ich_result = self.ichimoku.result

        self.buy_trigger = False
        self.buy_limit_price = 0
        self.sell_trigger = False
        self.sell_limit_price = 0

    def on_tick(self):
        if self.buy_trigger:
            if self.data[-1]['Close'] >= self.buy_limit_price:
                self.buy_trigger = False
                return 1, self.buy_limit_price
        elif self.sell_trigger:
            if self.data[-1]['Close'] <= self.sell_limit_price:
                self.sell_trigger = False
                return -1, self.sell_limit_price
        return 0, 0

    def on_data(self, candle, equity):
        self.data.pop(0)

        self.ichimoku.update(self.data)

        # Role 1
        # if self.data[-1]['Open'] < self.ichimoku.result['TenkanSen'][-1] < self.data[-1]['Close']:
        #     self.sell_trigger = False
        #     self.buy_trigger = True
        #     self.buy_limit_price = self.data[-1]['High']
        #
        # elif self.data[-1]['Close'] < self.ichimoku.result['TenkanSen'][-1] < self.data[-1]['Open']:
        #     self.buy_trigger = False
        #     self.sell_trigger = True
        #     self.sell_limit_price = self.data[-1]['Low']

        self.data.append(candle)
        # Role 2
        # Lower to Upper
        if (self.ich_result['TenkanSen'][-2] <= self.ich_result['KijunSen'][-2]) and\
                (self.ich_result['TenkanSen'][-1] > self.ich_result['KijunSen'][-1]):
            return 1, candle['Open']
        # Upper to Lower
        elif (self.ich_result['TenkanSen'][-2] >= self.ich_result['KijunSen'][-2]) and\
                (self.ich_result['TenkanSen'][-1] < self.ich_result['KijunSen'][-1]):
            return -1, candle['Open']


        return 0, 0

