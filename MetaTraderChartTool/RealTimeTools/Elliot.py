from MetaTrader.MetaTraderBase import MetaTraderBase
from MetaTraderChartTool.RealTimeTools.RealTimeTool import RealTimeTool
from Configuration.Trade.OnlineConfig import Config

from AlgorithmFactory.AlgorithmTools.Elliott import elliott

import pandas as pd
import numpy as np
from Utilities.Statistics import *
import pickle


class Elliot(RealTimeTool):

    def __init__(self, chart_tool: MetaTraderBase, data, symbol, wave4_enable, wave5_enable, inside_flat_zigzag_wc, post_prediction_enable, price_type, candle_time_frame, neo_time_frame, past_check_num, window, statistic_window, trade_enable):
        super().__init__(chart_tool, data)

        self.chart_tool.set_speed(10000)
        self.chart_tool.set_candle_start_delay(40)

        self.color = "40,180,60"
        self.width = 1

        self.rect_color = "4,129,25"
        self.rect_x, self.rect_y = 20, 40
        self.rect_width, self.rect_height = 300, 250
        self.label = f"Elliot"

        self.symbol = symbol
        self.trade_enable = trade_enable
        self.wave4_enable = wave4_enable
        self.wave5_enable = wave5_enable
        self.inside_flat_zigzag_wc = inside_flat_zigzag_wc
        self.post_prediction_enable = post_prediction_enable

        self.price_type = price_type
        self.past_check_num = past_check_num

        self.candle_time_frame = candle_time_frame
        self.neo_time_frame = neo_time_frame

        self.window = window

        monowave_list, polywave_list, post_prediction_list, In_impulse_prediction_list_w4 , In_impulse_prediction_list_w5, In_zigzag_flat_prediction_list =\
        elliott.calculate(pd.DataFrame(data), self.wave4_enable, self.wave5_enable, self.inside_flat_zigzag_wc, self.post_prediction_enable, price_type=self.price_type, candle_timeframe=candle_time_frame, neo_timeframe=neo_time_frame)

        pickle_out = open("data.pickle", "wb")
        pickle.dump(self.data, pickle_out)
        pickle_out.close()

        pickle_out = open("monowave.pickle", "wb")
        pickle.dump(monowave_list, pickle_out)
        pickle_out.close()

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

                directions_list = post_prediction_list[i]['Dr']

                buy_indexes, sell_indexes = [], []
                for l in range(len(x1_list)):
                    if directions_list[l] == 1:
                        sell_indexes.append(x1_list[l])
                    else:
                        buy_indexes.append(x1_list[l])

                self.get_statistics(buy_indexes, statistic_window)
                self.label = f"Elliot Buy ({statistic_window}) Post Prediction"
                self.draw_statistics()
                self.get_statistics(sell_indexes, statistic_window)
                self.rect_x, self.rect_y = 20, self.rect_height + 60
                self.label = f"Elliot Sell ({statistic_window}) Post Prediction"
                self.draw_statistics()

                post_prediction_list[i]['Start_time'] = list(np.array(times)[x1_list])
                post_prediction_list[i]['End_time'] = list(np.array(times)[x2_list])

                index = "Post_Pr" + str(i)
                self.result_final[index] = post_prediction_list[i]
            if self.wave4_enable:
                In_x1_list = In_impulse_prediction_list_w4[i]['X1']
                In_x2_list = In_impulse_prediction_list_w4[i]['X2']

                directions_list = In_impulse_prediction_list_w4[i]['Dr']

                buy_indexes, sell_indexes = [], []
                for l in range(len(In_x1_list)):
                    if directions_list[l] == 1:
                        sell_indexes.append(In_x1_list[l])
                    else:
                        buy_indexes.append(In_x1_list[l])

                self.get_statistics(buy_indexes, statistic_window)
                self.label = f"Elliot Buy ({statistic_window}) W4"
                self.draw_statistics()
                self.get_statistics(sell_indexes, statistic_window)
                self.rect_x, self.rect_y = 20, self.rect_height + 60
                self.label = f"Elliot Sell ({statistic_window}) W4"
                self.draw_statistics()


                In_impulse_prediction_list_w4[i]['Start_time'] = list(np.array(times)[In_x1_list])
                a = elliott.next_time(times[-1], candle_time_frame, In_x2_list[-1] - len(times) + 1)
                if a is None:
                    a = times[-1]
                # In_zigzag_flat_prediction_list[i]['End_time'] = list(np.array(times)[inter_x2_list])
                In_impulse_prediction_list_w4[i]['End_time'] = list(np.array(times)[In_x2_list[:-1]])
                In_impulse_prediction_list_w4[i]['End_time'].append(a)

                index = "In_Pr_w4" + str(i)
                self.result_final[index] = In_impulse_prediction_list_w4[i]

            if self.wave5_enable:
                In_x1_list = In_impulse_prediction_list_w5[i]['X1']
                In_x2_list = In_impulse_prediction_list_w5[i]['X2']

                directions_list = In_impulse_prediction_list_w5[i]['Dr']

                buy_indexes, sell_indexes = [], []
                for l in range(len(In_x1_list)):
                    if directions_list[l] == 1:
                        sell_indexes.append(In_x1_list[l])
                    else:
                        buy_indexes.append(In_x1_list[l])


                self.get_statistics(buy_indexes, statistic_window)
                self.label = f"Elliot Buy ({statistic_window}) W5"
                self.draw_statistics()
                self.get_statistics(sell_indexes, statistic_window)
                self.rect_x, self.rect_y = 20, self.rect_height + 60
                self.label = f"Elliot Sell ({statistic_window}) W5"
                self.draw_statistics()

                In_impulse_prediction_list_w5[i]['Start_time'] = list(np.array(times)[In_x1_list])
                a = elliott.next_time(times[-1], candle_time_frame, In_x2_list[-1] - len(times) + 1)
                if a is None:
                    a = times[-1]
                # In_zigzag_flat_prediction_list[i]['End_time'] = list(np.array(times)[inter_x2_list])
                In_impulse_prediction_list_w5[i]['End_time'] = list(np.array(times)[In_x2_list[:-1]])
                In_impulse_prediction_list_w5[i]['End_time'].append(a)

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
                
                self.last_post_prediction_time = self.result_final['Post_Pr0']['Start_time'][-1]
                self.last_post_prediction_index = post_prediction_list[0]['X1'][-1]

            ### inside_pattern_precition_zone
            if self.wave4_enable:
                self.color1 = "200,200,0"
                self.color2 = "200,200,0"
                self.color3 = "255,128,128"
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
                            chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=self.color2,
                                                  style=chart_tool.EnumStyle.DashDot, width=2)
                        # pass
                        else:
                            for k in range(len(start_prices[0])):
                                chart_tool.trend_line(names, start_times, [item1[k] for item1 in start_prices],
                                                      end_times,
                                                      [item2[k] for item2 in end_prices], color=self.color1,
                                                      style=chart_tool.EnumStyle.DashDot, width=2)
                                chart_tool.v_line([name + str(k) + '1' for name in names], times=start_times,
                                                  style=chart_tool.EnumStyle.DashDot)
                                chart_tool.v_line([name + str(k) + '2' for name in names], times=end_times,
                                                  style=chart_tool.EnumStyle.DashDot, color=self.color3)

                self.last_prediction_w4_time = self.result_final['In_Pr_w40']['Start_time'][-1]
                self.last_prediction_w4_index = In_impulse_prediction_list_w4[0]['X1'][-1]

            if self.wave5_enable:
                self.color1 = "200,200,0"
                self.color2 = "200,200,0"
                self.color3 = "255,128,128"
                start_times = []
                for j in range(len(self.result_final['In_Pr_w50']['Y1'][0])):
                    names = [f"In_Prediction_w5 {j}-{k}" for k in
                                range(len(self.result_final['In_Pr_w50']['Start_time']))]
                    start_times = self.result_final['In_Pr_w50']['Start_time']
                    end_times = self.result_final['In_Pr_w50']['End_time']
                    # start_prices = self.result_final['In_Pr_w40']['Y'+str(j+1)]
                    # end_prices = self.result_final['In_Pr_w40']['Y'+str(j+1)]
                    start_prices = [self.result_final['In_Pr_w50']['Y1'][l][j] for l in range(len(self.result_final['In_Pr_w50']['Y1']))]
                    end_prices = start_prices
                    # if (start_times != []):
                        # if (j == 0):
                    chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=self.color2,
                                                    style=chart_tool.EnumStyle.DashDot, width=2)
                            # pass
                        # else:
                        #     for k in range(len(start_prices[0])):
                        #         chart_tool.trend_line(names, start_times, [item1[k] for item1 in start_prices],
                        #                               end_times,
                        #                               [item2[k] for item2 in end_prices], color=self.color1,
                        #                               style=chart_tool.EnumStyle.DashDot, width=2)
                        #         chart_tool.v_line([name + str(k) + '1' for name in names], times=start_times,
                        #                           style=chart_tool.EnumStyle.DashDot)
                        #         chart_tool.v_line([name + str(k) + '2' for name in names], times=end_times,
                        #                           style=chart_tool.EnumStyle.DashDot, color=self.color3)

                self.last_prediction_w5_time = self.result_final['In_Pr_w50']['Start_time'][-1]
                self.last_prediction_w5_index = In_impulse_prediction_list_w5[0]['X1'][-1]

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

        if self.wave4_enable:
            if len(In_impulse_prediction_list_w4[0]['X1']) != 0:
                if self.data[In_impulse_prediction_list_w4[0]['X1'][-1]]['Time'] > self.last_prediction_w4_time \
                and self.data[In_impulse_prediction_list_w4[0]['X1'][-1]]['Time'] == self.data[monowave_list[0]['Start_candle_index'][mw_len -1]]['Time']:
                    self.last_prediction_w4_index += 1
                    self.last_prediction_w4_time = self.data[In_impulse_prediction_list_w4[0]['X1'][-1]]['Time']
                    tp_list = []
                    for j in range(4):
             
                        # start_times = [self.data[In_impulse_prediction_list_w4[0]['X1'][-1]]['Time']]
                        start_times = [candle['Time']]
                        end_times = [candle['Time'] + (In_impulse_prediction_list_w4[0]['X2'][-1] -In_impulse_prediction_list_w4[0]['X1'][-1]) \
                                     * min(self.data[-1]['Time'] - self.data[-2]['Time'], self.data[-2]['Time'] - self.data[-3]['Time'])]
                        # if In_impulse_prediction_list_w4[0]['X2'][-1] >= len(self.data):
                        #     end_times = [self.data[-1]['Time'] + ((In_impulse_prediction_list_w4[0]['X2'][-1]-In_impulse_prediction_list_w4[0]['X1'][-1]) - len(self.data))\
                        #                  * min(self.data[-1]['Time'] - self.data[-2]['Time'], self.data[-2]['Time'] - self.data[-3]['Time'])]
                        # else:
                        #     end_times = [self.data[In_impulse_prediction_list_w4[0]['X2'][-1]]['Time']]

                        # Shift prediction times 3 candles for synchronization

                        # start_prices = self.result_final['In_Pr_w40']['Y'+str(j+1)]
                        # end_prices = self.result_final['In_Pr_w40']['Y'+str(j+1)]
                        start_prices = In_impulse_prediction_list_w4[0]['Y1'][j][-1]
                        end_prices = In_impulse_prediction_list_w4[0]['Y1'][j][-1]

                        tp_list += start_prices


                        names = [f"In_Prediction_w4 {j}-{self.last_prediction_w4_index}-{i}" for i in range(len(start_prices))]
                        start_times = start_times*len(start_prices)
                        end_times = end_times * len(start_prices)
                        if (start_times != []):
                            if (j == 0):
                                self.chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=self.color2,
                                                      style=self.chart_tool.EnumStyle.DashDot, width=2)
                            # pass
                            else:
                                self.chart_tool.trend_line(names, start_times, start_prices,
                                                          end_times,end_prices, color=self.color1,
                                                          style=self.chart_tool.EnumStyle.DashDot, width=2)
                                self.chart_tool.v_line([f"{names[-1]}_1"], times=[start_times[0]],
                                                  style=self.chart_tool.EnumStyle.DashDot)
                                self.chart_tool.v_line([f"{names[-1]}_2"], times=[end_times[0]],
                                                  style=self.chart_tool.EnumStyle.DashDot, color=self.color3)
                    tp_list = [tp_list[i] for i in range(len(tp_list)) if tp_list[i] != 'none']
                    if len(tp_list) != 0 and self.trade_enable:
                        tp = abs(tp_list[0] - self.data[-1]['Close']) * 10 ** Config.symbols_pip[self.symbol]
                        if tp_list[0] > self.data[-1]['Close']:
                            self.chart_tool.buy(self.symbol, 0.1, tp, 100)
                        else:
                            self.chart_tool.sell(self.symbol, 0.1, tp, 100)

        if self.wave5_enable:
            if len(In_impulse_prediction_list_w5[0]['X1']) != 0:
                if self.data[In_impulse_prediction_list_w5[0]['X1'][-1]]['Time'] > self.last_prediction_w5_time:
                    self.last_prediction_w5_index += 1
                    self.last_prediction_w5_time = self.data[In_impulse_prediction_list_w5[0]['X1'][-1]]['Time']
                    tp_list = []
                    for j in range(4):

                        #start_times = [self.data[In_impulse_prediction_list_w4[0]['X1'][-1]]['Time']]
                        start_times = [candle['Time']]
                        end_times = [candle['Time'] + (In_impulse_prediction_list_w5[0]['X2'][-1] -In_impulse_prediction_list_w5[0]['X1'][-1]) \
                                     * min(self.data[-1]['Time'] - self.data[-2]['Time'], self.data[-2]['Time'] - self.data[-3]['Time'])]
                        start_prices = In_impulse_prediction_list_w5[0]['Y1'][j][-1]
                        end_prices = In_impulse_prediction_list_w5[0]['Y1'][j][-1]

                        tp_list += start_prices


                        names = [f"In_Prediction_w5{j}-{self.last_prediction_w5_index}-{i}" for i in range(len(start_prices))]
                        start_times = start_times*len(start_prices)
                        end_times = end_times * len(start_prices)
                        if (start_times != []):
                            if (j == 0):
                                self.chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=self.color2,
                                                      style=self.chart_tool.EnumStyle.DashDot, width=2)
                            # pass
                            else:
                                self.chart_tool.trend_line(names, start_times, start_prices,
                                                          end_times,end_prices, color=self.color1,
                                                          style=self.chart_tool.EnumStyle.DashDot, width=2)
                                self.chart_tool.v_line([f"{names[-1]}_1"], times=[start_times[0]],
                                                  style=self.chart_tool.EnumStyle.DashDot)
                                self.chart_tool.v_line([f"{names[-1]}_2"], times=[end_times[0]],
                                                  style=self.chart_tool.EnumStyle.DashDot, color=self.color3)

        if self.post_prediction_enable:
            color = "200,255,0"
            if len(post_prediction_list[0]['X1']) != 0:
                if self.data[post_prediction_list[0]['X1'][-1]]['Time'] > self.last_post_prediction_time:
                    self.last_post_prediction_index += 1
                    self.last_post_prediction_time = self.data[post_prediction_list[0]['X1'][-1]]['Time']
                    for j in range(3):
                        start_prices = post_prediction_list[0]['Y'+str(j+1)]
                        end_prices = post_prediction_list[0]['Y'+str(j+1)]
                        names = [f"Post_Prediction{j}-{self.last_post_prediction_index}-{i}" for i in range(len(start_prices))]
                        start_times = [candle['Time']]*len(start_prices)
                        end_times = ([candle['Time'] + (post_prediction_list[0]['X2'][-1] -post_prediction_list[0]['X1'][-1]) \
                                            * min(self.data[-1]['Time'] - self.data[-2]['Time'], self.data[-2]['Time'] - self.data[-3]['Time'])])* len(start_prices)
                        # start_times = self.result_final['Post_Pr0']['Start_time']
                        # end_times = self.result_final['Post_Pr0']['End_time']
                        
                        self.chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=color,
                                            style=self.chart_tool.EnumStyle.Dot)
    
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

    def get_statistics(self, index_list, statistic_window):
        results = get_bullish_bearish_ratio(self.data, index_list, statistic_window)
        self.bullish_ratio_min, self.bullish_ratio_max, self.bullish_ratio_mean = get_min_max_mean(
            [result['BullishRatio'] for result in results])
        self.bearish_ratio_min, self.bearish_ratio_max, self.bearish_ratio_mean = get_min_max_mean(
            [result['BearishRatio'] for result in results])
        self.first_bullish_cnt, self.first_bearish_cnt = 0, 0
        for result in results:
            if result['FirstIncome'] == "Bull":
                self.first_bullish_cnt += 1
            else:
                self.first_bearish_cnt += 1

    def draw_statistics(self):
        self.chart_tool.rectangle_label([f"RectLabel {self.label}"], [self.rect_x + self.rect_width], [self.rect_y],
                                        [self.rect_width], [self.rect_height],
                                        back_color=self.rect_color, color="200,199,199",
                                        border=self.chart_tool.EnumBorder.Sunken,
                                        corner=self.chart_tool.EnumBaseCorner.RightUpper)
        division = 10
        names, x, y, texts = [f"NameLabel {self.label}"], [self.rect_x + (self.rect_width // 2)], [
            self.rect_y + 0.5 * (self.rect_height // division)], [self.label]
        self.add_label(f"BullishRatioMean {self.label}", self.rect_x + (self.rect_width // 2),
                       self.rect_y + 2.5 * (self.rect_height // division),
                       f"Bullish Ratio Mean = {abs(round(self.bullish_ratio_mean, 3))} %", names, x, y, texts)
        self.add_label(f"BearishRatioMean {self.label}", self.rect_x + (self.rect_width // 2),
                       self.rect_y + 4.5 * (self.rect_height // division),
                       f"Bearish Ratio Mean = {abs(round(self.bearish_ratio_mean, 3))} %", names, x, y, texts)
        self.add_label(f"BullishFirstIncome {self.label}", self.rect_x + (self.rect_width // 2),
                       self.rect_y + 6.5 * (self.rect_height // division),
                       f"Bullish First Income = {self.first_bullish_cnt}", names, x, y, texts)
        self.add_label(f"BearishFirstIncome {self.label}", self.rect_x + (self.rect_width // 2),
                       self.rect_y + 8.5 * (self.rect_height // division),
                       f"Bearish First Income = {self.first_bearish_cnt}", names, x, y, texts)

        self.chart_tool.label(names, x, y, texts, corner=self.chart_tool.EnumBaseCorner.RightUpper,
                              anchor=self.chart_tool.EnumAnchor.Top, font="Times New Roman", font_size=12)

    def add_label(self, name, x, y, text, name_list, x_list, y_list, text_list):
        name_list.append(name)
        x_list.append(x)
        y_list.append(y)
        text_list.append(text)


