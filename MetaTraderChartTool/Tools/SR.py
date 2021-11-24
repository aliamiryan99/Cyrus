
from MetaTrader.MetaTraderBase import MetaTraderBase
from MetaTraderChartTool.Tools.Tool import Tool

from AlgorithmFactory.AlgorithmTools.Aggregate import aggregate_data
from AlgorithmFactory.AlgorithmTools.SR.SR_Levels_Functions import *
from AlgorithmFactory.AlgorithmTools.SR.SR_Lines_Functions import *
from AlgorithmFactory.AlgorithmTools.DataFormatters import dictionary_list_to_list_dictionary
from Configuration.Trade.OnlineConfig import Config


class SR(Tool):

    def __init__(self, data, symbol, tf1, tf2, tf3, mode):
        super().__init__(data)
        self.data = data
        self.mode = mode

        if mode == "Dynamic":
            self.data2 = aggregate_data(self.data, tf2)
            self.data3 = aggregate_data(self.data, tf3)

            self.data1 = self.data[-len(self.data3):]
            self.data2 = self.data2[-len(self.data3):]

            self.sr_data1 = dictionary_list_to_list_dictionary(self.data1)
            self.sr_data2 = dictionary_list_to_list_dictionary(self.data2)
            self.sr_data3 = dictionary_list_to_list_dictionary(self.data3)

            self.sr_levels = Dynamic_SR_levels(self.sr_data1, self.sr_data2, self.sr_data3, 10 ** -(Config.symbols_pip[symbol]-1))
        elif mode == "Static":
            self.sr_data1 = dictionary_list_to_list_dictionary(self.data)

            self.sr_levels = Static_SR_levels(self.sr_data1)[0]
        elif mode == "OSR":
            self.sr_data1 = dictionary_list_to_list_dictionary(self.data)

            self.osr_lines = Oblique_channel_and_SRLines(self.sr_data1, 10 ** -(Config.symbols_pip[symbol]-1))

    def draw(self, chart_tools: MetaTraderBase):

        if self.mode == "OSR":
            names, times1, prices1, times2, prices2 = [], [], [], [], []
            lines_coordinates = self.osr_lines[0]
            for i in range(len(lines_coordinates)):
                names.append(f"OSR Line {i}")
                times1.append(lines_coordinates[i][0])
                prices1.append(lines_coordinates[i][1])
                times2.append(lines_coordinates[i][2])
                prices2.append(lines_coordinates[i][3])
            chart_tools.trend_line(names, times1, prices1, times2, prices2)
        else:
            names, prices = [], []
            for i in range(len(self.sr_levels)):
                names.append(f"{self.mode} SR Level {i}")
                prices.append(self.sr_levels[i][1])
            chart_tools.h_line(names, prices)
