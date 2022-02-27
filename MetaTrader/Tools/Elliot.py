from MetaTrader.Tools import Tool
from MetaTraderChartTool.BasicChartTools import BasicChartTools
from AlgorithmFactory.AlgorithmTools.Elliott import elliott

# import Tool
# from MetaTraderChartTool import BasicChartTools
# from AlgorithmFactory.AlgorithmTools.Elliott import elliott


import pandas as pd
import numpy as np


class Elliot(Tool):

    def __init__(self, data, wave4_enable, wave5_enable, inside_flat_zigzag_wc, post_prediction_enable, price_type,
                 candle_time_frame, neo_time_frame):
        super().__init__(data)

        self.wave4_enable = wave4_enable
        self.wave5_enable = wave5_enable
        self.inside_flat_zigzag_wc = inside_flat_zigzag_wc
        self.inside_flat_zigzag_wc = inside_flat_zigzag_wc
        self.post_prediction_enable = post_prediction_enable

        monowave_list, polywave_list, post_prediction_list, In_impulse_prediction_list_w4, In_impulse_prediction_list_w5, In_zigzag_flat_prediction_list = \
            elliott.calculate(pd.DataFrame(data), wave4_enable, wave5_enable, inside_flat_zigzag_wc,
                              post_prediction_enable, price_type=price_type, candle_timeframe=candle_time_frame,
                              neo_timeframe=neo_time_frame)
        # TODO : if neo_wo_merge was True Then polywave_list = []
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

            if post_prediction_enable:
                x1_list = post_prediction_list[i]['X1']
                x2_list = post_prediction_list[i]['X2']

                post_prediction_list[i]['Start_time'] = list(np.array(times)[x1_list])
                post_prediction_list[i]['End_time'] = list(np.array(times)[x2_list])

                index = "Post_Pr" + str(i)
                self.result_final[index] = post_prediction_list[i]
            if wave4_enable:
                In_x1_list = In_impulse_prediction_list_w4[i]['X1']
                In_x2_list = In_impulse_prediction_list_w4[i]['X2']

                In_impulse_prediction_list_w4[i]['Start_time'] = list(np.array(times)[In_x1_list])

                a = elliott.next_time(times[-1], candle_time_frame, In_x2_list[-1] - len(times) + 1)
                # In_zigzag_flat_prediction_list[i]['End_time'] = list(np.array(times)[inter_x2_list])
                In_impulse_prediction_list_w4[i]['End_time'] = list(np.array(times)[In_x2_list[:-1]])
                In_impulse_prediction_list_w4[i]['End_time'].append(a)

                index = "In_Pr_w4" + str(i)
                self.result_final[index] = In_impulse_prediction_list_w4[i]

            if wave5_enable:
                In_x1_list = In_impulse_prediction_list_w5[i]['X1']
                In_x2_list = In_impulse_prediction_list_w5[i]['X2']

                In_impulse_prediction_list_w5[i]['Start_time'] = list(np.array(times)[In_x1_list])
                In_impulse_prediction_list_w5[i]['End_time'] = list(np.array(times)[In_x2_list])

                index = "In_Pr_w5" + str(i)
                self.result_final[index] = In_impulse_prediction_list_w5[i]
            ###########
            # zigzag-flat inter prediction
            if inside_flat_zigzag_wc:
                inter_x1_list = In_zigzag_flat_prediction_list[i]['X1']
                inter_x2_list = In_zigzag_flat_prediction_list[i]['X2']

                In_zigzag_flat_prediction_list[i]['Start_time'] = list(np.array(times)[inter_x1_list])

                a = elliott.next_time(times[-1], candle_time_frame, inter_x2_list[-1] - len(times) + 1)
                # In_zigzag_flat_prediction_list[i]['End_time'] = list(np.array(times)[inter_x2_list])
                In_zigzag_flat_prediction_list[i]['End_time'] = list(np.array(times)[inter_x2_list[:-1]])
                In_zigzag_flat_prediction_list[i]['End_time'].append(a)

                index = "In_Pr_zigzagFlat" + str(i)
                self.result_final[index] = In_zigzag_flat_prediction_list[i]

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
                prices1.append(max(self.data[mono_wave['End_candle_index']]['High'],
                                   mono_wave['End_price']))  # max need in neowave setup
                texts1.append(f"{mono_wave['Structure_list_label']}".replace(",", "-"))
            elif mono_wave['Direction'] == -1:
                names2.append(f"Mono Wave Label {i}")
                times2.append(mono_wave['End_time'])
                prices2.append(min(self.data[mono_wave['End_candle_index']]['Low'],
                                   mono_wave['End_price']))  # min need in neowave setup
                texts2.append(f"{mono_wave['Structure_list_label']}".replace(",", "-"))

        chart_tool.text(names1, times1, prices1, texts1, anchor=chart_tool.EnumAnchor.Bottom)
        chart_tool.text(names2, times2, prices2, texts2, anchor=chart_tool.EnumAnchor.Top)

        color = "0,0,255"
        width = 3

        for i in range(len(self.result_final['P0']['Type'])):
            self.result_final['P0']['Type'][i] = f"{self.result_final['P0']['Type'][i]}".replace(",", "-")
        names = [f"Poly Wave {i} - {self.result_final['P0']['Type'][i]}" for i in
                 range(len(self.result_final['P0']['Type']))]
        start_times = self.result_final['P0']['Start_time']
        end_times = self.result_final['P0']['End_time']
        start_prices = self.result_final['P0']['Start_price']
        end_prices = self.result_final['P0']['End_price']

        chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=color, width=width,
                              style=chart_tool.EnumStyle.Dot)

        if self.post_prediction_enable:
            color = "200,255,0"
            for j in range(3):
                names = [f"Post_Prediction {j}-{i}" for i in
                         range(len(self.result_final['Post_Pr0']['Start_time']))]
                start_times = self.result_final['Post_Pr0']['Start_time']
                end_times = self.result_final['Post_Pr0']['End_time']
                start_prices = self.result_final['Post_Pr0']['Y' + str(j + 1)]
                end_prices = self.result_final['Post_Pr0']['Y' + str(j + 1)]

                chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=color,
                                      style=chart_tool.EnumStyle.Dot)

        ### inside_pattern_precition_zone impulse
        if self.wave4_enable:
            color1 = "200,200,0"
            color2 = "200,200,0"
            color3 = "255,128,128"
            start_times = []
            for j in range(4):
                names = [f"In_Prediction_w4 {j}-{i}" for i in
                         range(len(self.result_final['In_Pr_w40']['Start_time']))]
                start_times = self.result_final['In_Pr_w40']['Start_time']
                end_times = self.result_final['In_Pr_w40']['End_time']
                # start_prices = self.result_final['In_Pr_w40']['Y'+str(j+1)]
                # end_prices = self.result_final['In_Pr_w40']['Y'+str(j+1)]
                start_prices = self.result_final['In_Pr_w40']['Y1'][j]
                end_prices = self.result_final['In_Pr_w40']['Y1'][j]
                if (start_times != []):
                    if (j == 0):
                        chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=color2,
                                              style=chart_tool.EnumStyle.DashDot, width=2)
                    # pass
                    else:
                        for k in range(len(start_prices[0])):
                            chart_tool.trend_line(names, start_times, [item1[k] for item1 in start_prices], end_times,
                                                  [item2[k] for item2 in end_prices], color=color1,
                                                  style=chart_tool.EnumStyle.DashDot, width=2)
                            chart_tool.v_line([name + str(k) + '1' for name in names], times=start_times,
                                              style=chart_tool.EnumStyle.DashDot)
                            chart_tool.v_line([name + str(k) + '2' for name in names], times=end_times,
                                              style=chart_tool.EnumStyle.DashDot, color=color3)

        if self.wave5_enable:
            # color1 = "0,0,200"
            color2 = "200,0,0"
            start_times = []
            # for j in range(4):
            names = [f"In_Prediction_w5 {j}-{i}" for i in
                     range(len(self.result_final['In_Pr_w50']['Start_time']))]
            start_times = self.result_final['In_Pr_w50']['Start_time']
            end_times = self.result_final['In_Pr_w50']['End_time']
            start_prices = self.result_final['In_Pr_w50']['Y1']
            end_prices = self.result_final['In_Pr_w50']['Y1']
            if (start_times != []):
                # if (j==0 and start_prices !="none"):
                chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=color2,
                                      style=chart_tool.EnumStyle.Dot, width=2)
                # pass
            # else:
            #     chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=color1,
            #                 style=chart_tool.EnumStyle.Dot , width=2)

        # zigzag flat inter prediction
        if self.inside_flat_zigzag_wc:

            color = "200,255,255"
            for j in range(3):
                names = [f"In_Prediction_zigzagFlat {j}-{i}" for i in
                         range(len(self.result_final['In_Pr_zigzagFlat0']['Start_time']))]
                start_times = self.result_final['In_Pr_zigzagFlat0']['Start_time']
                end_times = self.result_final['In_Pr_zigzagFlat0']['End_time']
                start_prices = self.result_final['In_Pr_zigzagFlat0']['Y' + str(j + 1)]
                end_prices = self.result_final['In_Pr_zigzagFlat0']['Y' + str(j + 1)]

                chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=color,
                                      style=chart_tool.EnumStyle.Dot)






