
from MetaTraderChartTool.Tools.Tool import Tool
from MetaTraderChartTool.BasicChartTools import BasicChartTools
from AlgorithmFactory.AlgorithmTools.Elliott import elliott

import pandas as pd
import numpy as np


class Elliot(Tool):

    def __init__(self, data):
        super().__init__(data)

        monowave_list, polywave_list = elliott.calculate(pd.DataFrame(data), price_type="neo", timeframe="H4", step=6)
        # TODO : if neo_wo_merge was True Then polywave_lsit = []
        self.result_final = {}
        results = []
        times = [row['Time'] for row in self.data]
        for i in range(len(monowave_list)):
            results.append(monowave_list[i].reset_index())
            # add start and end DateTime to the output dataframe
            start_time_list = results[i]['Start_candle_index'].tolist()
            end_time_list = results[i]['End_candle_index'].tolist()
            results[i]['Start_time'] = list(np.array(times)[start_time_list])
            results[i]['End_time'] = list(np.array(times)[end_time_list])

            index = "M" + str(i)
            self.result_final[index] = results[i].to_dict("records")

            start_time_list = polywave_list[i]['Start_index']
            end_time_list = polywave_list[i]['End_index']

            polywave_list[i]['Start_time'] = list(np.array(times)[start_time_list])
            polywave_list[i]['End_time'] = list(np.array(times)[end_time_list])

            index = "P" + str(i)
            self.result_final[index] = polywave_list[i]

    def draw(self, chart_tool: BasicChartTools):

        color = "255,255,255"
        width = 2

        names = [f"Mono Wave {i}" for i in range(len(self.result_final['M0']))]
        start_times = [item['Start_time'] for item in self.result_final['M0']]
        end_times = [item['End_time'] for item in self.result_final['M0']]
        start_prices = [item['Start_price'] for item in self.result_final['M0']]
        end_prices = [item['End_price'] for item in self.result_final['M0']]

        chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=color, width=width)

        names1, times1, prices1, texts1 = [], [], [], []
        names2, times2, prices2, texts2 = [], [], [], []
        i = 0
        for mono_wave in self.result_final['M0']:
            i += 1
            if mono_wave['Direction'] == 1:
                names1.append(f"Mono Wave Label {i}")
                times1.append(mono_wave['End_time'])
                prices1.append(self.data[mono_wave['End_candle_index']]['High'])
                texts1.append(f"{mono_wave['Structure_list_label']}".replace(",", "-"))
            elif mono_wave['Direction'] == -1:
                names2.append(f"Mono Wave Label {i}")
                times2.append(mono_wave['End_time'])
                prices2.append(self.data[mono_wave['End_candle_index']]['Low'])
                texts2.append(f"{mono_wave['Structure_list_label']}".replace(",", "-"))

        chart_tool.text(names1, times1, prices1, texts1, anchor=chart_tool.EnumAnchor.Bottom)
        chart_tool.text(names2, times2, prices2, texts2, anchor=chart_tool.EnumAnchor.Top)

        color = "0,0,255"
        width = 3

        names = [f"Poly Wave {i} - {self.result_final['P0']['Type'][i]}" for i in range(len(self.result_final['P0']['Type']))]
        start_times = self.result_final['P0']['Start_time']
        end_times = self.result_final['P0']['End_time']
        start_prices = self.result_final['P0']['Start_price']
        end_prices = self.result_final['P0']['End_price']

        chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=color, width=width, style=chart_tool.EnumStyle.Dot)


