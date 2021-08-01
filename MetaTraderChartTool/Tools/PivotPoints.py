
from MetaTraderChartTool.BasicChartTools import BasicChartTools
from AlgorithmTools.LocalExtermums import *


class PivotPoints:

    def __init__(self, data, extremum_window, extremum_mode):
        self.data = data

        self.local_min, self.local_max = get_local_extermums(data, extremum_window, extremum_mode)

    def draw(self, chart_tool: BasicChartTools):

        times1, prices1, texts1, names1 = [], [], [], []
        times2, prices2, texts2, names2 = [], [], [], []
        for i in range(len(self.local_min)):
            times1.append(self.data[self.local_min[i]]['Time'])
            prices1.append(self.data[self.local_min[i]]['Low'])
            texts1.append(self.data[self.local_min[i]]['Low'])
            names1.append(f"LocalMinPython{i}")
        for i in range(len(self.local_max)):
            times2.append(self.data[self.local_max[i]]['Time'])
            prices2.append(self.data[self.local_max[i]]['High'])
            texts2.append(self.data[self.local_max[i]]['High'])
            names2.append(f"LocalMaxPython{i}")

        chart_tool.text(names1, times1, prices1, texts1, anchor=chart_tool.EnumAnchor.Top, color="12,83,211")
        chart_tool.text(names2, times2, prices2, texts2, anchor=chart_tool.EnumAnchor.Bottom, color="211,83,12")

        # chart_tool.rectangle_label(["RectLabel1"], [20], [40], [120], [40], back_color="113,105,105", color="200,199,199", border=chart_tool.EnumBorder.Sunken)
        # chart_tool.label(["Label1"], [40], [50], ["Pivot Points"], anchor=chart_tool.EnumAnchor.LeftUpper, color="230,230,230")

