
from AlgorithmFactory.Algorithms.Algorithm import Algorithm
from AlgorithmFactory.AlgorithmTools.CandleTools import *
from Indicators.Ichimoku import Ichimoku
from Shared.Functions import Functions


class IchimokuAlgorithm(Algorithm):

    def __init__(self, data, role, tenkan, kijun, range_filter_enable, n, m, time_frame, sequential_trade, komu_cloud_filter, senkou_span_projection):    # role : 1, 2, 3
        self.data = data

        self.ichimoku = Ichimoku(self.data, tenkan, kijun, senkou_span_projection=senkou_span_projection)
        self.ich_result = self.ichimoku.result
        self.role = role
        self.range_filter_enable = range_filter_enable
        self.n, self.m = n, m
        self.time_frame = time_frame
        self.sequential_trade = sequential_trade
        self.komu_cloud_filter = komu_cloud_filter
        self.senkou_span_projection = senkou_span_projection

        self.ichimoku_line = "TenkanSen"
        if self.role == 2:
            self.ichimoku_line = "KijunSen"

        self.line_diff = []
        for i in range(1, len(self.ich_result["TenKijun"])):
            self.line_diff.append(self.ich_result["TenKijun"][i] - self.ich_result["TenKijun"][i-1])

        self.buy_trigger = False
        self.buy_limit_price = 0
        self.sell_trigger = False
        self.sell_limit_price = 0
        self.signal_trigger = 0
        self.last_time_id = Functions.get_time_id(self.data[-1]['Time'], time_frame)
        self.pre_signal = 0

    def on_tick(self):
        if self.buy_trigger:
            if self.data[-1]['High'] >= self.buy_limit_price:
                self.buy_trigger = False
                self.pre_signal = 1
                return 1, self.buy_limit_price
        elif self.sell_trigger:
            if self.data[-1]['Low'] <= self.sell_limit_price:
                self.sell_trigger = False
                self.pre_signal = -1
                return -1, self.sell_limit_price
        return 0, 0

    def on_data(self, candle, equity):
        self.data.pop(0)

        self.ichimoku.update(self.data)

        range_market = False
        if self.range_filter_enable:
            max_price = get_max_price(self.data, self.n)
            min_price = get_min_price(self.data, self.n)
            range_price = max_price - min_price

            self.line_diff.pop(0)
            self.line_diff.append(self.ich_result["TenKijun"][-1] - self.ich_result["TenKijun"][-2])

            avg_diff = 0
            for i in range(1, self.n+1):
                avg_diff += abs(self.line_diff[-i])
            avg_diff /= self.n * range_price
            avg_diff *= 100

            if avg_diff < self.m:
                range_market = True

        if self.komu_cloud_filter:
            max_cloud, min_cloud = max(self.ich_result["SenkouSpanA"][-26], self.ich_result["SenkouSpanB"][-26]), min(self.ich_result["SenkouSpanA"][-26], self.ich_result["SenkouSpanB"][-26])

            if min_cloud < self.data[-1]['Close'] < max_cloud:
                range_market = True

        signal, price = 0, 0
        if not range_market:
            # Role 1, 2
            if self.role == 1 or self.role == 2:
                if self.data[-2]['Close'] < self.ichimoku.result[self.ichimoku_line][-2] and self.ichimoku.result[self.ichimoku_line][-1] < self.data[-1]['Close']:
                    self.sell_trigger = False
                    self.buy_trigger = True
                    self.buy_limit_price = self.data[-1]['High']

                elif self.data[-1]['Close'] < self.ichimoku.result[self.ichimoku_line][-1] and self.ichimoku.result[self.ichimoku_line][-2] < self.data[-2]['Close']:
                    self.buy_trigger = False
                    self.sell_trigger = True
                    self.sell_limit_price = self.data[-1]['Low']

                if self.sequential_trade:
                    if self.role == 2 and self.pre_signal == 1:
                        if self.data[-2]['Close'] < self.ichimoku.result['TenkanSen'][-2] and \
                                self.ichimoku.result['TenkanSen'][-1] < self.data[-1]['Close']:
                            self.sell_trigger = False
                            self.buy_trigger = True
                            self.buy_limit_price = self.data[-1]['High']
                    if self.role == 3 and self.pre_signal == -1:
                        if self.data[-1]['Close'] < self.ichimoku.result['TenkanSen'][-1] and \
                                self.ichimoku.result['TenkanSen'][-2] < self.data[-2]['Close']:
                            self.buy_trigger = False
                            self.sell_trigger = True
                            self.sell_limit_price = self.data[-1]['Low']

            # Role 3
            if self.role == 3 or self.role == 6:
                # Lower to Upper
                if (self.ich_result['TenkanSen'][-2] <= self.ich_result['KijunSen'][-2]) and\
                        (self.ich_result['TenkanSen'][-1] > self.ich_result['KijunSen'][-1]):
                    signal, price = 1, candle['Open']
                # Upper to Lower
                elif (self.ich_result['TenkanSen'][-2] >= self.ich_result['KijunSen'][-2]) and\
                        (self.ich_result['TenkanSen'][-1] < self.ich_result['KijunSen'][-1]):
                    signal, price = -1, candle['Open']

            if self.role == 6:
                if signal == 1:
                    if self.data[-1]['Close'] < self.ich_result['KijunSen'][-1]:
                        self.signal_trigger = 1
                        signal, price = 0, 0
                if signal == -1:
                    if self.data[-1]['Close'] > self.ich_result['KijunSen'][-1]:
                        self.signal_trigger = -1
                        signal, price = 0, 0

                time_id = Functions.get_time_id(candle['Time'], self.time_frame)
                if self.last_time_id != time_id:
                    if self.signal_trigger != 0:
                        signal, price = self.signal_trigger, candle['Open']
                    self.signal_trigger = 0
                    self.last_time_id = time_id

            if self.role == 8:
                max_cloud, min_cloud = max(self.ich_result["SenkouSpanA"][-self.senkou_span_projection],
                                           self.ich_result["SenkouSpanB"][-self.senkou_span_projection]),\
                                       min(self.ich_result["SenkouSpanA"][-self.senkou_span_projection],
                                           self.ich_result["SenkouSpanB"][-self.senkou_span_projection])
                pre_max_cloud, pre_min_cloud = max(self.ich_result["SenkouSpanA"][-self.senkou_span_projection-1],
                                                   self.ich_result["SenkouSpanB"][-self.senkou_span_projection-1]),\
                                               min(self.ich_result["SenkouSpanA"][-self.senkou_span_projection-1],
                                                   self.ich_result["SenkouSpanB"][-self.senkou_span_projection-1])
                if self.data[-2]['Close'] < pre_max_cloud and max_cloud < self.data[-1]['Close']:
                    self.sell_trigger = False
                    self.buy_trigger = True
                    self.buy_limit_price = self.data[-1]['High']

                elif self.data[-1]['Close'] < min_cloud and min_cloud < self.data[-2]['Close']:
                    self.buy_trigger = False
                    self.sell_trigger = True
                    self.sell_limit_price = self.data[-1]['Low']

        self.data.append(candle)

        if self.buy_trigger:
            if self.data[-1]['High'] >= self.buy_limit_price:
                self.buy_trigger = False
                self.pre_signal = 1
                return 1, self.buy_limit_price
        elif self.sell_trigger:
            if self.data[-1]['Low'] <= self.sell_limit_price:
                self.sell_trigger = False
                self.pre_signal = -1
                return -1, self.sell_limit_price

        return signal, price

