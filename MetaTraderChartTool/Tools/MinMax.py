
from MetaTraderChartTool.BasicChartTools import BasicChartTools
from AlgorithmFactory.AlgorithmTools.LocalExtermums import *
from AlgorithmFactory.AlgorithmTools.CandleTools import *

from AlgorithmFactory.AlgorithmPackages.MinMaxTrend import MinMaxTrend

from MetaTraderChartTool.Tools.Tool import Tool


class MinMax(Tool):

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

        self.extend_line_style = chart_tool.EnumStyle.DashDotDot
        self.inc_color = "155,255,248"
        self.dec_color = "255,30,30"

        self.rect_color = "4,129,25"
        self.rect_x, self.rect_y = 20, 40
        self.rect_width, self.rect_height = 200, 40
        self.label = "Min Max Trend Line"

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

            x, y = self.x_up_trend[i], self.y_up_trend[i]
            x_ext, y_ext = self.x_extend_inc[i], self.y_extend_inc[i]
            times1.append(self.data[x[0]]['Time'])
            prices1.append(y[0])
            times2.append(self.data[x[1]]['Time'])
            prices2.append(y[1])
            if x_ext is not 0:
                names_ext.append(f"MinMaxTrendUpExtended{i}")
                times1_ext.append(self.data[x_ext[0]]['Time'])
                prices1_ext.append(y_ext[0])
                times2_ext.append(self.data[x_ext[-1]]['Time'])
                prices2_ext.append(y_ext[-1])
            else:
                print("Zero")

        chart_tool.trend_line(names, times1, prices1, times2, prices2, color=self.inc_color)
        chart_tool.trend_line(names_ext, times1_ext, prices1_ext, times2_ext, prices2_ext, color=self.inc_color, style=self.extend_line_style)

        names, times1, prices1, times2, prices2 = [], [], [], [], []
        names_ext, times1_ext, prices1_ext, times2_ext, prices2_ext = [], [], [], [], []
        for i in range(len(self.x_down_trend)):
            names.append(f"MinMaxDownTrend{i}")
            x, y = self.x_down_trend[i], self.y_down_trend[i]
            x_ext, y_ext = self.x_extend_dec[i], self.y_extend_dec[i]
            times1.append(self.data[x[0]]['Time'])
            prices1.append(y[0])
            times2.append(self.data[x[1]]['Time'])
            prices2.append(y[1])
            if x_ext is not 0:
                names_ext.append(f"MinMaxTrendDownExtended{i}")
                times1_ext.append(self.data[x_ext[0]]['Time'])
                prices1_ext.append(y_ext[0])
                times2_ext.append(self.data[x_ext[-1]]['Time'])
                prices2_ext.append(y_ext[-1])

        chart_tool.trend_line(names, times1, prices1, times2, prices2, color=self.dec_color)
        chart_tool.trend_line(names_ext, times1_ext, prices1_ext, times2_ext, prices2_ext, color=self.dec_color,
                              style=self.extend_line_style)

        chart_tool.rectangle_label(["RectLabel"], [self.rect_x], [self.rect_y], [self.rect_width], [self.rect_height],
                                   back_color=self.rect_color, color="200,199,199", border=chart_tool.EnumBorder.Sunken)
        chart_tool.label(["Label"], [self.rect_x + (self.rect_width//2)], [self.rect_y + (self.rect_height // 4)],
                         [self.label], anchor=chart_tool.EnumAnchor.Top, font="Times New Roman", font_size=12)
