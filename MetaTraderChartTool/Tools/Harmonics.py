
from MetaTraderChartTool.BasicChartTools import BasicChartTools

from AlgorithmFactory.AlgorithmTools.LocalExtermums import *
from ta.momentum import *

from AlgorithmFactory.AlgorithmPackages.HarmonicPattern.HarmonicDetection import harmonic_pattern
from AlgorithmFactory.AlgorithmPackages.HarmonicPattern.HarmonicFilter import filter_results

from random import randint
import pickle


class Harmonics:

    def __init__(self, data, extremum_window, time_range, price_range_alpha, harmonic_name, alpha, beta, fibo_tolerance, pattern_direction, harmonic_list, save_result):
        self.data = data

        self.alpha = alpha
        self.beta = beta

        self.extremum_window = extremum_window
        self.time_range = time_range
        self.price_range_alpha = price_range_alpha
        self.harmonic_name = harmonic_name
        self.fibo_tolerance = fibo_tolerance
        self.pattern_direction = pattern_direction
        self.harmonic_list = harmonic_list

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

        if save_result:
            self.result = {}
            if self.harmonic_name == "All":
                for name in self.harmonic_list:
                    self.result[name] = {}
                    self.calculate_harmonic(name)
            else:
                self.calculate_harmonic(harmonic_name)

            result_file = open("MetaTraderChartTool/Tools/Save Results/Harmonic.pkl", "wb+")
            data_file = open("MetaTraderChartTool/Tools/Save Results/HarmonicData.pkl", "wb+")
            pickle.dump(self.result, result_file)
            pickle.dump(self.data, data_file)
        else:
            result_file = open("MetaTraderChartTool/Tools/Save Results/Harmonic.pkl", "rb")
            data_file = open("MetaTraderChartTool/Tools/Save Results/HarmonicData.pkl", "rb")
            self.result = pickle.load(result_file)
            self.data = pickle.load(data_file)

    def calculate_harmonic(self, harmonic_name):
        if self.pattern_direction=='both':
            self.bullish_result = harmonic_pattern(self.high, self.low, self.middle, self.local_min_price_area,
                                                   self.local_max_price_area, harmonic_name, "Bullish", True,
                                                   self.alpha, self.beta,self.fibo_tolerance)
            self.bearish_result = harmonic_pattern(self.high, self.low, self.middle, self.local_min_price_area,
                                                   self.local_max_price_area, harmonic_name, "Bearish", True,
                                                   self.alpha, self.beta,self.fibo_tolerance)

            self.bullish_result = filter_results(self.high, self.low, self.bullish_result, self.middle,
                                                 self.harmonic_name,
                                                 "Bullish", self.alpha, self.beta)
            self.bearish_result = filter_results(self.high, self.low, self.bearish_result, self.middle,
                                                 self.harmonic_name,
                                                 "Bearish", self.alpha, self.beta)
            self.result[harmonic_name] = {'bullish': self.bullish_result, 'bearish': self.bearish_result}
        elif self.pattern_direction == 'bullish':
            self.bullish_result = harmonic_pattern(self.high, self.low, self.middle, self.local_min_price_area,
                                                   self.local_max_price_area, harmonic_name, "Bullish", True,
                                                   self.alpha, self.beta, self.fibo_tolerance)

            self.bullish_result = filter_results(self.high, self.low, self.bullish_result, self.middle,
                                                 self.harmonic_name,
                                                 "Bullish", self.alpha, self.beta)
            self.result[harmonic_name] = {'bullish': self.bullish_result}
        elif self.pattern_direction == 'bearish':
            self.bearish_result = harmonic_pattern(self.high, self.low, self.middle, self.local_min_price_area,
                                                   self.local_max_price_area, harmonic_name, "Bearish", True,
                                                   self.alpha, self.beta, self.fibo_tolerance)

            self.bearish_result = filter_results(self.high, self.low, self.bearish_result, self.middle,
                                                 self.harmonic_name,
                                                 "Bearish", self.alpha, self.beta)
            self.result[harmonic_name] = {'bearish': self.bearish_result}

    def draw(self, chart_tool: BasicChartTools):

        width = 2
        bullish_color = '20,20,255'
        bearish_color = '255,20,20'

        # define N digit random number

        n = 5
        range_start = 10 ** (n - 1)
        range_end = (10 ** n) - 1
        random_tage = randint(range_start, range_end)

        if self.harmonic_name == 'ABCD_None':
            names, times1, prices1, times2, prices2 = [], [], [], [], []
            names_ext, times1_ext, prices1_ext, times2_ext, prices2_ext = [], [], [], [], []
            name_txt1, text_txt1, time_txt1, price_txt1 = [], [], [], []
            name_txt2, text_txt2, time_txt2, price_txt2 = [], [], [], []
            i = 0
            for result in self.bullish_result:
                self.add_line(f"{self.harmonic_name}_BullishHarmonic{i}_Line1_{(random_tage)}", self.data[int(result[1])]['Time'], self.data[int(result[2])]['Time'], result[6], result[7], names, times1, times2, prices1, prices2)
                self.add_line(f"{self.harmonic_name}_BullishHarmonic{i}_Line2_{(random_tage)}", self.data[int(result[2])]['Time'], self.data[int(result[3])]['Time'], result[7], result[8], names, times1, times2, prices1, prices2)
                self.add_line(f"{self.harmonic_name}_BullishHarmonic{i}_Line3_{(random_tage)}", self.data[int(result[3])]['Time'], self.data[int(result[4])]['Time'], result[8], result[9], names, times1, times2, prices1, prices2)
                self.add_line(f"{self.harmonic_name}_BullishHarmonic{i}_DottedLine1_{(random_tage)}", self.data[int(result[1])]['Time'], self.data[int(result[3])]['Time'], result[6], result[8], names_ext, times1_ext, times2_ext, prices1_ext, prices2_ext)
                self.add_line(f"{self.harmonic_name}_BullishHarmonic{i}_DottedLine2_{(random_tage)}", self.data[int(result[2])]['Time'], self.data[int(result[4])]['Time'], result[7], result[9], names_ext, times1_ext, times2_ext, prices1_ext, prices2_ext)
                self.add_text(f"{self.harmonic_name}_BullishHarmonic{i}_A_{(random_tage)}", "A", self.data[int(result[1])]['Time'], result[6], name_txt1, text_txt1, time_txt1, price_txt1)
                self.add_text(f"{self.harmonic_name}_BullishHarmonic{i}_B_{(random_tage)}", "B", self.data[int(result[2])]['Time'], result[7], name_txt2, text_txt2, time_txt2, price_txt2)
                self.add_text(f"{self.harmonic_name}_BullishHarmonic{i}_C_{(random_tage)}", "C", self.data[int(result[3])]['Time'], result[8], name_txt1, text_txt1, time_txt1, price_txt1)
                self.add_text(f"{self.harmonic_name}_BullishHarmonic{i}_D_{(random_tage)}", "D", self.data[int(result[4])]['Time'], result[9], name_txt2, text_txt2, time_txt2, price_txt2)
                self.add_text(f"{self.harmonic_name}_BullishHarmonic{i}_AC_{(random_tage)}", f"{round(result[11],4)}", self.data[int((result[1]+result[3])/2)]['Time'], (result[6]+result[8])/2, name_txt1, text_txt1, time_txt1, price_txt1)
                self.add_text(f"{self.harmonic_name}_BullishHarmonic{i}_BD_{(random_tage)}", f"{round(result[12],4)}", self.data[int((result[2]+result[4])/2)]['Time'], (result[7]+result[9])/2, name_txt2, text_txt2, time_txt2, price_txt2)
                i += 1

            chart_tool.trend_line(names, times1, prices1, times2, prices2, color=bullish_color, width=width)
            chart_tool.trend_line(names_ext, times1_ext, prices1_ext, times2_ext, prices2_ext, color=bullish_color,
                                  style=chart_tool.EnumStyle.Dot)
            chart_tool.text(name_txt1, time_txt1, price_txt1, text_txt1, anchor=chart_tool.EnumAnchor.Bottom)
            chart_tool.text(name_txt2, time_txt2, price_txt2, text_txt2, anchor=chart_tool.EnumAnchor.Top)

            names, times1, prices1, times2, prices2 = [], [], [], [], []
            names_ext, times1_ext, prices1_ext, times2_ext, prices2_ext = [], [], [], [], []
            name_txt1, text_txt1, time_txt1, price_txt1 = [], [], [], []
            name_txt2, text_txt2, time_txt2, price_txt2 = [], [], [], []
            i = 0
            for result in self.bearish_result:
                self.add_line(f"{self.harmonic_name}_BearishHarmonic{i}_Line1_{(random_tage)}", self.data[int(result[1])]['Time'], self.data[int(result[2])]['Time'], result[6], result[7], names, times1, times2, prices1, prices2)
                self.add_line(f"{self.harmonic_name}_BearishHarmonic{i}_Line2_{(random_tage)}", self.data[int(result[2])]['Time'], self.data[int(result[3])]['Time'], result[7], result[8], names, times1, times2, prices1, prices2)
                self.add_line(f"{self.harmonic_name}_BearishHarmonic{i}_Line3_{(random_tage)}", self.data[int(result[3])]['Time'], self.data[int(result[4])]['Time'], result[8], result[9], names, times1, times2, prices1, prices2)
                self.add_line(f"{self.harmonic_name}_BearishHarmonic{i}_DottedLine1_{(random_tage)}", self.data[int(result[1])]['Time'], self.data[int(result[3])]['Time'], result[6], result[8], names_ext, times1_ext, times2_ext, prices1_ext, prices2_ext)
                self.add_line(f"{self.harmonic_name}_BearishHarmonic{i}_DottedLine2_{(random_tage)}", self.data[int(result[2])]['Time'], self.data[int(result[4])]['Time'], result[7], result[9], names_ext, times1_ext, times2_ext, prices1_ext, prices2_ext)
                self.add_text(f"{self.harmonic_name}_BearishHarmonic{i}_A_{(random_tage)}", "A", self.data[int(result[1])]['Time'], result[6], name_txt1, text_txt1, time_txt1, price_txt1)
                self.add_text(f"{self.harmonic_name}_BearishHarmonic{i}_B_{(random_tage)}", "B", self.data[int(result[2])]['Time'], result[7], name_txt2, text_txt2, time_txt2, price_txt2)
                self.add_text(f"{self.harmonic_name}_BearishHarmonic{i}_C_{(random_tage)}", "C", self.data[int(result[3])]['Time'], result[8], name_txt1, text_txt1, time_txt1, price_txt1)
                self.add_text(f"{self.harmonic_name}_BearishHarmonic{i}_D_{(random_tage)}", "D", self.data[int(result[4])]['Time'], result[9], name_txt2, text_txt2, time_txt2, price_txt2)
                self.add_text(f"{self.harmonic_name}_BearishHarmonic{i}_AC_{(random_tage)}", f"{round(result[11], 4)}", self.data[int((result[1] + result[3]) / 2)]['Time'], (result[6] + result[8]) / 2, name_txt1, text_txt1, time_txt1, price_txt1)
                self.add_text(f"{self.harmonic_name}_BearishHarmonic{i}_BD_{(random_tage)}", f"{round(result[12], 4)}", self.data[int((result[2] + result[4]) / 2)]['Time'], (result[7] + result[9]) / 2, name_txt2, text_txt2, time_txt2, price_txt2)
                i += 1

            chart_tool.trend_line(names, times1, prices1, times2, prices2, color=bearish_color, width=width)
            chart_tool.trend_line(names_ext, times1_ext, prices1_ext, times2_ext, prices2_ext, color=bearish_color,
                                  style=chart_tool.EnumStyle.Dot)

            chart_tool.text(name_txt1, time_txt1, price_txt1, text_txt1, anchor=chart_tool.EnumAnchor.Top)
            chart_tool.text(name_txt2, time_txt2, price_txt2, text_txt2, anchor=chart_tool.EnumAnchor.Bottom)
        else:
            for name in self.result.keys():
                if 'bullish' in self.result[name].keys():
                    bulish_result = self.result[name]['bullish']
                    names, times1, prices1, times2, prices2, times3, prices3 = [], [], [], [], [], [], []
                    name_txt1, text_txt1, time_txt1, price_txt1 = [], [], [], []
                    name_txt2, text_txt2, time_txt2, price_txt2 = [], [], [], []
                    i = 0
                    for result in self.result[name]['bullish']:
                        self.add_triangle(f"{name}_BullishHarmonic{i}_Triangle1_{(random_tage)}", self.data[int(result[0])]['Time'], self.data[int(result[1])]['Time'], self.data[int(result[2])]['Time'], result[5], result[6], result[7], names, times1, times2, times3, prices1, prices2, prices3)
                        self.add_triangle(f"{name}_BullishHarmonic{i}_Triangle2_{(random_tage)}", self.data[int(result[2])]['Time'], self.data[int(result[3])]['Time'], self.data[int(result[4])]['Time'], result[7], result[8], result[9], names, times1, times2, times3, prices1, prices2, prices3)
                        self.add_text(f"{name}_BullishHarmonic{i}_X_{(random_tage)}", "X", self.data[int(result[0])]['Time'], result[5], name_txt2, text_txt2, time_txt2, price_txt2)
                        self.add_text(f"{name}_BullishHarmonic{i}_A_{(random_tage)}", "A", self.data[int(result[1])]['Time'], result[6], name_txt1, text_txt1, time_txt1, price_txt1)
                        self.add_text(f"{name}_BullishHarmonic{i}_B_{(random_tage)}", "B", self.data[int(result[2])]['Time'], result[7], name_txt2, text_txt2, time_txt2, price_txt2)
                        self.add_text(f"{name}_BullishHarmonic{i}_Name_{(random_tage)}", name, self.data[int(result[2])]['Time'], result[7], name_txt1, text_txt1, time_txt1, price_txt1)
                        self.add_text(f"{name}_BullishHarmonic{i}_C_{(random_tage)}", "C", self.data[int(result[3])]['Time'], result[8], name_txt1, text_txt1, time_txt1, price_txt1)
                        self.add_text(f"{name}_BullishHarmonic{i}_D_{(random_tage)}", "D", self.data[int(result[4])]['Time'], result[9], name_txt2, text_txt2, time_txt2, price_txt2)
                        self.add_text(f"{name}_BullishHarmonic{i}_XB_{(random_tage)}", f"{round(result[10], 4)}", self.data[int((result[0] + result[2]) / 2)]['Time'], (result[5] + result[7]) / 2, name_txt2, text_txt2, time_txt2, price_txt2)
                        self.add_text(f"{name}_BullishHarmonic{i}_AC_{(random_tage)}", f"{round(result[11], 4)}", self.data[int((result[1] + result[3]) / 2)]['Time'], (result[6] + result[8]) / 2, name_txt1, text_txt1, time_txt1, price_txt1)
                        self.add_text(f"{name}_BullishHarmonic{i}_BD_{(random_tage)}", f"{round(result[12], 4)}", self.data[int((result[2] + result[4]) / 2)]['Time'], (result[7] + result[9]) / 2, name_txt2, text_txt2, time_txt2, price_txt2)
                        self.add_text(f"{name}_BullishHarmonic{i}_XD_{(random_tage)}", f"{round(result[13], 4)}", self.data[int((result[0] + result[4]) / 2)]['Time'], (result[5] + result[9]) / 2, name_txt2, text_txt2, time_txt2, price_txt2)
                        i += 1

                    chart_tool.triangle(names, times1, prices1, times2, prices2, times3, prices3, width=width, color=bullish_color, back=1)
                    chart_tool.text(name_txt1, time_txt1, price_txt1, text_txt1, anchor=chart_tool.EnumAnchor.Bottom)
                    chart_tool.text(name_txt2, time_txt2, price_txt2, text_txt2, anchor=chart_tool.EnumAnchor.Top)

                if 'bearish' in self.result[name].keys():
                    bearish_result = self.result[name]['bearish']
                    names, times1, prices1, times2, prices2, times3, prices3 = [], [], [], [], [], [], []
                    name_txt1, text_txt1, time_txt1, price_txt1 = [], [], [], []
                    name_txt2, text_txt2, time_txt2, price_txt2 = [], [], [], []
                    i = 0
                    for result in self.result[name]['bearish']:
                        self.add_triangle(f"{name}_BearishHarmonic{i}_Triangle1_{(random_tage)}", self.data[int(result[0])]['Time'], self.data[int(result[1])]['Time'], self.data[int(result[2])]['Time'], result[5], result[6], result[7], names, times1, times2, times3, prices1, prices2, prices3)
                        self.add_triangle(f"{name}_BearishHarmonic{i}_Triangle2_{(random_tage)}", self.data[int(result[2])]['Time'], self.data[int(result[3])]['Time'], self.data[int(result[4])]['Time'], result[7], result[8], result[9], names, times1, times2, times3, prices1, prices2, prices3)
                        self.add_text(f"{name}_BearishHarmonic{i}_X_{(random_tage)}", "X", self.data[int(result[0])]['Time'], result[5], name_txt2, text_txt2, time_txt2, price_txt2)
                        self.add_text(f"{name}_BearishHarmonic{i}_A_{(random_tage)}", "A", self.data[int(result[1])]['Time'], result[6], name_txt1, text_txt1, time_txt1, price_txt1)
                        self.add_text(f"{name}_BearishHarmonic{i}_B_{(random_tage)}", "B", self.data[int(result[2])]['Time'], result[7], name_txt2, text_txt2, time_txt2, price_txt2)
                        self.add_text(f"{name}_BearishHarmonic{i}_Name_{(random_tage)}", name, self.data[int(result[2])]['Time'], result[7], name_txt1, text_txt1, time_txt1, price_txt1)
                        self.add_text(f"{name}_BearishHarmonic{i}_C_{(random_tage)}", "C", self.data[int(result[3])]['Time'], result[8], name_txt1, text_txt1, time_txt1, price_txt1)
                        self.add_text(f"{name}_BearishHarmonic{i}_D_{(random_tage)}", "D", self.data[int(result[4])]['Time'], result[9], name_txt2, text_txt2, time_txt2, price_txt2)
                        self.add_text(f"{name}_BearishHarmonic{i}_XB_{(random_tage)}", f"{round(result[10], 4)}", self.data[int((result[0] + result[2]) / 2)]['Time'], (result[5] + result[7]) / 2, name_txt2, text_txt2, time_txt2, price_txt2)
                        self.add_text(f"{name}_BearishHarmonic{i}_AC_{(random_tage)}", f"{round(result[11], 4)}", self.data[int((result[1] + result[3]) / 2)]['Time'], (result[6] + result[8]) / 2, name_txt1, text_txt1, time_txt1, price_txt1)
                        self.add_text(f"{name}_BearishHarmonic{i}_BD_{(random_tage)}", f"{round(result[12], 4)}", self.data[int((result[2] + result[4]) / 2)]['Time'], (result[7] + result[9]) / 2, name_txt2, text_txt2, time_txt2, price_txt2)
                        self.add_text(f"{name}_BearishHarmonic{i}_XD_{(random_tage)}", f"{round(result[13], 4)}", self.data[int((result[0] + result[4]) / 2)]['Time'], (result[5] + result[9]) / 2, name_txt2, text_txt2, time_txt2, price_txt2)
                        i += 1

                    chart_tool.triangle(names, times1, prices1, times2, prices2, times3, prices3, width=width, color=bearish_color, back=1)
                    chart_tool.text(name_txt1, time_txt1, price_txt1, text_txt1, anchor=chart_tool.EnumAnchor.Top)
                    chart_tool.text(name_txt2, time_txt2, price_txt2, text_txt2, anchor=chart_tool.EnumAnchor.Bottom)

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

    @staticmethod
    def add_text(name, text, t, p, name_list, text_list, t_list, p_list):
        name_list.append(name)
        text_list.append(text)
        t_list.append(t)
        p_list.append(p)
