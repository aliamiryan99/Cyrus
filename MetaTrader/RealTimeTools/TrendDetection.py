from MetaTrader.MetaTraderBase import MetaTraderBase
from MetaTrader.RealTimeTools.RealTimeTool import RealTimeTool

from AlgorithmFactory.AlgorithmTools.LocalExtermums import *
from AlgorithmFactory.AlgorithmPackages.Trend.TrendDetection import *


class TrendDetection(RealTimeTool):

    def __init__(self, chart_tool: MetaTraderBase, data, window_left, window_right, mode):
        super().__init__(chart_tool, data)

        self.window = window_left
        self.mode = mode

        open , high, low, close = get_ohlc(data)

        self.local_min, self.local_max = get_local_extermums_asymetric(self.data, window_left, window_right, mode)

        bullish, bearish = detect_trend(self.local_max, self.local_min, high, low)

        self.draw_trend_starts(bullish, "Bullish", "20,20,200")
        self.draw_trend_starts(bearish, "Bearish", "200,20,20")

        self.last_local_min, self.last_local_max = self.local_min[-1], self.local_max[-1]
        self.last_min_id, self.last_max_id = 1, 1
        self.last_min_delete, self.last_max_delete = 1, 1

        self.draw_local_extremum(self.local_min, self.local_max)

    def on_tick(self, time, bid, ask):
        pass

    def on_data(self, candle):
        self.data.pop(0)

        self.local_min, self.local_max = update_local_extremum_list(self.data, self.local_min, self.local_max, self.window, self.mode)
        self.last_local_min, self.last_local_max = self.last_local_min-1, self.last_local_max-1

        if self.local_min[-1] != self.last_local_min:
            self.draw_local_extremum([self.local_min[-1]], [])
            self.chart_tool.delete([f'LocalMinPython{self.last_min_delete}'])
            self.last_min_delete += 1
            self.last_local_min = self.local_min[-1]
            print(f"Local Min Time {self.data[self.local_min[-1]]['Time']}")
        if self.local_max[-1] != self.last_local_max:
            self.draw_local_extremum([], [self.local_max[-1]])
            self.chart_tool.delete([f'LocalMaxPython{self.last_max_delete}'])
            self.last_max_delete += 1
            self.last_local_max = self.local_max[-1]
            print(f"Local Max Time {self.data[self.local_max[-1]]['Time']}")

        self.data.append(candle)

    def draw_local_extremum(self, local_min, local_max):

        if len(local_min) != 0:
            times1, prices1, texts1, names1 = [], [], [], []
            for i in range(len(local_min)):
                times1.append(self.data[local_min[i]]['Time'])
                prices1.append(self.data[local_min[i]]['Low'])
                texts1.append(self.data[local_min[i]]['Low'])
                names1.append(f"LocalMinPython{self.last_min_id}")
                self.last_min_id += 1
            self.chart_tool.arrow_up(names1, times1, prices1, anchor=self.chart_tool.EnumArrowAnchor.Top, color="12,83,211")
        if len(local_max) != 0:
            times2, prices2, texts2, names2 = [], [], [], []
            for i in range(len(local_max)):
                times2.append(self.data[local_max[i]]['Time'])
                prices2.append(self.data[local_max[i]]['High'])
                texts2.append(self.data[local_max[i]]['High'])
                names2.append(f"LocalMaxPython{self.last_max_id}")
                self.last_max_id += 1
            self.chart_tool.arrow_down(names2, times2, prices2, anchor=self.chart_tool.EnumArrowAnchor.Bottom, color="211,83,12")

    def draw_trend_starts(self, starts, type, color):
        names = [f"{type} trend {i}" for i in range(len(starts))]
        times = [self.data[starts[i]]['Time'] for i in range(len(starts))]
        self.chart_tool.v_line(names, times, color=color)
