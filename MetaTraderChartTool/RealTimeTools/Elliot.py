from MetaTraderChartTool.BasicChartTools import BasicChartTools
from MetaTraderChartTool.RealTimeTools.RealTimeTool import RealTimeTool

from AlgorithmFactory.AlgorithmTools.Elliott import elliott

import pandas as pd
import numpy as np


class Elliot(RealTimeTool):

    def __init__(self, chart_tool: BasicChartTools, data, price_type, candle_time_frame, neo_time_frame, past_check_num, window):
        super().__init__(chart_tool, data)

        self.wave4_enable = False
        self.wave5_enable = False
        self.inside_flat_zigzag_wc = False
        self.inside_flat_zigzag_wc = False
        self.post_prediction_enable = False

        self.price_type = price_type
        self.past_check_num = past_check_num

        self.candle_time_frame = candle_time_frame
        self.neo_time_frame = neo_time_frame

        self.window = window

        monowave_list, polywave_list, post_prediction_list, In_impulse_prediction_list_w4 , In_impulse_prediction_list_w5, In_zigzag_flat_prediction_list =\
        elliott.calculate(pd.DataFrame(data), self.wave4_enable, self.wave5_enable, self.inside_flat_zigzag_wc, self.post_prediction_enable, price_type=self.price_type, candle_timeframe=candle_time_frame, neo_timeframe=neo_time_frame)

        self.pre_monowave_time = self.data[monowave_list[0]['Start_candle_index'][len(monowave_list[0]['Start_candle_index'])-self.past_check_num]]['Time']

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

            if self.post_prediction_enable:
                x1_list = post_prediction_list[i]['X1']
                x2_list = post_prediction_list[i]['X2']

                post_prediction_list[i]['Start_time'] = list(np.array(times)[x1_list])
                post_prediction_list[i]['End_time'] = list(np.array(times)[x2_list])

                index = "Post_Pr" + str(i)
                self.result_final[index] = post_prediction_list[i]
            if self.wave4_enable:
                In_x1_list = In_impulse_prediction_list_w4[i]['X1']
                In_x2_list = In_impulse_prediction_list_w4[i]['X2']

                In_impulse_prediction_list_w4[i]['Start_time'] = list(np.array(times)[In_x1_list])
                In_impulse_prediction_list_w4[i]['End_time'] = list(np.array(times)[In_x2_list])

                index = "In_Pr_w4" + str(i)
                self.result_final[index] = In_impulse_prediction_list_w4[i]

            if self.wave5_enable:
                In_x1_list = In_impulse_prediction_list_w5[i]['X1']
                In_x2_list = In_impulse_prediction_list_w5[i]['X2']

                In_impulse_prediction_list_w5[i]['Start_time'] = list(np.array(times)[In_x1_list])
                In_impulse_prediction_list_w5[i]['End_time'] = list(np.array(times)[In_x2_list])

                index = "In_Pr_w5" + str(i)
                self.result_final[index] = In_impulse_prediction_list_w5[i]
            ###########
            #zigzag-flat inter prediction
            if self.inside_flat_zigzag_wc:
                inter_x1_list = In_zigzag_flat_prediction_list[i]['X1']
                inter_x2_list = In_zigzag_flat_prediction_list[i]['X2']

                In_zigzag_flat_prediction_list[i]['Start_time'] = list(np.array(times)[inter_x1_list])
                In_zigzag_flat_prediction_list[i]['End_time'] = list(np.array(times)[inter_x2_list])

                index = "In_Pr_zigzagFlat" + str(i)
                self.result_final[index] = In_zigzag_flat_prediction_list[i]


            color = "255,255,255"
            width = 2

            names = [f"Mono Wave {i}" for i in range(len(self.result_final['M0']))]
            start_times = [item['Start_time'] for item in self.result_final['M0']]
            end_times = [item['End_time'] for item in self.result_final['M0']]
            start_prices = [item['Start_price'] for item in self.result_final['M0']]
            end_prices = [item['End_price'] for item in self.result_final['M0']]

            chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=color, width=width)

            self.last_monowave_names = [names[-i] for i in range(self.past_check_num, 0, -1)]
            self.last_monowave_index = len(self.result_final['M0'])-1
            self.last_monowave_index_head = len(self.result_final['M0'])-self.past_check_num

            names1, times1, prices1, texts1 = [], [], [], []
            names2, times2, prices2, texts2 = [], [], [], []
            i = 0
            for mono_wave in self.result_final['M0']:
                if mono_wave['Direction'] == 1:
                    names1.append(f"Mono Wave Label {i}")
                    times1.append(mono_wave['End_time'])
                    prices1.append(max(self.data[mono_wave['End_candle_index']]['High'], mono_wave['End_price'])) # max need in neowave setup
                    texts1.append(f"{mono_wave['Structure_list_label']}".replace(",", "-"))
                elif mono_wave['Direction'] == -1:
                    names2.append(f"Mono Wave Label {i}")
                    times2.append(mono_wave['End_time'])
                    prices2.append(min(self.data[mono_wave['End_candle_index']]['Low'], mono_wave['End_price']))  # min need in neowave setup
                    texts2.append(f"{mono_wave['Structure_list_label']}".replace(",", "-"))
                i += 1

            chart_tool.text(names1, times1, prices1, texts1, anchor=chart_tool.EnumAnchor.Bottom)
            chart_tool.text(names2, times2, prices2, texts2, anchor=chart_tool.EnumAnchor.Top)

            self.color = "0,0,255"
            self.width = 3

            for i in range(len(self.result_final['P0']['Type'])):
                self.result_final['P0']['Type'][i] = f"{self.result_final['P0']['Type'][i]}".replace(",", "-")
            names = [f"Poly Wave {i} - {self.result_final['P0']['Type'][i]}" for i in range(len(self.result_final['P0']['Type']))]
            start_times = self.result_final['P0']['Start_time']
            end_times = self.result_final['P0']['End_time']
            start_prices = self.result_final['P0']['Start_price']
            end_prices = self.result_final['P0']['End_price']

            chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=self.color, width=self.width, style=chart_tool.EnumStyle.Dot)

            self.last_polywave = {"Start": max(start_times), "End": max(end_times), "Index": len(self.result_final['P0']['Type'])}

            if self.post_prediction_enable:
                color = "200,255,0"
                for j in range(3):
                    names = [f"Post_Prediction {j}-{i}" for i in
                            range(len(self.result_final['Post_Pr0']['Start_time']))]
                    start_times = self.result_final['Post_Pr0']['Start_time']
                    end_times = self.result_final['Post_Pr0']['End_time']
                    start_prices = self.result_final['Post_Pr0']['Y'+str(j+1)]
                    end_prices = self.result_final['Post_Pr0']['Y'+str(j+1)]

                    chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=color,
                                        style=chart_tool.EnumStyle.Dot)

            ### inside_pattern_precition_zone
            if self.wave4_enable:
                color1 = "0,0,200"
                color2 = "20,0,150"
                start_times =[]
                for j in range(4):
                    names = [f"In_Prediction_w4 {j}-{i}" for i in
                                range(len(self.result_final['In_Pr_w40']['Start_time']))]
                    start_times = self.result_final['In_Pr_w40']['Start_time']
                    end_times = self.result_final['In_Pr_w40']['End_time']
                    start_prices = self.result_final['In_Pr_w40']['Y'+str(j+1)]
                    end_prices = self.result_final['In_Pr_w40']['Y'+str(j+1)]
                    if (start_times != []):
                        if (j==0 and start_prices !="none"):
                            chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=color2,
                                        style=chart_tool.EnumStyle.Dot , width=2)
                            # pass
                        else:
                            chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=color1,
                                        style=chart_tool.EnumStyle.Dot , width=2)

            if self.wave5_enable:
                # color1 = "0,0,200"
                color2 = "200,0,0"
                start_times =[]
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
                                style=chart_tool.EnumStyle.Dot , width=2)
                    # pass
                # else:
                #     chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=color1,
                #                 style=chart_tool.EnumStyle.Dot , width=2)

            if self.inside_flat_zigzag_wc:
                # zigzag flat inter prediction
                color = "200,255,255"
                for j in range(3):
                    names = [f"In_Prediction_zigzagFlat {j}-{i}" for i in
                            range(len(self.result_final['In_Pr_zigzagFlat0']['Start_time']))]
                    start_times = self.result_final['In_Pr_zigzagFlat0']['Start_time']
                    end_times = self.result_final['In_Pr_zigzagFlat0']['End_time']
                    start_prices = self.result_final['In_Pr_zigzagFlat0']['Y'+str(j+1)]
                    end_prices = self.result_final['In_Pr_zigzagFlat0']['Y'+str(j+1)]

                    chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=color,
                                        style=chart_tool.EnumStyle.Dot)

        self.data = self.data[-self.window:] # batch data mode for better performance

    def on_tick(self, time, bid, ask):
        pass

    def on_data(self, candle):
        self.data.pop(0)

        # self.chart_tool.connector.send_clear_request()
        #
        # monowave_list, polywave_list, post_prediction_list, In_impulse_prediction_list_w4 , In_impulse_prediction_list_w5, In_zigzag_flat_prediction_list =\
        # elliott.calculate(pd.DataFrame(self.data), self.wave4_enable, self.wave5_enable, self.inside_flat_zigzag_wc, self.post_prediction_enable, price_type=self.price_type, candle_timeframe="H4", neo_timeframe="d1")
        #
        # self.pre_monowave_list = monowave_list
        #
        # # TODO : if neo_wo_merge was True Then polywave_lsit = []
        # self.result_final = {}
        # results = []
        # times = [row['Time'] for row in self.data]
        # for i in range(len(monowave_list)):
        #     results.append(monowave_list[i].reset_index())
        #     # add start and end DateTime to the output dataframe
        #     start_time_list = results[i]['Start_candle_index'].tolist()
        #     end_time_list = results[i]['End_candle_index'].tolist()
        #     results[i]['Start_time'] = list(np.array(times)[start_time_list])
        #     results[i]['End_time'] = list(np.array(times)[end_time_list])
        #
        #     index = "M" + str(i)
        #     self.result_final[index] = results[i].to_dict("records")
        #
        #     start_time_list = polywave_list[i]['Start_index']
        #     end_time_list = polywave_list[i]['End_index']
        #
        #     polywave_list[i]['Start_time'] = list(np.array(times)[start_time_list])
        #     polywave_list[i]['End_time'] = list(np.array(times)[end_time_list])
        #
        #     index = "P" + str(i)
        #     self.result_final[index] = polywave_list[i]
        #
        #     if self.post_prediction_enable:
        #         x1_list = post_prediction_list[i]['X1']
        #         x2_list = post_prediction_list[i]['X2']
        #
        #         post_prediction_list[i]['Start_time'] = list(np.array(times)[x1_list])
        #         post_prediction_list[i]['End_time'] = list(np.array(times)[x2_list])
        #
        #         index = "Post_Pr" + str(i)
        #         self.result_final[index] = post_prediction_list[i]
        #     if self.wave4_enable:
        #         In_x1_list = In_impulse_prediction_list_w4[i]['X1']
        #         In_x2_list = In_impulse_prediction_list_w4[i]['X2']
        #
        #         In_impulse_prediction_list_w4[i]['Start_time'] = list(np.array(times)[In_x1_list])
        #         In_impulse_prediction_list_w4[i]['End_time'] = list(np.array(times)[In_x2_list])
        #
        #         index = "In_Pr_w4" + str(i)
        #         self.result_final[index] = In_impulse_prediction_list_w4[i]
        #
        #     if self.wave5_enable:
        #         In_x1_list = In_impulse_prediction_list_w5[i]['X1']
        #         In_x2_list = In_impulse_prediction_list_w5[i]['X2']
        #
        #         In_impulse_prediction_list_w5[i]['Start_time'] = list(np.array(times)[In_x1_list])
        #         In_impulse_prediction_list_w5[i]['End_time'] = list(np.array(times)[In_x2_list])
        #
        #         index = "In_Pr_w5" + str(i)
        #         self.result_final[index] = In_impulse_prediction_list_w5[i]
        #     ###########
        #     #zigzag-flat inter prediction
        #     if self.inside_flat_zigzag_wc:
        #         inter_x1_list = In_zigzag_flat_prediction_list[i]['X1']
        #         inter_x2_list = In_zigzag_flat_prediction_list[i]['X2']
        #
        #         In_zigzag_flat_prediction_list[i]['Start_time'] = list(np.array(times)[inter_x1_list])
        #         In_zigzag_flat_prediction_list[i]['End_time'] = list(np.array(times)[inter_x2_list])
        #
        #         index = "In_Pr_zigzagFlat" + str(i)
        #         self.result_final[index] = In_zigzag_flat_prediction_list[i]
        #
        #
        #     color = "255,255,255"
        #     width = 2
        #
        #     names = [f"Mono Wave {i}" for i in range(len(self.result_final['M0']))]
        #     start_times = [item['Start_time'] for item in self.result_final['M0']]
        #     end_times = [item['End_time'] for item in self.result_final['M0']]
        #     start_prices = [item['Start_price'] for item in self.result_final['M0']]
        #     end_prices = [item['End_price'] for item in self.result_final['M0']]
        #
        #     self.chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=color, width=width)
        #
        #     self.last_monowave_name = names[-1]
        #     self.last_monowave_index = len(self.result_final['M0'])-1
        #
        #     names1, times1, prices1, texts1 = [], [], [], []
        #     names2, times2, prices2, texts2 = [], [], [], []
        #     i = 0
        #     for mono_wave in self.result_final['M0']:
        #         i += 1
        #         if mono_wave['Direction'] == 1:
        #             names1.append(f"Mono Wave Label {i}")
        #             times1.append(mono_wave['End_time'])
        #             prices1.append(max(self.data[mono_wave['End_candle_index']]['High'], mono_wave['End_price'])) # max need in neowave setup
        #             texts1.append(f"{mono_wave['Structure_list_label']}".replace(",", "-"))
        #         elif mono_wave['Direction'] == -1:
        #             names2.append(f"Mono Wave Label {i}")
        #             times2.append(mono_wave['End_time'])
        #             prices2.append(min(self.data[mono_wave['End_candle_index']]['Low'], mono_wave['End_price']))  # min need in neowave setup
        #             texts2.append(f"{mono_wave['Structure_list_label']}".replace(",", "-"))
        #
        #     self.chart_tool.text(names1, times1, prices1, texts1, anchor=self.chart_tool.EnumAnchor.Bottom)
        #     self.chart_tool.text(names2, times2, prices2, texts2, anchor=self.chart_tool.EnumAnchor.Top)
        #
        #
        #
        #     color = "0,0,255"
        #     width = 3
        #
        #     for i in range(len(self.result_final['P0']['Type'])):
        #         self.result_final['P0']['Type'][i] = f"{self.result_final['P0']['Type'][i]}".replace(",", "-")
        #     names = [f"Poly Wave {i} - {self.result_final['P0']['Type'][i]}" for i in range(len(self.result_final['P0']['Type']))]
        #     start_times = self.result_final['P0']['Start_time']
        #     end_times = self.result_final['P0']['End_time']
        #     start_prices = self.result_final['P0']['Start_price']
        #     end_prices = self.result_final['P0']['End_price']
        #
        #     self.chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=color, width=width, style=self.chart_tool.EnumStyle.Dot)
        #
        #     if self.post_prediction_enable:
        #         color = "200,255,0"
        #         for j in range(3):
        #             names = [f"Post_Prediction {j}-{i}" for i in
        #                     range(len(self.result_final['Post_Pr0']['Start_time']))]
        #             start_times = self.result_final['Post_Pr0']['Start_time']
        #             end_times = self.result_final['Post_Pr0']['End_time']
        #             start_prices = self.result_final['Post_Pr0']['Y'+str(j+1)]
        #             end_prices = self.result_final['Post_Pr0']['Y'+str(j+1)]
        #
        #             self.chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=color,
        #                                 style=self.chart_tool.EnumStyle.Dot)
        #
        #     ### inside_pattern_precition_zone
        #     if self.wave4_enable:
        #         color1 = "0,0,200"
        #         color2 = "20,0,150"
        #         start_times =[]
        #         for j in range(4):
        #             names = [f"In_Prediction_w4 {j}-{i}" for i in
        #                         range(len(self.result_final['In_Pr_w40']['Start_time']))]
        #             start_times = self.result_final['In_Pr_w40']['Start_time']
        #             end_times = self.result_final['In_Pr_w40']['End_time']
        #             start_prices = self.result_final['In_Pr_w40']['Y'+str(j+1)]
        #             end_prices = self.result_final['In_Pr_w40']['Y'+str(j+1)]
        #             if (start_times != []):
        #                 if (j==0 and start_prices !="none"):
        #                     self.chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=color2,
        #                                 style=self.chart_tool.EnumStyle.Dot , width=2)
        #                     # pass
        #                 else:
        #                     self.chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=color1,
        #                                 style=self.chart_tool.EnumStyle.Dot , width=2)
        #
        #     if self.wave5_enable:
        #         # color1 = "0,0,200"
        #         color2 = "200,0,0"
        #         start_times =[]
        #         # for j in range(4):
        #         names = [f"In_Prediction_w5 {j}-{i}" for i in
        #                     range(len(self.result_final['In_Pr_w50']['Start_time']))]
        #         start_times = self.result_final['In_Pr_w50']['Start_time']
        #         end_times = self.result_final['In_Pr_w50']['End_time']
        #         start_prices = self.result_final['In_Pr_w50']['Y1']
        #         end_prices = self.result_final['In_Pr_w50']['Y1']
        #         if (start_times != []):
        #             # if (j==0 and start_prices !="none"):
        #             self.chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=color2,
        #                         style=self.chart_tool.EnumStyle.Dot , width=2)
        #             # pass
        #         # else:
        #         #     chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=color1,
        #         #                 style=chart_tool.EnumStyle.Dot , width=2)
        #
        #     if self.inside_flat_zigzag_wc:
        #         # zigzag flat inter prediction
        #         color = "200,255,255"
        #         for j in range(3):
        #             names = [f"In_Prediction_zigzagFlat {j}-{i}" for i in
        #                     range(len(self.result_final['In_Pr_zigzagFlat0']['Start_time']))]
        #             start_times = self.result_final['In_Pr_zigzagFlat0']['Start_time']
        #             end_times = self.result_final['In_Pr_zigzagFlat0']['End_time']
        #             start_prices = self.result_final['In_Pr_zigzagFlat0']['Y'+str(j+1)]
        #             end_prices = self.result_final['In_Pr_zigzagFlat0']['Y'+str(j+1)]
        #
        #             self.chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=color,
        #                                 style=self.chart_tool.EnumStyle.Dot)

        monowave_list, polywave_list, post_prediction_list, In_impulse_prediction_list_w4,\
        In_impulse_prediction_list_w5, In_zigzag_flat_prediction_list = elliott.calculate(
            pd.DataFrame(self.data),
            self.wave4_enable,
            self.wave5_enable,
            self.inside_flat_zigzag_wc,
            self.post_prediction_enable,
            price_type=self.price_type,
            candle_timeframe=self.candle_time_frame,
            neo_timeframe=self.neo_time_frame)

        last_index = self.last_monowave_index

        mw_len = len(monowave_list[0]['Start_candle_index'])
        i = mw_len - 1
        while True:
            if self.data[monowave_list[0]['Start_candle_index'][i]]['Time'] == self.pre_monowave_time:
                self.chart_tool.delete(self.last_monowave_names)

                names, start_time, start_price, end_time, end_price = [], [], [], [], []

                index = self.last_monowave_index_head
                for j in range(i, mw_len):
                    names.append(f"Mono Wave {index}")
                    start_time.append(self.data[monowave_list[0]['Start_candle_index'][j]]['Time'])
                    start_price.append(monowave_list[0]['Start_price'][j])
                    end_time.append(self.data[monowave_list[0]['End_candle_index'][j]]['Time'])
                    end_price.append(monowave_list[0]['End_price'][j])
                    index += 1
                    if monowave_list[0]['End_price'][j] is None:
                        print("Nan")

                self.last_monowave_index = index
                self.last_monowave_index_head = index - self.past_check_num

                self.chart_tool.trend_line(names, start_time, start_price, end_time, end_price, width=2)

                for j in range(self.past_check_num):
                    self.last_monowave_names[j] = f"Mono Wave {self.last_monowave_index - (self.past_check_num - 1 - j)}"

                self.pre_monowave_time = self.data[monowave_list[0]['Start_candle_index'][mw_len - self.past_check_num]]['Time']

                break
            else:
                i -= 1

        if len(polywave_list[0]['Start_index']) != 0:
            if self.data[max(polywave_list[0]['Start_index'])]['Time'] != self.last_polywave['Start'] or \
                    self.data[max(polywave_list[0]['End_index'])]['Time'] != self.last_polywave['End']:
                i = 1
                names, start_times, start_prices, end_times, end_prices = [], [], [], [], []
                for i in range(len(polywave_list[0]['Start_index'])):
                    if self.data[polywave_list[0]['Start_index'][i]]['Time'] > self.last_polywave['Start'] or self.data[polywave_list[0]['End_index'][i]]['Time'] > self.last_polywave['End']:
                        if polywave_list[0]['Start_index'][i] > self.window // 5:
                            polywave_list[0]['Type'][i] = f"{polywave_list[0]['Type'][i]}".replace(",", "-")
                            names.append(f"Poly Wave {self.last_polywave['Index']} - {polywave_list[0]['Type'][i]}")
                            start_times.append(self.data[polywave_list[0]['Start_index'][i]]['Time'])
                            end_times.append(self.data[polywave_list[0]['End_index'][i]]['Time'])
                            start_prices.append(polywave_list[0]['Start_price'][i])
                            end_prices.append(polywave_list[0]['End_price'][i])
                            self.last_polywave['Index'] += 1

                if len(start_times) != 0:
                    self.last_polywave['Start'] = max(start_times)
                    self.last_polywave['End'] = max(end_times)

                    self.chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=self.color,
                                          width=self.width, style=self.chart_tool.EnumStyle.Dot)

        #
        # print("Line")
        # mw_len = len(monowave_list[0]['Start_candle_index'])
        # if self.data[monowave_list[0]['Start_candle_index'].values[-2]]['Time'] == self.pre_last_monowave_time or self.data[monowave_list[0]['Start_candle_index'].values[-1]]['Time'] == self.pre_last_monowave_time:
        #     self.chart_tool.delete(self.last_monowave_names)
        #     start_times = [self.data[monowave_list[0]['Start_candle_index'][mw_len-i]]['Time'] for i in range(self.past_check_num, 0, -1)]
        #     start_prices = [monowave_list[0]['Start_price'][mw_len-i] for i in range(self.past_check_num, 0, -1)]
        #     end_times = [self.data[monowave_list[0]['End_candle_index'][mw_len-i]]['Time'] for i in range(self.past_check_num, 0, -1)]
        #     end_prices = [monowave_list[0]['End_price'][mw_len-i] for i in range(self.past_check_num, 0, -1)]
        #     print("Edit Line")
        #     self.chart_tool.trend_line(self.last_monowave_names, start_times, start_prices, end_times, end_prices, width=2)
        # else:
        #     self.chart_tool.delete(self.last_monowave_names)
        #     self.last_monowave_index -= 1
        #     names, start_time, start_price, end_time, end_price = [], [], [], [], []
        #     for i in range(mw_len-1, 0, -1):
        #         if self.data[monowave_list[0]['Start_candle_index'].values[i]]['Time'] == self.pre_last_monowave_time:
        #             n_new_mw =  mw_len - i
        #             for j in range(n_new_mw):
        #                 self.last_monowave_index += 1
        #                 for k in range(self.past_check_num, 1, -1):
        #                     self.last_monowave_names[-k] = self.last_monowave_names[-k+1]
        #                 self.last_monowave_names[-1] = f"Mono Wave {self.last_monowave_index}"
        #                 names.append(self.last_monowave_names[-1])
        #                 start_time.append(self.data[monowave_list[0]['Start_candle_index'][i+j]]['Time'])
        #                 start_price.append(monowave_list[0]['Start_price'][i+j])
        #                 end_time.append(self.data[monowave_list[0]['End_candle_index'][i+j]]['Time'])
        #                 end_price.append(monowave_list[0]['End_price'][i+j])
        #             print(f"num of new Lines: {n_new_mw}")
        #             print(start_time)
        #             self.pre_last_monowave_time = self.data[monowave_list[0]['Start_candle_index'][mw_len-self.past_check_num]]['Time']
        #             self.chart_tool.trend_line(names, start_time, start_price, end_time, end_price, width=2)

        labels_num = 5
        mw_label = [f"Mono Wave Label {i}" for i in range(last_index, max(1, self.last_monowave_index-labels_num), -1)]
        self.chart_tool.delete(mw_label)

        names1, times1, prices1, texts1 = [], [], [], []
        names2, times2, prices2, texts2 = [], [], [], []
        i = 0

        for i in range(max(0, len(monowave_list[0])-labels_num), len(monowave_list[0])):
            if monowave_list[0]['Direction'][i] == 1:
                names1.append(f"Mono Wave Label {self.last_monowave_index - (len(monowave_list[0]) - i) + 1}")
                times1.append(self.data[monowave_list[0]['End_candle_index'][i]]['Time'])
                prices1.append(max(self.data[monowave_list[0]['End_candle_index'][i]]['High'], monowave_list[0]['End_price'][i])) # max need in neowave setup
                texts1.append(f"{monowave_list[0]['Structure_list_label'][i]}".replace(",", "-"))
            elif monowave_list[0]['Direction'][i] == -1:
                names2.append(f"Mono Wave Label {self.last_monowave_index - (len(monowave_list[0]) - i) + 1}")
                times2.append(self.data[monowave_list[0]['End_candle_index'][i]]['Time'])
                prices2.append(min(self.data[monowave_list[0]['End_candle_index'][i]]['Low'], monowave_list[0]['End_price'][i]))  # min need in neowave setup
                texts2.append(f"{monowave_list[0]['Structure_list_label'][i]}".replace(",", "-"))

        self.chart_tool.text(names1, times1, prices1, texts1, anchor=self.chart_tool.EnumAnchor.Bottom)
        self.chart_tool.text(names2, times2, prices2, texts2, anchor=self.chart_tool.EnumAnchor.Top)

        self.data.append(candle)
