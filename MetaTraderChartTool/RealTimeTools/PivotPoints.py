from MetaTraderChartTool.BasicChartTools import BasicChartTools
from MetaTraderChartTool.RealTimeTools.RealTimeTool import RealTimeTool

from AlgorithmFactory.AlgorithmTools.LocalExtermums import *


class PivotPoints(RealTimeTool):

    def __init__(self, chart_tool: BasicChartTools, data, window, mode):
        super().__init__(chart_tool, data)

        self.window = window
        self.mode = mode

        self.local_min, self.local_max = get_local_extermums(self.data, window, mode)

        self.last_local_min, self.last_local_max = self.local_min[-1], self.local_max[-1]
        self.last_min_id, self.last_max_id = 1, 1

        self.draw_local_extremum(self.local_min, self.local_max)

    def on_tick(self):
        pass

    def on_data(self, candle):
        self.data.pop(0)

        self.local_min, self.local_max = update_local_extremum_list(self.data, self.local_min, self.local_max, self.window, self.mode)
        self.last_local_min, self.last_local_max = self.last_local_min-1, self.last_local_max-1

        if self.local_min[-1] != self.last_local_min:
            self.draw_local_extremum([self.local_min[-1]], [])
            self.last_local_min = self.local_min[-1]
            print(f"Local Min Time {self.data[self.local_min[-1]]['Time']}")
        if self.local_max[-1] != self.last_local_max:
            self.draw_local_extremum([], [self.local_max[-1]])
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
            self.chart_tool.text(names1, times1, prices1, texts1, anchor=self.chart_tool.EnumAnchor.Top, color="12,83,211")
        if len(local_max) != 0:
            times2, prices2, texts2, names2 = [], [], [], []
            for i in range(len(local_max)):
                times2.append(self.data[local_max[i]]['Time'])
                prices2.append(self.data[local_max[i]]['High'])
                texts2.append(self.data[local_max[i]]['High'])
                names2.append(f"LocalMaxPython{self.last_max_id}")
                self.last_max_id += 1
            self.chart_tool.text(names2, times2, prices2, texts2, anchor=self.chart_tool.EnumAnchor.Bottom, color="211,83,12")
