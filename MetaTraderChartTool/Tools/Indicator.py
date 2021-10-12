import numpy as np

from MetaTraderChartTool.BasicChartTools import BasicChartTools
from AlgorithmFactory.AlgorithmTools.LocalExtermums import *
from MetaTraderChartTool.Tools.Tool import Tool
import talib


class Indicator(Tool):

    def _init_(self, data):
        super()._init_(data)

        self.indicator_values = []
        self.line70 = []
        self.line50 = []
        self.line30 = []
        self.open   = []
        self.close  = []
        self.high   = []
        self.low    = []

        # ----------------- || main body of indicator || -----------------
        for i in range(len(self.data)):
            self.open.append(self.data[i]['Open'])
            self.close.append(self.data[i]['Close'])
            self.high.append(self.data[i]['High'])
            self.low.append(self.data[i]['Low'])

        src = self.close
        rsi = talib.RSI(np.array(src), 14)

        # find the overbought/middle section to oversold section
        section = None
        sections = []
        for i in range(len(rsi)):
            if rsi[i] < 30:
                section = 'oversold'
            elif rsi[i] > 70:
                section = 'overbought'
            elif rsi[i] <= 70 and rsi[i] >= 50:
                section = 'middlePlus'
            elif rsi[i] < 50 and rsi[i] >= 30:
                section = 'middleMinus'
            else:
                section = 'None'
            sections.append(section)

        # ------------------------------------------ || find the buy pattern || _______
        self.buy_idx = []
        self.buy_idx_time = []
        self.buy_idx_value = []

        len_kp_tr = 3
        tr_kj_lk = 1.8
        for i in range(len(sections) - 2, -1, -1):
            if sections[i] == 'middleMinus':
                middleMinusIdx = i

                for j in range(middleMinusIdx + 1, len(sections) - 1):
                    if sections[j] == 'oversold' and max(rsi[i + 1:j + 1]) < rsi[i] and min(rsi[i:j]) > rsi[j]:
                        overSoldIdx = j

                        for k in range(overSoldIdx + 1, len(sections) - 1):
                            if sections[k] == 'middleMinus' and rsi[k] < rsi[i] and min(rsi[j + 1:k + 1]) > rsi[j] and \
                                    max(rsi[j:k]) < rsi[k]:
                                middleMinusIdx2 = k

                                for l in range(middleMinusIdx2 + 1, len(sections) - 1):
                                    if sections[l] == 'middleMinus' and rsi[l] < rsi[k] and rsi[l] > rsi[j] and \
                                            (rsi[l] < rsi[l - 1] and rsi[l] < rsi[l + 1]) and max(rsi[k + 1:l + 1]) < \
                                            rsi[k] and \
                                            min(rsi[k:l]) > rsi[l]:
                                        middleMinusIdx3 = l

                                        for p in range(middleMinusIdx3 + 1, len(sections) - 1):
                                            if (sections[p] == 'middleMinus' or sections[p] == 'middlePlus') and rsi[p]\
                                                    > rsi[k] and (((k-j)/(l-k)) >= tr_kj_lk) and min(rsi[l + 1:p + 1]) >\
                                                    rsi[l]:
                                                self.buy_idx.append([i, j, k, l, p])
                                                self.buy_idx_time.append([self.data[i]['Time'], self.data[j]['Time'],
                                                                          self.data[k]['Time'], self.data[l]['Time'],
                                                                          self.data[p]['Time']])
                                                self.buy_idx_value.append([rsi[i], rsi[j], rsi[k], rsi[l], rsi[p]])
                                                break

        # ------------------------------------------ || find the Sell pattern || _______
        self.sell_idx = []
        self.sell_idx_time = []
        self.sell_idx_value = []

        for i in range(len(sections) - 2, -1, -1):
            if sections[i] == 'middlePlus':
                middlePlusIdx = i

                for j in range(middlePlusIdx + 1, len(sections) - 1):
                    if sections[j] == 'overbought' and max(rsi[i:j]) < rsi[j] and min(rsi[i+1:j+1]) > rsi[i]:
                        overboughtIdx = j

                        for k in range(overboughtIdx + 1, len(sections) - 1):
                            if sections[k] == 'middlePlus' and rsi[k] > rsi[i] and max(rsi[j + 1:k + 1]) < rsi[
                                j] and min(rsi[j:k]) > rsi[k]:
                                middlePlusIdx2 = k

                                for l in range(middlePlusIdx2 + 1, len(sections) - 1):
                                    if sections[l] == 'middlePlus' and rsi[l] > rsi[k] and rsi[l] < rsi[j] and \
                                            (rsi[l] > rsi[l - 1] and rsi[l] > rsi[l + 1]) and min(rsi[k + 1:l + 1]) > \
                                            rsi[k] and max(rsi[k:l]) < rsi[l]:
                                        middlePlusIdx3 = l

                                        for p in range(middlePlusIdx3 + 1, len(sections) - 1):
                                            if (sections[p] == 'middleMinus' or sections[p] == 'middlePlus') and \
                                                    rsi[p] < rsi[k] and (((k - j) / (l - k)) >= tr_kj_lk) and \
                                                    max(rsi[l + 1:p + 1]) < rsi[l]:
                                                self.sell_idx.append([i, j, k, l, p])
                                                self.sell_idx_time.append(
                                                    [self.data[i]['Time'], self.data[j]['Time'],
                                                     self.data[k]['Time'], self.data[l]['Time'],
                                                     self.data[p]['Time']])
                                                self.sell_idx_value.append(
                                                    [rsi[i], rsi[j], rsi[k], rsi[l], rsi[p]])
                                                break

        line70 = 70 * np.ones(len(rsi))
        line50 = 50 * np.ones(len(rsi))
        line30 = 30 * np.ones(len(rsi))

        # convert Indicator valuee to the chart val
        Max = np.nanmax(rsi)
        Min = np.nanmin(rsi)
        newMax = np.min(self.low)
        newMin = np.min(self.low) - np.max(np.array(self.high) - np.array(self.low))
        newRSI = (newMax - newMin) / (Max - Min) * (rsi - Max) + newMax

        line70 = (newMax - newMin) / (Max - Min) * (line70 - Max) + newMax
        line50 = (newMax - newMin) / (Max - Min) * (line50 - Max) + newMax
        line30 = (newMax - newMin) / (Max - Min) * (line30 - Max) + newMax

        for i in range(len(self.buy_idx_value)-1):
            self.buy_idx_value[i] = (newMax - newMin) / (Max - Min) * (self.buy_idx_value[i] - Max) + newMax

        for i in range(len(self.sell_idx_value)-1):
            self.sell_idx_value[i] = (newMax - newMin) / (Max - Min) * (self.sell_idx_value[i] - Max) + newMax
        # remove NaN from RSI
        np.where(np.isnan(rsi), np.nanmean(rsi), rsi)

        self.buy_pattern_ = []

        # Build data Time
        for i in range(len(data)):
            self.indicator_values.append((self.data[i]['Time'], newRSI[i]))
            self.line70.append((self.data[i]['Time'], line70[i]))
            self.line50.append((self.data[i]['Time'], line50[i]))
            self.line30.append((self.data[i]['Time'], line30[i]))

    def draw(self, chart_tool: BasicChartTools):

        # ------------------------- || plot the RSI Lines || --------------------
        times1, times2, prices1, prices2, names1 = [], [], [], [], []
        time1_line, time2_line, price_line_30, price_line_30_end, price_line_50, price_line_50_end, price_line_70, \
        price_line_70_end, names2, names3, names4 = [], [], [], [], [], [], [], [], [], [], []
        for i in range(len(self.indicator_values) - 1):
            # Value of RSI
            times1.append(self.indicator_values[i][0])
            times2.append(self.indicator_values[i + 1][0])
            prices1.append(self.indicator_values[i][1])
            prices2.append(self.indicator_values[i + 1][1])
            names1.append(f"IndicatorLine{i}")

            # Value of 30 Line
            price_line_30.append(self.line30[i][1])
            price_line_30_end.append(self.line30[i + 1][1])
            names2.append(f"line30{i}")

            # Value of 50 Line
            price_line_50.append(self.line50[i][1])
            price_line_50_end.append(self.line50[i + 1][1])
            names3.append(f"line50{i}")

            # Value of 70 Line
            price_line_70.append(self.line70[i][1])
            price_line_70_end.append(self.line70[i + 1][1])
            names4.append(f"line70{i}")
        # rsi lines
        chart_tool.trend_line(names1, times1, prices1, times2, prices2, width=3)

        # plot line 30 and 50 and 70
        chart_tool.trend_line(names2, times1, price_line_30, times2, price_line_30_end, color="95,215,0", style=2)
        chart_tool.trend_line(names3, times1, price_line_50, times2, price_line_50_end, color="192,192,192",
                              style=2)
        chart_tool.trend_line(names4, times1, price_line_70, times2, price_line_70_end, color="215,0,95", style=2)
        """"
        # ------------------------- || plot the Buy Patterns || --------------------
        times_patternA1, times_patternA2, times_patternB1, times_patternB2, times_patternC1, times_patternC2, \
        times_patternD1, times_patternD2 = [], [], [], [], [], [], [], []
        prices_patternA1, prices_patternA2, prices_patternB1, prices_patternB2, prices_patternC1, prices_patternC2, \
        prices_patternD1, prices_patternD2,prices_pattern_arrow = [], [], [], [], [], [], [], [], []

        names_patternA, names_patternB, names_patternC, names_patternD,names_pattern_arrow = [], [], [], [], []

        for i in range(len(self.buy_idx) - 1):
            # leg1
            times_patternA1.append(self.buy_idx_time[i][0])
            times_patternA2.append(self.buy_idx_time[i][1])
            prices_patternA1.append(self.buy_idx_value[i][0])
            prices_patternA2.append(self.buy_idx_value[i][1])
            names_patternA.append(f"lineA{i}")

            # leg2
            times_patternB1.append(self.buy_idx_time[i][1])
            times_patternB2.append(self.buy_idx_time[i][2])
            prices_patternB1.append(self.buy_idx_value[i][1])
            prices_patternB2.append(self.buy_idx_value[i][2])
            names_patternB.append(f"lineB{i}")

            # leg3
            times_patternC1.append(self.buy_idx_time[i][2])
            times_patternC2.append(self.buy_idx_time[i][3])
            prices_patternC1.append(self.buy_idx_value[i][2])
            prices_patternC2.append(self.buy_idx_value[i][3])
            names_patternC.append(f"lineC{i}")

            # leg4
            times_patternD1.append(self.buy_idx_time[i][3])
            times_patternD2.append(self.buy_idx_time[i][4])
            prices_patternD1.append(self.buy_idx_value[i][3])
            prices_patternD2.append(self.buy_idx_value[i][4])

            names_patternD.append(f"lineD{i}")

            # name buy arrow
            names_pattern_arrow.append(f"buyArrow{i}")
            prices_pattern_arrow.append(self.data[self.buy_idx[i][-1]]['Open'])

            # pattern
            chart_tool.trend_line(names_patternA, times_patternA1, prices_patternA1,times_patternA2, prices_patternA2, color="135,0,0", style=1,width=2)
            chart_tool.trend_line(names_patternB, times_patternB1, prices_patternB1,times_patternB2, prices_patternB2, color="0,135,0", style=1,width=2)
            chart_tool.trend_line(names_patternC, times_patternC1, prices_patternC1,times_patternC2, prices_patternC2, color="255,0,0", style=1,width=2)
            chart_tool.trend_line(names_patternD, times_patternD1, prices_patternD1,times_patternD2, prices_patternD2, color="0,215,0", style=1,width=2)

            # Arrow Up in the latest index of pattern
            chart_tool.arrow_buy(names_pattern_arrow, times_patternD2, prices_pattern_arrow, color="0,128,0",width=2)
        """
        # ------------------------- || plot the Sell Patterns || --------------------
        times_patternA1, times_patternA2, times_patternB1, times_patternB2, times_patternC1, times_patternC2, \
        times_patternD1, times_patternD2 = [], [], [], [], [], [], [], []
        prices_patternA1, prices_patternA2, prices_patternB1, prices_patternB2, prices_patternC1, prices_patternC2, \
        prices_patternD1, prices_patternD2, prices_pattern_arrow = [], [], [], [], [], [], [], [], []

        names_patternA, names_patternB, names_patternC, names_patternD, names_pattern_arrow = [], [], [], [], []

        for i in range(len(self.sell_idx) - 1):
            # leg1
            times_patternA1.append(self.sell_idx_time[i][0])
            times_patternA2.append(self.sell_idx_time[i][1])
            prices_patternA1.append(self.sell_idx_value[i][0])
            prices_patternA2.append(self.sell_idx_value[i][1])
            names_patternA.append(f"lineA{i}")

            # leg2
            times_patternB1.append(self.sell_idx_time[i][1])
            times_patternB2.append(self.sell_idx_time[i][2])
            prices_patternB1.append(self.sell_idx_value[i][1])
            prices_patternB2.append(self.sell_idx_value[i][2])
            names_patternB.append(f"lineB{i}")

            # leg3
            times_patternC1.append(self.sell_idx_time[i][2])
            times_patternC2.append(self.sell_idx_time[i][3])
            prices_patternC1.append(self.sell_idx_value[i][2])
            prices_patternC2.append(self.sell_idx_value[i][3])
            names_patternC.append(f"lineC{i}")

            # leg4
            times_patternD1.append(self.sell_idx_time[i][3])
            times_patternD2.append(self.sell_idx_time[i][4])
            prices_patternD1.append(self.sell_idx_value[i][3])
            prices_patternD2.append(self.sell_idx_value[i][4])

            names_patternD.append(f"lineD{i}")

            names_pattern_arrow.append(f"sellArrow{i}")
            prices_pattern_arrow.append(self.data[self.sell_idx[i][-1]]['Open'])

            # pattern
            chart_tool.trend_line(names_patternA, times_patternA1, prices_patternA1, times_patternA2, prices_patternA2,
                                  color="135,0,0", style=1, width=2)
            chart_tool.trend_line(names_patternB, times_patternB1, prices_patternB1, times_patternB2, prices_patternB2,
                                  color="0,135,0", style=1, width=2)
            chart_tool.trend_line(names_patternC, times_patternC1, prices_patternC1, times_patternC2, prices_patternC2,
                                  color="255,0,0", style=1, width=2)
            chart_tool.trend_line(names_patternD, times_patternD1, prices_patternD1, times_patternD2, prices_patternD2,
                                  color="0,215,0", style=1, width=2)

            # Arrow Up in the latest index of pattern
            chart_tool.arrow_sell(names_pattern_arrow, times_patternD2, prices_pattern_arrow, color="0,128,0", width=2)