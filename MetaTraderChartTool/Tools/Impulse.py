
from MetaTraderChartTool.BasicChartTools import BasicChartTools
from AlgorithmTools.LocalExtermums import *
from AlgorithmTools.Impulse import get_impulses


class Impulse:

    def __init__(self, data, extremum_window, extremum_mode, candles_tr, extremum_show):
        self.data = data

        self.extremum_mode = extremum_mode
        self.extremum_window = extremum_window
        self.extremum_show = extremum_show

        self.local_min_price, self.local_max_price = get_local_extermums(self.data, extremum_window, extremum_mode)
        self.up_impulse, self.down_impulse = get_impulses(self.data, self.local_min_price, self.local_max_price, candles_tr)

    def draw(self, chart_tool: BasicChartTools):

        if self.extremum_show:
            local_min_times, local_min_prices, local_min_names = [], [], []
            local_max_times, local_max_prices, local_max_names = [], [], []
            for i in range(len(self.local_min_price)):
                local_min_times.append(self.data[self.local_min_price[i]]['Time'])
                local_min_prices.append(self.data[self.local_min_price[i]]['Low'])
                local_min_names.append(f"LocalMinPython{i}")
            for i in range(len(self.local_max_price)):
                local_max_times.append(self.data[self.local_max_price[i]]['Time'])
                local_max_prices.append(self.data[self.local_max_price[i]]['High'])
                local_max_names.append(f"LocalMaxPython{i}")

            chart_tool.arrow_up(local_min_names, local_min_times, local_min_prices, anchor=chart_tool.EnumArrowAnchor.Top,
                                color="12,83,211")
            chart_tool.arrow_down(local_max_names, local_max_times, local_max_prices,
                                  anchor=chart_tool.EnumArrowAnchor.Bottom, color="211,83,12")

        names, times1, prices1, times2, prices2 = [], [], [], [], []
        i = 0
        for impulse in self.up_impulse:
            names.append(f"UpImpulse{i}")
            times1.append(self.data[impulse[0]]['Time'])
            times2.append(self.data[impulse[1]]['Time'])
            prices1.append(self.data[impulse[0]]['Low'])
            prices2.append(self.data[impulse[1]]['High'])
            i += 1

        chart_tool.fibonacci_retracement(names, times1, prices1, times2, prices2, color="60,120,240")
        chart_tool.trend_line(names, times1, prices1, times2, prices2, color="60,120,240", style=chart_tool.EnumStyle.Dot)

        names, times1, prices1, times2, prices2 = [], [], [], [], []
        i = 0
        for impulse in self.down_impulse:
            names.append(f"DownImpulse{i}")
            times1.append(self.data[impulse[0]]['Time'])
            times2.append(self.data[impulse[1]]['Time'])
            prices1.append(self.data[impulse[0]]['High'])
            prices2.append(self.data[impulse[1]]['Low'])
            i += 1

        chart_tool.fibonacci_retracement(names, times1, prices1, times2, prices2, color="240,120,60")
        chart_tool.trend_line(names, times1, prices1, times2, prices2, color="240,120,60",
                              style=chart_tool.EnumStyle.Dot)

        # chart_tool.rectangle_label(["RectLabel1"], [20], [40], [120], [40], back_color="113,105,105", color="200,199,199", border=chart_tool.EnumBorder.Sunken)
        # chart_tool.label(["Label1"], [40], [50], ["Pivot Points"], anchor=chart_tool.EnumAnchor.LeftUpper, color="230,230,230")

