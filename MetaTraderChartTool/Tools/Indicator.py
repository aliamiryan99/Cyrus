
from MetaTraderChartTool.BasicChartTools import BasicChartTools
from AlgorithmFactory.AlgorithmTools.LocalExtermums import *
from MetaTraderChartTool.Tools.Tool import Tool


class Indicator(Tool):

    def __init__(self, data):
        super().__init__(data)

        self.indicator_values = []

        for i in range(len(data)):
            self.indicator_values.append((self.data[i]['Time'], self.data[i]['High'] + (self.data[i]['High']-self.data[i]['Low'])))

    def draw(self, chart_tool: BasicChartTools):

        times1, times2, prices1, prices2, names1 = [], [], [], [], []
        for i in range(len(self.indicator_values)-1):
            times1.append(self.indicator_values[i][0])
            times2.append(self.indicator_values[i+1][0])
            prices1.append(self.indicator_values[i][1])
            prices2.append(self.indicator_values[i+1][1])
            names1.append(f"IndicatorLine{i}")

        chart_tool.trend_line(names1, times1, prices1, times2, prices2)
