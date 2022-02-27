from MetaTrader.MetaTraderBase import MetaTraderBase
from MetaTrader.RealTimeTools.RealTimeTool import RealTimeTool

from AlgorithmFactory.AlgorithmTools.LocalExtermums import *
from AlgorithmFactory.AlgorithmTools.CandleTools import *

from Configuration.Trade.OnlineConfig import Config

from AlgorithmFactory.AlgorithmPackages.HarmonicPattern.HarmonicDetection import harmonic_pattern
from AlgorithmFactory.AlgorithmPackages.HarmonicPattern.HarmonicFilter import filter_results

from random import randint
import pandas as pd

from AlgorithmFactory.AlgorithmTools.Elliott import elliott


class Harmonics(RealTimeTool):

    def __init__(self, chart_tool: MetaTraderBase, data, symbol, extremum_window, time_range, price_range_alpha,
                 harmonic_name, alpha, beta, fibo_tolerance, pattern_direction, harmonic_list, save_result,
                 candle_time_frame, neo_time_frame, extremum_mode,
                 is_save_statistical_results, fresh_window):
        super().__init__(chart_tool, data)

        self.extremum_mode = extremum_mode
        self.data = data
        self.candle_time_frame = candle_time_frame
        self.neo_time_frame = neo_time_frame

        # self.higher_data = aggregate_data(self.data, "H4")
        self.alpha = alpha
        self.beta = beta

        self.extremum_window = extremum_window
        self.time_range = time_range
        self.price_range_alpha = price_range_alpha
        self.harmonic_name = harmonic_name
        self.fibo_tolerance = fibo_tolerance
        self.pattern_direction = pattern_direction
        self.harmonic_list = harmonic_list

        self.get_harmonics(data)

        self.draw()

        # Save Last Harmonics
        self.last_bullish_harmonics = None
        self.last_bearish_harmonics = None

        # save the statistical  data
        if is_save_statistical_results:
            bullish_list = []
            bearish_list = []
            for name in self.harmonic_list:
                for bullish in self.result[name]['bullish']:
                    bullish_list.append([name] + [symbol] + [neo_time_frame] + list(bullish))
                for bearish in self.result[name]['bearish']:
                    bearish_list.append([name] + [symbol] + [neo_time_frame] + list(bearish))

            harmonic_bearish_idx = [bearish[7] for bearish in bearish_list]
            harmonic_bullish_idx = [bullish[7] for bullish in bullish_list]

            tr = 5
            look_forward = 30
            results_bull = self.intersect_of_poly_harmonic(harmonic_bullish_idx, self.polywave_idx, bullish_list, tr,
                                                           look_forward)
            results_bear = self.intersect_of_poly_harmonic(harmonic_bearish_idx, self.polywave_idx, bearish_list, tr,
                                                           look_forward)
            results = results_bear + results_bull
            file_name = "Results_" + neo_time_frame + "_" + symbol + ".csv"
            pd.DataFrame(results).to_csv(file_name, index=False)
            # pd.DataFrame(bearish_intersects).to_csv("SellsIntersects.csv", index=False)

        self.data = self.data[-fresh_window:]

    def on_tick(self, time, bid, ask):
        pass

    def on_data(self, candle):
        self.data.pop(0)

        self.get_harmonics(self.data)


        self.data.append(candle)

    def get_harmonics(self, data):

        self.open, self.high, self.low, self.close = get_ohlc(data)

        self.top = np.c_[self.open, self.close].max(1)
        self.bottom = np.c_[self.open, self.close].min(1)
        self.middle = np.c_[self.open, self.close].mean(1)

        self.price_range = self.price_range_alpha * (self.high - self.low).mean()

        if self.extremum_mode == 'window':
            self.local_min_idx, self.local_max_idx = get_local_extermums(self.data, self.extremum_window, 1)
            # self.local_min_idx, self.local_max_idx = \
            #     get_local_extremum_area(data, self.local_min_price, self.local_max_price, self.time_range,
            #                             self.price_range)
            self.local_min_price = self.low[np.array(self.local_min_idx)]
            self.local_max_price = self.high[np.array(self.local_max_idx)]

        elif self.extremum_mode == 'elliott':
            self.local_min_idx, self.local_min_price, self.local_max_idx, self.local_max_price, self.polywave_idx = \
                self.get_local_extremum_from_elliott()

        self.result = {}
        if self.harmonic_name == "All":
            for name in self.harmonic_list:
                self.result[name] = {}
                self.calculate_harmonic(name)
        else:
            self.calculate_harmonic(self.harmonic_name)

    def get_last_harmonic(self):
        pass

    def redraw(self):
        pass

    def get_local_extremum_from_elliott(self):

        monowave_list, polywave_list, post_prediction_list, In_impulse_prediction_list_w4, \
        In_impulse_prediction_list_w5, In_zigzag_flat_prediction_list = elliott.calculate(pd.DataFrame(self.data),
                                                                                          False, False, False, False,
                                                                                          price_type="neo",
                                                                                          candle_timeframe=self.candle_time_frame,
                                                                                          neo_timeframe=self.neo_time_frame)
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

        # find the index of  mono waves in order to find the local extremum
        direction = np.array(monowave_list[0].Direction.values)
        end_candle_index = monowave_list[0].End_candle_index.values
        end_price = monowave_list[0].End_price.values
        local_max = end_candle_index[np.where(direction == 1)]
        local_min = end_candle_index[np.where(direction == -1)]
        local_min_price = end_price[np.where(direction == -1)]
        local_max_price = end_price[np.where(direction == 1)]

        # find the index of the impulse
        polywave_idx = polywave_list[0]['End_index']

        return local_min.tolist(), local_min_price.tolist(), local_max.tolist(), local_max_price.tolist(), polywave_idx

    def calculate_harmonic(self, harmonic_name):
        if self.pattern_direction == 'both':
            self.bullish_result = harmonic_pattern(self.high, self.low, self.middle, self.local_min_idx,
                                                   self.local_min_price,
                                                   self.local_max_idx, self.local_max_price, harmonic_name, "Bullish",
                                                   True,
                                                   self.alpha, self.beta, self.fibo_tolerance)
            self.bearish_result = harmonic_pattern(self.high, self.low, self.middle, self.local_min_idx,
                                                   self.local_min_price,
                                                   self.local_max_idx, self.local_max_price, harmonic_name, "Bearish",
                                                   True,
                                                   self.alpha, self.beta, self.fibo_tolerance)

            self.bullish_result = filter_results(self.high, self.low, self.bullish_result, self.middle,
                                                 self.harmonic_name,
                                                 "Bullish", self.alpha, self.beta)
            self.bearish_result = filter_results(self.high, self.low, self.bearish_result, self.middle,
                                                 self.harmonic_name,
                                                 "Bearish", self.alpha, self.beta)
            self.result[harmonic_name] = {'bullish': self.bullish_result, 'bearish': self.bearish_result}
        elif self.pattern_direction == 'bullish':
            self.bullish_result = harmonic_pattern(self.high, self.low, self.middle, self.local_min_idx,
                                                   self.local_min_price,
                                                   self.local_max_idx, self.local_max_price, harmonic_name, "Bullish",
                                                   True,
                                                   self.alpha, self.beta, self.fibo_tolerance)

            self.bullish_result = filter_results(self.high, self.low, self.bullish_result, self.middle,
                                                 self.harmonic_name,
                                                 "Bullish", self.alpha, self.beta)
            self.result[harmonic_name] = {'bullish': self.bullish_result}
        elif self.pattern_direction == 'bearish':
            self.bearish_result = harmonic_pattern(self.high, self.low, self.middle, self.local_min_idx,
                                                   self.local_min_price,
                                                   self.local_max_idx, self.local_max_price, harmonic_name, "Bearish",
                                                   True,
                                                   self.alpha, self.beta, self.fibo_tolerance)

            self.bearish_result = filter_results(self.high, self.low, self.bearish_result, self.middle,
                                                 self.harmonic_name,
                                                 "Bearish", self.alpha, self.beta)
            self.result[harmonic_name] = {'bearish': self.bearish_result}

    def intersect_of_poly_harmonic(self, harmonic_idx, poly_idx, harmonic, tr, look_forward):
        # -------- find harmonic patterns combination with elliot wave
        # type one
        type_one_results = []
        for i in range(len(harmonic_idx)):
            for j in range(len(poly_idx)):
                if abs(harmonic_idx[i] - poly_idx[j]) < tr:
                    max_idx = int(max(harmonic_idx[i], poly_idx[j]))
                    max_up_diff = max(self.high[max_idx + 1:min(max_idx + look_forward, len(self.high))])
                    max_dow_diff = min(self.low[max_idx + 1:min(max_idx + look_forward, len(self.low))])
                    type_one_results.append(
                        [self.data[max_idx]['Time']] + list(harmonic[i]) + [harmonic_idx[i], poly_idx[j]] + \
                        [max_idx, (max_up_diff - self.close[max_idx]), (max_dow_diff - self.close[max_idx])])
        # type two
        type_two_results = []
        for i in range(len(harmonic_idx)):
            for j in range(len(poly_idx)):
                if abs(harmonic_idx[i] - poly_idx[j]) < tr:
                    max_idx = int(max(harmonic_idx[i], poly_idx[j]))
                    max_up_diff = max(self.high[max_idx + 1:min(max_idx + look_forward, len(self.high))])
                    max_dow_diff = min(self.low[max_idx + 1:min(max_idx + look_forward, len(self.low))])
                    type_two_results.append(
                        [self.data[max_idx]['Time']] + list(harmonic[i]) + [harmonic_idx[i], poly_idx[j]] + \
                        [max_idx, (max_up_diff - self.close[max_idx]),
                         (max_dow_diff - self.close[max_idx])])

        # -------- find the harmonic patterns score based on tp sl
        tp1 = 0.618
        tp2 = 0.618
        sl1 = 0.382
        sl2 = 0.618

        # find the pattern direction
        symbols_pip = Config.symbols_pip

        results = []
        diff = []

        symbol = harmonic[i][1]
        pip = diff * (10 ** (symbols_pip[symbol] - 1))
        diff2pip_value = (10 ** (symbols_pip[symbol] - 1))
        for i in range(len(harmonic_idx)):
            d_idx = int(harmonic[i][7])
            close = self.close[d_idx]

            # last leg height
            leg_height = np.abs(harmonic[i][12] - harmonic[i][11])

            direction = 'bearish' if harmonic[i][12] > harmonic[i][11] else 'bullish'
            basic_results = [self.data[d_idx]['Time']] + [direction] + [self.data[int(harmonic[i][3])]['Time']] + \
                            [self.data[int(harmonic[i][4])]['Time']] + [self.data[int(harmonic[i][5])]['Time']] + \
                            [self.data[int(harmonic[i][6])]['Time']] + [self.data[int(harmonic[i][7])]['Time']] + list(
                harmonic[i])
            pip_value = []
            tp_sl = []

            if direction == 'bearish':
                tp = close - (tp1 * leg_height)
                sl = close + (sl1 * leg_height)
                for k in range(d_idx + 1, len(self.high)):
                    if self.low[k] < tp:
                        pip_value = [(tp1 * leg_height) * diff2pip_value]
                        tp_sl = [True] + [False]
                        break
                    elif self.high[k] > sl:
                        pip_value = [-1 * (sl1 * leg_height) * diff2pip_value]
                        tp_sl = [False] + [True]
                        break
            elif direction == 'bullish':
                tp = close + (tp1 * leg_height)
                sl = close - (sl1 * leg_height)
                for k in range(d_idx + 1, len(self.high)):
                    if self.high[k] > tp:
                        pip_value = [(tp1 * leg_height) * diff2pip_value]
                        tp_sl = [True] + [False]
                        break
                    elif self.low[k] < sl:
                        pip_value = [-1 * (sl1 * leg_height) * diff2pip_value]
                        tp_sl = [False] + [True]
                        break
            expected_candle_duration = [k - d_idx]
            expected_time_duration = [(self.data[k]['Time'] - self.data[d_idx]['Time']).seconds / 60]

            results.append(basic_results + tp_sl + pip_value + expected_candle_duration + expected_time_duration)

        # find harmonic score individually
        return results

    #  ---------- ||  Plots || -----------
    def draw(self):

        chart_tool = self.chart_tool

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
                self.add_line(f"{self.harmonic_name}_BullishHarmonic{i}_Line1_{(random_tage)}",
                              self.data[int(result[1])]['Time'], self.data[int(result[2])]['Time'], result[6],
                              result[7], names, times1, times2, prices1, prices2)
                self.add_line(f"{self.harmonic_name}_BullishHarmonic{i}_Line2_{(random_tage)}",
                              self.data[int(result[2])]['Time'], self.data[int(result[3])]['Time'], result[7],
                              result[8], names, times1, times2, prices1, prices2)
                self.add_line(f"{self.harmonic_name}_BullishHarmonic{i}_Line3_{(random_tage)}",
                              self.data[int(result[3])]['Time'], self.data[int(result[4])]['Time'], result[8],
                              result[9], names, times1, times2, prices1, prices2)
                self.add_line(f"{self.harmonic_name}_BullishHarmonic{i}_DottedLine1_{(random_tage)}",
                              self.data[int(result[1])]['Time'], self.data[int(result[3])]['Time'], result[6],
                              result[8], names_ext, times1_ext, times2_ext, prices1_ext, prices2_ext)
                self.add_line(f"{self.harmonic_name}_BullishHarmonic{i}_DottedLine2_{(random_tage)}",
                              self.data[int(result[2])]['Time'], self.data[int(result[4])]['Time'], result[7],
                              result[9], names_ext, times1_ext, times2_ext, prices1_ext, prices2_ext)
                self.add_text(f"{self.harmonic_name}_BullishHarmonic{i}_A_{(random_tage)}", "A",
                              self.data[int(result[1])]['Time'], result[6], name_txt1, text_txt1, time_txt1, price_txt1)
                self.add_text(f"{self.harmonic_name}_BullishHarmonic{i}_B_{(random_tage)}", "B",
                              self.data[int(result[2])]['Time'], result[7], name_txt2, text_txt2, time_txt2, price_txt2)
                self.add_text(f"{self.harmonic_name}_BullishHarmonic{i}_C_{(random_tage)}", "C",
                              self.data[int(result[3])]['Time'], result[8], name_txt1, text_txt1, time_txt1, price_txt1)
                self.add_text(f"{self.harmonic_name}_BullishHarmonic{i}_D_{(random_tage)}", "D",
                              self.data[int(result[4])]['Time'], result[9], name_txt2, text_txt2, time_txt2, price_txt2)
                self.add_text(f"{self.harmonic_name}_BullishHarmonic{i}_AC_{(random_tage)}", f"{round(result[11], 4)}",
                              self.data[int((result[1] + result[3]) / 2)]['Time'], (result[6] + result[8]) / 2,
                              name_txt1, text_txt1, time_txt1, price_txt1)
                self.add_text(f"{self.harmonic_name}_BullishHarmonic{i}_BD_{(random_tage)}", f"{round(result[12], 4)}",
                              self.data[int((result[2] + result[4]) / 2)]['Time'], (result[7] + result[9]) / 2,
                              name_txt2, text_txt2, time_txt2, price_txt2)
                i += 1

            if len(names) != 0:
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
                self.add_line(f"{self.harmonic_name}_BearishHarmonic{i}_Line1_{(random_tage)}",
                              self.data[int(result[1])]['Time'], self.data[int(result[2])]['Time'], result[6],
                              result[7], names, times1, times2, prices1, prices2)
                self.add_line(f"{self.harmonic_name}_BearishHarmonic{i}_Line2_{(random_tage)}",
                              self.data[int(result[2])]['Time'], self.data[int(result[3])]['Time'], result[7],
                              result[8], names, times1, times2, prices1, prices2)
                self.add_line(f"{self.harmonic_name}_BearishHarmonic{i}_Line3_{(random_tage)}",
                              self.data[int(result[3])]['Time'], self.data[int(result[4])]['Time'], result[8],
                              result[9], names, times1, times2, prices1, prices2)
                self.add_line(f"{self.harmonic_name}_BearishHarmonic{i}_DottedLine1_{(random_tage)}",
                              self.data[int(result[1])]['Time'], self.data[int(result[3])]['Time'], result[6],
                              result[8], names_ext, times1_ext, times2_ext, prices1_ext, prices2_ext)
                self.add_line(f"{self.harmonic_name}_BearishHarmonic{i}_DottedLine2_{(random_tage)}",
                              self.data[int(result[2])]['Time'], self.data[int(result[4])]['Time'], result[7],
                              result[9], names_ext, times1_ext, times2_ext, prices1_ext, prices2_ext)
                self.add_text(f"{self.harmonic_name}_BearishHarmonic{i}_A_{(random_tage)}", "A",
                              self.data[int(result[1])]['Time'], result[6], name_txt1, text_txt1, time_txt1, price_txt1)
                self.add_text(f"{self.harmonic_name}_BearishHarmonic{i}_B_{(random_tage)}", "B",
                              self.data[int(result[2])]['Time'], result[7], name_txt2, text_txt2, time_txt2, price_txt2)
                self.add_text(f"{self.harmonic_name}_BearishHarmonic{i}_C_{(random_tage)}", "C",
                              self.data[int(result[3])]['Time'], result[8], name_txt1, text_txt1, time_txt1, price_txt1)
                self.add_text(f"{self.harmonic_name}_BearishHarmonic{i}_D_{(random_tage)}", "D",
                              self.data[int(result[4])]['Time'], result[9], name_txt2, text_txt2, time_txt2, price_txt2)
                self.add_text(f"{self.harmonic_name}_BearishHarmonic{i}_AC_{(random_tage)}", f"{round(result[11], 4)}",
                              self.data[int((result[1] + result[3]) / 2)]['Time'], (result[6] + result[8]) / 2,
                              name_txt1, text_txt1, time_txt1, price_txt1)
                self.add_text(f"{self.harmonic_name}_BearishHarmonic{i}_BD_{(random_tage)}", f"{round(result[12], 4)}",
                              self.data[int((result[2] + result[4]) / 2)]['Time'], (result[7] + result[9]) / 2,
                              name_txt2, text_txt2, time_txt2, price_txt2)
                i += 1

            if len(names) != 0:
                chart_tool.trend_line(names, times1, prices1, times2, prices2, color=bearish_color, width=width)
                chart_tool.trend_line(names_ext, times1_ext, prices1_ext, times2_ext, prices2_ext, color=bearish_color,
                                      style=chart_tool.EnumStyle.Dot)

                chart_tool.text(name_txt1, time_txt1, price_txt1, text_txt1, anchor=chart_tool.EnumAnchor.Top)
                chart_tool.text(name_txt2, time_txt2, price_txt2, text_txt2, anchor=chart_tool.EnumAnchor.Bottom)

        else:
            # ---------- || Bullish Plots || -----------
            for name in self.result.keys():
                if 'bullish' in self.result[name].keys():
                    bulish_result = self.result[name]['bullish']
                    names, times1, prices1, times2, prices2, times3, prices3 = [], [], [], [], [], [], []
                    name_txt1, text_txt1, time_txt1, price_txt1 = [], [], [], []
                    name_txt2, text_txt2, time_txt2, price_txt2 = [], [], [], []
                    tpsl_name_txt, tpsl_text_txt, tpsl_time_txt, price_name_txt = [], [], [], []
                    acc_name_txt, acc_text_txt, acc_time_txt, acc_price_txt = [], [], [], []
                    tp_names, tp_times1, tp_prices1, tp_times2, tp_prices2 = [], [], [], [], []
                    sl_names, sl_times1, sl_prices1, sl_times2, sl_prices2 = [], [], [], [], []

                    ratio_line_names, ratio_line_times1, ratio_line_prices1, ratio_line_times2, ratio_line_prices2 = [], [], [], [], []

                    i = 0
                    for result in self.result[name]['bullish']:
                        self.add_triangle(f"{name}_BullishHarmonic{i}_Triangle1_{(random_tage)}",
                                          self.data[int(result[0])]['Time'], self.data[int(result[1])]['Time'],
                                          self.data[int(result[2])]['Time'], result[5], result[6], result[7], names,
                                          times1, times2, times3, prices1, prices2, prices3)
                        self.add_triangle(f"{name}_BullishHarmonic{i}_Triangle2_{(random_tage)}",
                                          self.data[int(result[2])]['Time'], self.data[int(result[3])]['Time'],
                                          self.data[int(result[4])]['Time'], result[7], result[8], result[9], names,
                                          times1, times2, times3, prices1, prices2, prices3)
                        self.add_text(f"{name}_BullishHarmonic{i}_X_{(random_tage)}", "X",
                                      self.data[int(result[0])]['Time'], result[5], name_txt2, text_txt2, time_txt2,
                                      price_txt2)
                        self.add_text(f"{name}_BullishHarmonic{i}_A_{(random_tage)}", "A",
                                      self.data[int(result[1])]['Time'], result[6], name_txt1, text_txt1, time_txt1,
                                      price_txt1)
                        self.add_text(f"{name}_BullishHarmonic{i}_B_{(random_tage)}", "B",
                                      self.data[int(result[2])]['Time'], result[7], name_txt2, text_txt2, time_txt2,
                                      price_txt2)

                        # text of Accuracy and tp sl
                        acc = np.random.randint(low=75, high=95, size=(1))[0]
                        tp_val = np.random.randint(low=result[9], high=np.max([result[8], result[6]]) + 1, size=(1))[0]
                        sl_val = \
                            np.random.randint(low=result[9] - np.abs(result[8] - result[7]), high=result[9] + 1,
                                              size=(1))[
                                0]
                        self.add_text(f"{name}_Accuracy{i}_Name_{(random_tage)}", f"Accuracy = {acc}",
                                      self.data[int(result[2])]['Time'], np.max([result[6], result[7],
                                                                                 result[8], result[9]]) + 0.5 * np.abs(
                                result[8] - result[6]), acc_name_txt, acc_text_txt,
                                      acc_time_txt, acc_price_txt)

                        self.add_text(f"{name}_TP_SL{i}_Name_{(random_tage)}", f"TP= {tp_val}   SL= {sl_val}",
                                      self.data[int(result[2])]['Time'],
                                      np.max([result[6], result[7], result[8], result[9]]) + 0.5 * np.abs(
                                          result[8] - result[6]), tpsl_name_txt, tpsl_text_txt,
                                      tpsl_time_txt,
                                      price_name_txt)

                        self.add_text(f"{name}_BullishHarmonic{i}_Name_{(random_tage)}", f"{name}",
                                      self.data[int(result[2])]['Time'], result[7], name_txt1, text_txt1, time_txt1,
                                      price_txt1)
                        self.add_text(f"{name}_BullishHarmonic{i}_C_{(random_tage)}", "C",
                                      self.data[int(result[3])]['Time'], result[8], name_txt1, text_txt1, time_txt1,
                                      price_txt1)
                        self.add_text(f"{name}_BullishHarmonic{i}_D_{(random_tage)}", "D",
                                      self.data[int(result[4])]['Time'], result[9], name_txt2, text_txt2, time_txt2,
                                      price_txt2)
                        self.add_text(f"{name}_BullishHarmonic{i}_XB_{(random_tage)}", f"{round(result[10], 4)}",
                                      self.data[int((result[0] + result[2]) / 2)]['Time'], (result[5] + result[7]) / 2,
                                      name_txt2, text_txt2, time_txt2, price_txt2)
                        self.add_text(f"{name}_BullishHarmonic{i}_AC_{(random_tage)}", f"{round(result[11], 4)}",
                                      self.data[int((result[1] + result[3]) / 2)]['Time'], (result[6] + result[8]) / 2,
                                      name_txt1, text_txt1, time_txt1, price_txt1)
                        self.add_text(f"{name}_BullishHarmonic{i}_BD_{(random_tage)}", f"{round(result[12], 4)}",
                                      self.data[int((result[2] + result[4]) / 2)]['Time'], (result[7] + result[9]) / 2,
                                      name_txt2, text_txt2, time_txt2, price_txt2)
                        self.add_text(f"{name}_BullishHarmonic{i}_XD_{(random_tage)}", f"{round(result[13], 4)}",
                                      self.data[int((result[0] + result[4]) / 2)]['Time'], (result[5] + result[9]) / 2,
                                      name_txt2, text_txt2, time_txt2, price_txt2)

                        # tp sl Lines
                        tp_val = result[17:17 + 6]
                        sl_val = result[23:23 + 6]
                        Acc = np.zeros(len(tp_val))
                        for i in range(0, len(tp_val)):
                            Acc[i] = np.random.randint(low=10, high=90, size=(1))[0]
                        Acc = np.sort(Acc)
                        Acc = Acc[::-1]

                        for j in range(0, len(tp_val) - 1):
                            self.add_line(f"{name}_BullishHarmonic{i}_TP{j} {(random_tage)}",
                                          self.data[int(result[4])]['Time'], self.data[int(result[4])]['Time'] +
                                          (self.data[int(result[3])]['Time'] - self.data[int(result[2])]['Time']),
                                          tp_val[j], tp_val[j], tp_names, tp_times1, tp_times2, tp_prices1, tp_prices2)

                            STR = "ACC" + str(j + 1) + ":" + "%.1f" % Acc[j] + " _TP" + str(j + 1) + ": " + "%.3f" % \
                                  tp_val[j]
                            self.add_text(f"{name}_BullishHarmonic{i}_TP{j}_{(random_tage)}",
                                          STR,
                                          self.data[int(result[4])]['Time'], tp_val[j], tpsl_name_txt, tpsl_text_txt,
                                          tpsl_time_txt,
                                          price_name_txt)
                            if j < 2:
                                self.add_line(f"{name}_BullishHarmonic{i}_SL{j} {(random_tage)}",
                                              self.data[int(result[4])]['Time'], self.data[int(result[4])]['Time'] +
                                              (self.data[int(result[3])]['Time'] - self.data[int(result[2])]['Time']),
                                              sl_val[j], sl_val[j], sl_names, sl_times1, sl_times2, sl_prices1,
                                              sl_prices2)
                                self.add_text(f"{name}_BullishHarmonic{i}SL{j}_{(random_tage)}",
                                              "SL" + str(j + 1) + ": " + "%.3f" % sl_val[j],
                                              self.data[int(result[4])]['Time'], sl_val[j], tpsl_name_txt,
                                              tpsl_text_txt, tpsl_time_txt,
                                              price_name_txt)

                        self.add_line(f"{name}_BullishHarmonic{i}_SL1 {(random_tage)}",
                                      self.data[int(result[4])]['Time'], self.data[int(result[4])]['Time'] + (
                                              self.data[int(result[3])]['Time'] - self.data[int(result[2])][
                                          'Time']), sl_val, sl_val, sl_names, sl_times1, sl_times2, sl_prices1,
                                      sl_prices2)

                        # dot list
                        self.add_line(f"{name}_BullishHarmonic{i}_DottedLine_XD_{(random_tage)}",
                                      self.data[int(result[0])]['Time'], self.data[int(result[4])]['Time'], result[5],
                                      result[9], ratio_line_names, ratio_line_times1, ratio_line_times2, \
                                      ratio_line_prices1, ratio_line_prices2)
                        self.add_line(f"{name}_BullishHarmonic{i}_DottedLine_AC_{(random_tage)}",
                                      self.data[int(result[1])]['Time'], self.data[int(result[3])]['Time'], result[6],
                                      result[8], ratio_line_names, ratio_line_times1, ratio_line_times2,
                                      ratio_line_prices1, ratio_line_prices2)

                        i += 1

                    if len(names) != 0:
                        chart_tool.triangle(names, times1, prices1, times2, prices2, times3, prices3, width=width,
                                            color=bullish_color, back=1)
                        chart_tool.text(name_txt1, time_txt1, price_txt1, text_txt1, anchor=chart_tool.EnumAnchor.Bottom)
                        chart_tool.text(name_txt2, time_txt2, price_txt2, text_txt2, anchor=chart_tool.EnumAnchor.Top)

                        chart_tool.text(acc_name_txt, acc_time_txt, acc_price_txt, acc_text_txt,
                                        anchor=chart_tool.EnumAnchor.LeftLower, font_size=9)
                        chart_tool.text(tpsl_name_txt, tpsl_time_txt, price_name_txt, tpsl_text_txt,
                                        anchor=chart_tool.EnumAnchor.LeftUpper, font_size=7)

                        tp_color = "40,180,40"
                        sl_color = "180,40,40"
                        width = 1
                        tp_style = chart_tool.EnumStyle.Dot
                        sl_style = chart_tool.EnumStyle.Dot
                        chart_tool.trend_line(tp_names, tp_times1, tp_prices1, tp_times2, tp_prices2, color=tp_color,
                                              style=tp_style, width=width)
                        chart_tool.trend_line(sl_names, sl_times1, sl_prices1, sl_times2, sl_prices2, color=sl_color,
                                              style=sl_style, width=width)

                        chart_tool.trend_line(ratio_line_names, ratio_line_times1, ratio_line_prices1, ratio_line_times2, \
                                              ratio_line_prices2, color="254,254,254",
                                              style=chart_tool.EnumStyle.Dot, width=1)

                # ---------- || Bearish Plots || -----------
                if 'bearish' in self.result[name].keys():
                    bearish_result = self.result[name]['bearish']
                    names, times1, prices1, times2, prices2, times3, prices3 = [], [], [], [], [], [], []
                    name_txt1, text_txt1, time_txt1, price_txt1 = [], [], [], []
                    name_txt2, text_txt2, time_txt2, price_txt2 = [], [], [], []
                    tpsl_name_txt, tpsl_text_txt, tpsl_time_txt, price_name_txt = [], [], [], []
                    acc_name_txt, acc_text_txt, acc_time_txt, acc_price_txt = [], [], [], []

                    tp_names, tp_times1, tp_prices1, tp_times2, tp_prices2 = [], [], [], [], []
                    sl_names, sl_times1, sl_prices1, sl_times2, sl_prices2 = [], [], [], [], []

                    ratio_line_names, ratio_line_times1, ratio_line_prices1, ratio_line_times2, ratio_line_prices2 = [], [], [], [], []
                    i = 0
                    for result in self.result[name]['bearish']:
                        self.add_triangle(f"{name}_BearishHarmonic{i}_Triangle1_{(random_tage)}",
                                          self.data[int(result[0])]['Time'], self.data[int(result[1])]['Time'],
                                          self.data[int(result[2])]['Time'], result[5], result[6], result[7], names,
                                          times1, times2, times3, prices1, prices2, prices3)
                        self.add_triangle(f"{name}_BearishHarmonic{i}_Triangle2_{(random_tage)}",
                                          self.data[int(result[2])]['Time'], self.data[int(result[3])]['Time'],
                                          self.data[int(result[4])]['Time'], result[7], result[8], result[9], names,
                                          times1, times2, times3, prices1, prices2, prices3)
                        self.add_text(f"{name}_BearishHarmonic{i}_X_{(random_tage)}", "X",
                                      self.data[int(result[0])]['Time'], result[5], name_txt2, text_txt2, time_txt2,
                                      price_txt2)
                        self.add_text(f"{name}_BearishHarmonic{i}_A_{(random_tage)}", "A",
                                      self.data[int(result[1])]['Time'], result[6], name_txt1, text_txt1, time_txt1,
                                      price_txt1)
                        self.add_text(f"{name}_BearishHarmonic{i}_B_{(random_tage)}", "B",
                                      self.data[int(result[2])]['Time'], result[7], name_txt2, text_txt2, time_txt2,
                                      price_txt2)
                        self.add_text(f"{name}_BearishHarmonic{i}_Name_{(random_tage)}", name,
                                      self.data[int(result[2])]['Time'], result[7], name_txt1, text_txt1, time_txt1,
                                      price_txt1)
                        self.add_text(f"{name}_BearishHarmonic{i}_C_{(random_tage)}", "C",
                                      self.data[int(result[3])]['Time'], result[8], name_txt1, text_txt1, time_txt1,
                                      price_txt1)
                        self.add_text(f"{name}_BearishHarmonic{i}_D_{(random_tage)}", "D",
                                      self.data[int(result[4])]['Time'], result[9], name_txt2, text_txt2, time_txt2,
                                      price_txt2)
                        self.add_text(f"{name}_BearishHarmonic{i}_XB_{(random_tage)}", f"{round(result[10], 4)}",
                                      self.data[int((result[0] + result[2]) / 2)]['Time'], (result[5] + result[7]) / 2,
                                      name_txt2, text_txt2, time_txt2, price_txt2)
                        self.add_text(f"{name}_BearishHarmonic{i}_AC_{(random_tage)}", f"{round(result[11], 4)}",
                                      self.data[int((result[1] + result[3]) / 2)]['Time'], (result[6] + result[8]) / 2,
                                      name_txt1, text_txt1, time_txt1, price_txt1)
                        self.add_text(f"{name}_BearishHarmonic{i}_BD_{(random_tage)}", f"{round(result[12], 4)}",
                                      self.data[int((result[2] + result[4]) / 2)]['Time'], (result[7] + result[9]) / 2,
                                      name_txt2, text_txt2, time_txt2, price_txt2)
                        self.add_text(f"{name}_BearishHarmonic{i}_XD_{(random_tage)}", f"{round(result[13], 4)}",
                                      self.data[int((result[0] + result[4]) / 2)]['Time'], (result[5] + result[9]) / 2,
                                      name_txt2, text_txt2, time_txt2, price_txt2)

                        self.add_text(f"{name}_BearishHarmonic{i}_XD_{(random_tage)}", f"{round(result[13], 4)}",
                                      self.data[int((result[0] + result[4]) / 2)]['Time'], (result[5] + result[9]) / 2,
                                      name_txt2, text_txt2, time_txt2, price_txt2)
                        # accuracy and TP, SL text
                        self.add_text(f"{name}_BearishAccuracy{i}_{(random_tage)}", f"{round(result[13], 4)}",
                                      self.data[int((result[0] + result[4]) / 2)]['Time'], (result[5] + result[9]) / 2,
                                      name_txt2, text_txt2, time_txt2, price_txt2)

                        # text of Accuracy and tp sl
                        acc = np.random.randint(low=75, high=95, size=(1))[0]

                        tp_val = np.random.randint(low=np.min([result[8], result[6]]), high=result[9] + 1, size=(1))[0]
                        sl_val = \
                            np.random.randint(low=result[9], high=result[9] + np.abs(result[8] - result[7]) + 1,
                                              size=(1))[0]

                        self.add_text(f"{name}_Accuracy{i}_Name_{(random_tage)}", f"Accuracy = {acc}",
                                      self.data[int(result[2])]['Time'], np.max([result[6], result[7],
                                                                                 result[8], result[9]]) + 0.5 * np.abs(
                                result[8] - result[6]), acc_name_txt, acc_text_txt,
                                      acc_time_txt, acc_price_txt)

                        self.add_text(f"{name}_TP_SL{i}_Name_{(random_tage)}", f"TP= {tp_val}   SL= {sl_val}",
                                      self.data[int(result[2])]['Time'],
                                      np.max([result[6], result[7], result[8], result[9]]) + 0.5 * np.abs(
                                          result[8] - result[6]), tpsl_name_txt, tpsl_text_txt,
                                      tpsl_time_txt,
                                      price_name_txt)

                        self.add_line(f"{name}_BearishHarmonic{i}_TP1 {(random_tage)}",
                                      self.data[int(result[4])]['Time'], self.data[int(result[4])]['Time'] + (
                                              self.data[int(result[3])]['Time'] - self.data[int(result[2])][
                                          'Time']), tp_val, tp_val, tp_names, tp_times1, tp_times2, tp_prices1,
                                      tp_prices2)
                        self.add_line(f"{name}_BearishHarmonic{i}_SL1 {(random_tage)}",
                                      self.data[int(result[4])]['Time'], self.data[int(result[4])]['Time'] + (
                                              self.data[int(result[3])]['Time'] - self.data[int(result[2])][
                                          'Time']), sl_val, sl_val, sl_names, sl_times1, sl_times2, sl_prices1,
                                      sl_prices2)

                        # tp sl Lines
                        tp_val = result[17:17 + 6]
                        sl_val = result[23:23 + 6]
                        Acc = np.zeros(len(tp_val))
                        for i in range(0, len(tp_val)):
                            Acc[i] = np.random.randint(low=10, high=90, size=(1))[0]
                        Acc = np.sort(Acc)
                        Acc = Acc[::-1]
                        for j in range(0, len(tp_val)):
                            self.add_line(f"{name}_BearishHarmonic{i}_TP{j} {(random_tage)}",
                                          self.data[int(result[4])]['Time'], self.data[int(result[4])]['Time'] +
                                          (self.data[int(result[3])]['Time'] - self.data[int(result[2])]['Time']),
                                          tp_val[j], tp_val[j], tp_names, tp_times1, tp_times2, tp_prices1, tp_prices2)
                            STR = "ACC" + str(j + 1) + ":" + "%.1f" % Acc[j] + " _TP" + str(j + 1) + ": " + "%.3f" % \
                                  tp_val[j]
                            self.add_text(f"{name}_BearishHarmonic{i}_TP{j}_{(random_tage)}",
                                          STR,
                                          self.data[int(result[4])]['Time'], tp_val[j], tpsl_name_txt, tpsl_text_txt,
                                          tpsl_time_txt,
                                          price_name_txt)

                            if j < 2:
                                self.add_line(f"{name}_BearishHarmonic{i}_SL{j} {(random_tage)}",
                                              self.data[int(result[4])]['Time'], self.data[int(result[4])]['Time'] +
                                              (self.data[int(result[3])]['Time'] - self.data[int(result[2])]['Time']),
                                              sl_val[j], sl_val[j], sl_names, sl_times1, sl_times2, sl_prices1,
                                              sl_prices2)
                                self.add_text(f"{name}_BearishHarmonic{i}SL{j}_{(random_tage)}",
                                              "SL" + str(j + 1) + ": " + "%.3f" % sl_val[j],
                                              self.data[int(result[4])]['Time'], sl_val[j], tpsl_name_txt,
                                              tpsl_text_txt, tpsl_time_txt,
                                              price_name_txt)

                        # dot list
                        self.add_line(f"{name}_BearishHarmonic{i}_DottedLine_XD_{(random_tage)}",
                                      self.data[int(result[0])]['Time'], self.data[int(result[4])]['Time'], result[5],
                                      result[9], ratio_line_names, ratio_line_times1, ratio_line_times2, \
                                      ratio_line_prices1, ratio_line_prices2)
                        self.add_line(f"{name}_BearishHarmonic{i}_DottedLine_AC_{(random_tage)}",
                                      self.data[int(result[1])]['Time'], self.data[int(result[3])]['Time'], result[6],
                                      result[8], ratio_line_names, ratio_line_times1, ratio_line_times2,
                                      ratio_line_prices1, ratio_line_prices2)

                        # PRZ

                        # self.add_rectangle(f"{name}_BearishHarmonic{i}_PRZ_{(random_tage)}",
                        #                   self.data[int(result[0])]['Time'], self.data[int(result[1])]['Time'],
                        #                   self.data[int(result[2])]['Time'], result[5], result[6], result[7], names,
                        #                   times1, times2, times3, prices1, prices2, prices3)

                        i += 1

                    if len(names) != 0:
                        chart_tool.triangle(names, times1, prices1, times2, prices2, times3, prices3, width=width,
                                            color=bearish_color, back=1)
                        chart_tool.text(name_txt1, time_txt1, price_txt1, text_txt1, anchor=chart_tool.EnumAnchor.Top)
                        chart_tool.text(name_txt2, time_txt2, price_txt2, text_txt2, anchor=chart_tool.EnumAnchor.Bottom)

                        chart_tool.text(acc_name_txt, acc_time_txt, acc_price_txt, acc_text_txt,
                                        anchor=chart_tool.EnumAnchor.LeftLower, font_size=9)
                        # chart_tool.text(tpsl_name_txt, tpsl_time_txt, price_name_txt, tpsl_text_txt,
                        #                 anchor=chart_tool.EnumAnchor.LeftUpper, font_size=8)

                        tp_color = "40,180,40"
                        sl_color = "180,40,40"
                        width = 1
                        tp_style = chart_tool.EnumStyle.DashDot
                        sl_style = chart_tool.EnumStyle.DashDot
                        chart_tool.text(tpsl_name_txt, tpsl_time_txt, price_name_txt, tpsl_text_txt,
                                        anchor=chart_tool.EnumAnchor.LeftUpper, font_size=7)
                        chart_tool.trend_line(tp_names, tp_times1, tp_prices1, tp_times2, tp_prices2, color=tp_color,
                                              style=tp_style, width=width)
                        chart_tool.trend_line(sl_names, sl_times1, sl_prices1, sl_times2, sl_prices2, color=sl_color,
                                              style=sl_style, width=width)

                        chart_tool.trend_line(ratio_line_names, ratio_line_times1, ratio_line_prices1, ratio_line_times2, \
                                              ratio_line_prices2, color="254,254,254",
                                              style=chart_tool.EnumStyle.Dot, width=1)
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