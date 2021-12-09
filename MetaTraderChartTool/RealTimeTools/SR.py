
from MetaTrader.MetaTraderBase import MetaTraderBase
from MetaTraderChartTool.RealTimeTools.RealTimeTool import RealTimeTool


from AlgorithmFactory.AlgorithmTools.Aggregate import aggregate_data
from AlgorithmFactory.AlgorithmTools.SR.SR_Levels_Functions import *
from AlgorithmFactory.AlgorithmTools.SR.SR_Lines_Functions import *
from AlgorithmFactory.AlgorithmTools.DataFormatters import dictionary_list_to_list_dictionary
from AlgorithmFactory.AlgorithmTools.StrongNumberTools import get_strong_number
from Configuration.Trade.OnlineConfig import Config

from AlgorithmFactory.AlgorithmTools.Channels import coordinate_lines


class SR(RealTimeTool):

    def __init__(self, chart_tool: MetaTraderBase, data, symbol, static_leverage_degree, tf1, tf2, tf3, mode, window,
                 with_area, area_base):
        super().__init__(chart_tool, data)

        self.data = data
        self.mode = mode
        self.symbol = symbol
        self.tf1, self.tf2, self.tf3 = tf1, tf2, tf3
        self.window = window
        self.cnt = 0
        self.cnt_tr = 10

        self.with_area = with_area
        self.area_base = area_base

        self.pre_osr_lines_style = chart_tool.EnumStyle.DashDotDot

        if mode == "Dynamic":
            self.data2 = aggregate_data(self.data, tf2)
            self.data3 = aggregate_data(self.data, tf3)

            self.data1 = self.data[-len(self.data3):]
            self.data2 = self.data2[-len(self.data3):]

            self.sr_data1 = dictionary_list_to_list_dictionary(self.data1)
            self.sr_data2 = dictionary_list_to_list_dictionary(self.data2)
            self.sr_data3 = dictionary_list_to_list_dictionary(self.data3)

            self.sr_levels = Dynamic_SR_levels(self.sr_data1, self.sr_data2, self.sr_data3,
                                               10 ** -(Config.symbols_pip[symbol] - 1))
            self.draw_lines()
            self.pre_sr_levels = self.sr_levels
        elif mode == "Static":
            self.sr_data1 = dictionary_list_to_list_dictionary(self.data)

            self.sr_levels = Static_SR_levels(self.sr_data1, level_degree=static_leverage_degree)[0]
            self.draw_lines()
            self.pre_sr_levels = self.sr_levels
        elif mode == "OSR":
            self.sr_data1 = dictionary_list_to_list_dictionary(self.data)

            self.osr_lines = Oblique_channel_and_SRLines(self.sr_data1, 10 ** -(Config.symbols_pip[symbol] - 1))
            self.pre_osr_lines = self.osr_lines
            self.osr_id = 1
            self.draw_lines()

        self.data = self.data[-self.window:]

    def on_tick(self, time, bid, ask):
        pass

    def on_data(self, candle):
        if len(self.data) > self.window:
            self.data.pop(0)

        self.cnt += 1
        self.delete_lines()
        self.calculate()
        self.draw_lines()

        self.data.append(candle)

    def calculate(self):
        if self.mode == "Dynamic":
            if self.cnt >= self.cnt_tr:
                self.data2 = aggregate_data(self.data, self.tf2)
                self.data3 = aggregate_data(self.data, self.tf3)

                self.data1 = self.data[-len(self.data3):]
                self.data2 = self.data2[-len(self.data3):]

                self.sr_data1 = dictionary_list_to_list_dictionary(self.data1)
                self.sr_data2 = dictionary_list_to_list_dictionary(self.data2)
                self.sr_data3 = dictionary_list_to_list_dictionary(self.data3)

                self.sr_levels = Dynamic_SR_levels(self.sr_data1, self.sr_data2, self.sr_data3,
                                                   10 ** -(Config.symbols_pip[self.symbol] - 1))
                self.cnt = 0
        elif self.mode == "Static":
            if self.cnt >= self.cnt_tr:
                self.sr_data1 = dictionary_list_to_list_dictionary(self.data)

                self.sr_levels = Static_SR_levels(self.sr_data1)[0]


        elif self.mode == "OSR":
            self.sr_data1 = dictionary_list_to_list_dictionary(self.data)

            self.osr_lines = Oblique_channel_and_SRLines(self.sr_data1, 10 ** -(Config.symbols_pip[self.symbol] - 1))

    def draw_lines(self):
        if self.mode == "OSR":
            names, times1, prices1, times2, prices2 = [], [], [], [], []
            lines_coordinates = self.osr_lines[0]
            for i in range(len(lines_coordinates)):
                names.append(f"OSR Line {i}")
                times1.append(lines_coordinates[i][0])
                prices1.append(lines_coordinates[i][1])
                times2.append(lines_coordinates[i][2])
                prices2.append(lines_coordinates[i][3])
            self.chart_tool.trend_line(names, times1, prices1, times2, prices2)

            if self.pre_osr_lines[0][0][0] != self.osr_lines[0][0][0]:
                lines_coordinates = self.pre_osr_lines[0]
                for i in range(len(lines_coordinates)):
                    names.append(f"OSR Line {i} {self.osr_id}")
                    times1.append(lines_coordinates[i][0])
                    prices1.append(lines_coordinates[i][1])
                    times2.append(lines_coordinates[i][2])
                    prices2.append(lines_coordinates[i][3])
                self.chart_tool.trend_line(names, times1, prices1, times2, prices2, style=self.pre_osr_lines_style)
                self.osr_id += 1

            self.pre_osr_lines = self.osr_lines
        else:
            names, prices = [], []

            for i in range(len(self.sr_levels)):
                names.append(f"{self.mode} SR Level {i}")
                prices.append(self.sr_levels[i][1])

            self.chart_tool.h_line(names, prices)
            self.pre_sr_levels = self.sr_levels

            if self.with_area:
                area_names, times1, prices1, times2, prices2 = [], [], [], [], []
                for i in range(len(self.sr_levels)):
                    pip = Config.symbols_pip[self.symbol]
                    pre_strong_price = get_strong_number(self.sr_levels[i][1], self.area_base, pip)
                    area_names.append(f"{self.mode} Area Sr Level {i}")
                    times1.append(self.data[0]["Time"])
                    prices1.append(pre_strong_price)
                    times2.append(self.data[-1]["Time"] + (self.data[-1]["Time"] - self.data[-2]['Time']) * 2)
                    prices2.append(pre_strong_price + self.area_base / 10 ** pip)
                self.chart_tool.rectangle(area_names, times1, prices1, times2, prices2, back=1)

    def delete_lines(self):
        if self.mode == "OSR":
            names = []
            lines_coordinates = self.pre_osr_lines[0]
            for i in range(len(lines_coordinates)):
                names.append(f"OSR Line {i}")
            self.chart_tool.delete(names)
        else:
            names = []
            area_names = []
            for i in range(len(self.pre_sr_levels)):
                names.append(f"{self.mode} SR Level {i}")
                area_names.append(f"{self.mode} Area Sr Level {i}")
            self.chart_tool.delete(names)
            if self.with_area:
                self.chart_tool.delete(area_names)

    def coordinate_osr_lines(self):
        lines = self.osr_lines[0]
        x1 = ((lines[0][2] - lines[0][0]).seconds + (lines[0][2] - lines[0][0]).days * 86400) / 8640000
        y1 = lines[0][3]
        m1 = (lines[0][3] - lines[0][1]) / (x1)

        x2 = ((lines[1][2] - lines[0][0]).seconds + (lines[1][2] - lines[0][0]).days * 86400) / 8640000
        y2 = lines[1][3]
        m2 = (lines[1][3] - lines[1][1]) / (x2)

        x3, y3 = coordinate_lines(x1, y1, m1, x2, y2, m2)
        return x3, y3

