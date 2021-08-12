
from MetaTraderChartTool.BasicChartTools import BasicChartTools
from AlgorithmFactory.AlgorithmTools.LocalExtermums import *
from AlgorithmFactory.AlgorithmTools.CandleTools import *

from AlgorithmFactory.AlgorithmPackages.MinMaxTrend import MinMaxTrend


class MinMax:

    def __init__(self, data, extremum_window, extremum_mode, extremum_show):
        super().__init__(data)

        self.open, self.high, self.low, self.close = get_ohlc(data)
        self.bottom, self.top = get_bottom_top(data)

        self.extremum_mode = extremum_mode
        self.extremum_window = extremum_window
        self.extremum_show = extremum_show

        self.local_min_price, self.local_max_price = get_local_extermums(self.data, extremum_window, extremum_mode)

        self.x_up_trend, self.y_up_trend, self.x_down_trend, self.y_down_trend, self.x_extend_inc, self.y_extend_inc, \
        self.x_extend_dec, self.y_extend_dec, self.sell_idx, self.sell, self.buy_idx, self.buy = \
            MinMaxTrend.min_max_trend_detect(self.open, self.high, self.low, self.close, self.top, self.bottom,
                                             self.local_min_price, self.local_max_price, True)

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

            chart_tool.arrow_up(local_min_names, local_min_times, local_min_prices, anchor=chart_tool.EnumArrowAnchor.Top, color="12,83,211")
            chart_tool.arrow_down(local_max_names, local_max_times, local_max_prices, anchor=chart_tool.EnumArrowAnchor.Bottom, color="211,83,12")

        names, times1, prices1, times2, prices2 = [], [], [], [], []
        names_ext, times1_ext, prices1_ext, times2_ext, prices2_ext = [], [], [], [], []
        for i in range(len(self.x_up_trend)):
            names.append(f"MinMaxUpTrend{i}")
            names_ext.append(f"MinMaxTrendUpExtended{i}")
            x, y = self.x_up_trend[i], self.y_up_trend[i]
            x_ext, y_ext = self.x_extend_inc[i], self.y_extend_inc[i]
            times1.append(self.data[x[0]]['Time'])
            prices1.append(y[0])
            times2.append(self.data[x[1]]['Time'])
            prices2.append(y[1])
            if x_ext is not 0:
                times1_ext.append(self.data[x_ext[0]]['Time'])
                prices1_ext.append(y_ext[0])
                times2_ext.append(self.data[x_ext[-1]]['Time'])
                prices2_ext.append(y_ext[-1])

        chart_tool.trend_line(names, times1, prices1, times2, prices2, color="255,30,30")
        chart_tool.trend_line(names_ext, times1_ext, prices1_ext, times2_ext, prices2_ext, color="240,100,30", style=chart_tool.EnumStyle.Dot)

        names, times1, prices1, times2, prices2 = [], [], [], [], []
        names_ext, times1_ext, prices1_ext, times2_ext, prices2_ext = [], [], [], [], []
        for i in range(len(self.x_down_trend)):
            names.append(f"MinMaxDownTrend{i}")
            names_ext.append(f"MinMaxTrendDownExtended{i}")
            x, y = self.x_down_trend[i], self.y_down_trend[i]
            x_ext, y_ext = self.x_extend_dec[i], self.y_extend_dec[i]
            times1.append(self.data[x[0]]['Time'])
            prices1.append(y[0])
            times2.append(self.data[x[1]]['Time'])
            prices2.append(y[1])
            if x_ext is not 0:
                times1_ext.append(self.data[x_ext[0]]['Time'])
                prices1_ext.append(y_ext[0])
                times2_ext.append(self.data[x_ext[-1]]['Time'])
                prices2_ext.append(y_ext[-1])

        chart_tool.trend_line(names, times1, prices1, times2, prices2, color="30,30,255")
        chart_tool.trend_line(names_ext, times1_ext, prices1_ext, times2_ext, prices2_ext, color="30,30,255",
                              style=chart_tool.EnumStyle.Dot)

        # chart_tool.rectangle_label(["RectLabel1"], [20], [40], [120], [40], back_color="113,105,105", color="200,199,199", border=chart_tool.EnumBorder.Sunken)
        # chart_tool.label(["Label1"], [40], [50], ["Pivot Points"], anchor=chart_tool.EnumAnchor.LeftUpper, color="230,230,230")

