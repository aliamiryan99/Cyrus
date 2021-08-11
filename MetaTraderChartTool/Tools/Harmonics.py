
from MetaTraderChartTool.BasicChartTools import BasicChartTools

from AlgorithmFactory.AlgorithmTools.LocalExtermums import *
from ta.momentum import *

from AlgorithmFactory.AlgorithmPackages.HarmonicPattern.HarmonicDetection import harmonic_pattern
from AlgorithmFactory.AlgorithmPackages.HarmonicPattern.HarmonicFilter import filter_results


class Harmonics:

    def __init__(self, data, extremum_window, time_range, price_range_alpha, harmonic_name):
        self.data = data

        self.extremum_window = extremum_window
        self.time_range = time_range
        self.price_range_alpha = price_range_alpha
        self.harmonic_name = harmonic_name

        self.open = np.array([d['Open'] for d in self.data])
        self.high = np.array([d['High'] for d in self.data])
        self.low = np.array([d['Low'] for d in self.data])
        self.close = np.array([d['Close'] for d in self.data])

        self.top = np.c_[self.open, self.close].max(1)
        self.bottom = np.c_[self.open, self.close].min(1)
        self.middle = np.c_[self.open, self.close].mean(1)

        self.price_range = self.price_range_alpha * (self.high - self.low).mean()

        self.local_min_price, self.local_max_price = get_local_extermums(self.data, extremum_window, 1)

        self.local_min_price_area, self.local_max_price_area = \
            get_local_extremum_area(data, self.local_min_price, self.local_max_price, self.time_range, self.price_range)

        self.bullish_result = harmonic_pattern(self.high, self.low, self.middle, self.local_min_price_area,
                                               self.local_max_price_area, self.harmonic_name, "Bullish", True)
        self.bearish_result = harmonic_pattern(self.high, self.low, self.middle, self.local_min_price_area,
                                               self.local_max_price_area, self.harmonic_name, "Bearish", True)

        self.bullish_result = filter_results(self.high, self.low, self.bullish_result, self.middle, self.harmonic_name,
                                             "Bullish")
        self.bearish_result = filter_results(self.high, self.low, self.bearish_result, self.middle, self.harmonic_name,
                                             "Bearish")

    def draw(self, chart_tool: BasicChartTools):

        width = 2
        bullish_color = '20,20,255'
        bearish_color = '255,20,20'
        if self.harmonic_name == 'ABCD':
            names, times1, prices1, times2, prices2 = [], [], [], [], []
            names_ext, times1_ext, prices1_ext, times2_ext, prices2_ext = [], [], [], [], []
            i = 0
            for result in self.bullish_result:
                self.add_line(f"BullishHarmonic{i}_Line1", self.data[int(result[1])]['Time'], self.data[int(result[2])]['Time'], result[6], result[7], names, times1, times2, prices1, prices2)
                self.add_line(f"BullishHarmonic{i}_Line2", self.data[int(result[2])]['Time'], self.data[int(result[3])]['Time'], result[7], result[8], names, times1, times2, prices1, prices2)
                self.add_line(f"BullishHarmonic{i}_Line3", self.data[int(result[3])]['Time'], self.data[int(result[4])]['Time'], result[8], result[9], names, times1, times2, prices1, prices2)
                self.add_line(f"BullishHarmonic{i}_DottedLine1", self.data[int(result[1])]['Time'], self.data[int(result[3])]['Time'], result[6], result[8], names_ext, times1_ext, times2_ext, prices1_ext, prices2_ext)
                self.add_line(f"BullishHarmonic{i}_DottedLine2", self.data[int(result[2])]['Time'], self.data[int(result[4])]['Time'], result[7], result[9], names_ext, times1_ext, times2_ext, prices1_ext, prices2_ext)
                i += 1

            chart_tool.trend_line(names, times1, prices1, times2, prices2, color=bullish_color, width=width)
            chart_tool.trend_line(names_ext, times1_ext, prices1_ext, times2_ext, prices2_ext, color=bullish_color,
                                  style=chart_tool.EnumStyle.Dot)

            names, times1, prices1, times2, prices2 = [], [], [], [], []
            names_ext, times1_ext, prices1_ext, times2_ext, prices2_ext = [], [], [], [], []
            i = 0
            for result in self.bearish_result:
                self.add_line(f"BearishHarmonic{i}_Line1", self.data[int(result[1])]['Time'], self.data[int(result[2])]['Time'], result[6], result[7], names, times1, times2, prices1, prices2)
                self.add_line(f"BearishHarmonic{i}_Line2", self.data[int(result[2])]['Time'], self.data[int(result[3])]['Time'], result[7], result[8], names, times1, times2, prices1, prices2)
                self.add_line(f"BearishHarmonic{i}_Line3", self.data[int(result[3])]['Time'], self.data[int(result[4])]['Time'], result[8], result[9], names, times1, times2, prices1, prices2)
                self.add_line(f"BearishHarmonic{i}_DottedLine1", self.data[int(result[1])]['Time'], self.data[int(result[3])]['Time'], result[6], result[8], names_ext, times1_ext, times2_ext, prices1_ext, prices2_ext)
                self.add_line(f"BearishHarmonic{i}_DottedLine2", self.data[int(result[2])]['Time'], self.data[int(result[4])]['Time'], result[7], result[9], names_ext, times1_ext, times2_ext, prices1_ext, prices2_ext)
                i += 1

            chart_tool.trend_line(names, times1, prices1, times2, prices2, color=bearish_color, width=width)
            chart_tool.trend_line(names_ext, times1_ext, prices1_ext, times2_ext, prices2_ext, color=bearish_color,
                                  style=chart_tool.EnumStyle.Dot)
        else:
            names, times1, prices1, times2, prices2, times3, prices3 = [], [], [], [], [], [], []
            i = 0
            for result in self.bullish_result:
                self.add_triangle(f"BullishHarmonic{i}_Triangle1", self.data[int(result[0])]['Time'], self.data[int(result[1])]['Time'], self.data[int(result[2])]['Time'], result[5], result[6], result[7], names, times1, times2, times3, prices1, prices2, prices3)
                self.add_triangle(f"BullishHarmonic{i}_Triangle2", self.data[int(result[2])]['Time'], self.data[int(result[3])]['Time'], self.data[int(result[4])]['Time'], result[7], result[8], result[9], names, times1, times2, times3, prices1, prices2, prices3)
                i += 1

            chart_tool.triangle(names, times1, prices1, times2, prices2, times3, prices3, width=width, color=bullish_color, back=1)

            names, times1, prices1, times2, prices2, times3, prices3 = [], [], [], [], [], [], []
            i = 0
            for result in self.bearish_result:
                self.add_triangle(f"BearishHarmonic{i}_Triangle1", self.data[int(result[0])]['Time'], self.data[int(result[1])]['Time'], self.data[int(result[2])]['Time'], result[5], result[6], result[7], names, times1, times2, times3, prices1, prices2, prices3)
                self.add_triangle(f"BearishHarmonic{i}_Triangle2", self.data[int(result[2])]['Time'], self.data[int(result[3])]['Time'], self.data[int(result[4])]['Time'], result[7], result[8], result[9], names, times1, times2, times3, prices1, prices2, prices3)
                i += 1

            chart_tool.triangle(names, times1, prices1, times2, prices2, times3, prices3, width=width, color=bearish_color, back=1)

        # chart_tool.rectangle_label(["RectLabel1"], [20], [40], [120], [40], back_color="113,105,105", color="200,199,199", border=chart_tool.EnumBorder.Sunken)
        # chart_tool.label(["Label1"], [40], [50], ["Pivot Points"], anchor=chart_tool.EnumAnchor.LeftUpper, color="230,230,230")

    @staticmethod
    def add_line(name, t1, t2, p1, p2, name_list, t1_list, t2_list, p1_list, p2_list):
        name_list.append(name)
        t1_list.append(t1)
        t2_list.append(t2)
        p1_list.append(p1)
        p2_list.append(p2)

    @staticmethod
    def add_triangle(name, t1, t2, t3, p1, p2, p3, name_list, t1_list, t2_list, t3_list, p1_list, p2_list, p3_list):
        name_list.append(name)
        t1_list.append(t1)
        t2_list.append(t2)
        t3_list.append(t3)
        p1_list.append(p1)
        p2_list.append(p2)
        p3_list.append(p3)
