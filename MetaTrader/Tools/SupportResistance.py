
from MetaTraderChartTool.BasicChartTools import BasicChartTools
from AlgorithmFactory.AlgorithmTools.LocalExtermums import *
from AlgorithmFactory.AlgorithmTools.CandleTools import *
from AlgorithmFactory.AlgorithmTools import RSTools
from MetaTrader.Tools import Tool


class SupportResistance(Tool):

    def __init__(self, data, extremum_window, extremum_mode, sections, extremum_show):
        super().__init__(data)

        self.extremum_mode = extremum_mode
        self.extremum_window = extremum_window
        self.sections = sections
        self.extremum_show = extremum_show
        self.sections_filed = [False] * self.sections

        self.open, self.high, self.low, self.close = get_ohlc(data)
        self.bottom, self.top = get_bottom_top(self.data)

        self.global_max_price = self.high.max()
        self.global_min_price = self.low.min()

        self.local_min_price, self.local_max_price = get_local_extermums(self.data, extremum_window, extremum_mode)
        local_min_value, local_max_value = self.bottom[self.local_min_price], self.top[self.local_max_price]
        local_extremum = np.array((self.local_min_price.tolist() + self.local_max_price.tolist()))
        local_extremum_value = np.array(local_min_value.tolist() + local_max_value.tolist())
        self.r_s_matrix = RSTools.get_support_resistance_lines(self.data, local_extremum, local_extremum_value)

        self.s_values, self.r_values = [], []
        for r_s in self.r_s_matrix:
            value = r_s[1]
            section = int(((value - self.global_min_price) / (self.global_max_price - self.global_min_price)) * self.sections)
            if section == self.sections:
                section -= 1
            if not self.sections_filed[section]:
                if value > self.data[-1]['Close']:
                    self.r_values.append(value)
                else:
                    self.s_values.append(value)
                self.sections_filed[section] = True

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

        s_names = []
        for i in range(len(self.s_values)):
            s_names.append(f"Support{i}")
        r_names = []
        for i in range(len(self.r_values)):
            r_names.append(f"Resistance{i}")

        chart_tool.h_line(s_names, self.s_values, color="100,100,230")
        chart_tool.h_line(r_names, self.r_values, color="230,100,100")


        # chart_tool.rectangle_label(["Support Resistance Rect"], [20], [40], [150], [40], back_color="113,105,105", color="160,199,199", border=chart_tool.EnumBorder.Sunken)
        # chart_tool.label(["Support Resistance Label"], [40], [50], ["Support Resistance"], anchor=chart_tool.EnumAnchor.LeftUpper, color="230,230,230")

