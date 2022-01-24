


import numpy as np
import pandas as pd
import copy
import sys
from tqdm import tqdm

from AlgorithmFactory.AlgorithmTools.Elliott.utility import *
from AlgorithmFactory.AlgorithmTools.Elliott.mw_utils import *


class MonoWave:
    def __init__(self, dataF_price_node):
        self.nodes = dataF_price_node
        self.cols = [
            'MW_start_index', 'MW_end_index', 'Start_candle_index',
            'End_candle_index', 'Start_price', 'End_price', 'Max_candle_index', 'Max_price', 'Min_candle_index',
            'Min_price', 'Duration',
            'Price_range', 'Price_coverage', 'Direction', 'Slop', 'Num_sub_monowave', 'Prev_wave_retracement_ratio',
            'Next_wave_retracement_ratio', 'Num_retracement_rule', 'Num_condition',
            'Wave_category', 'Structure_list_label', 'Candid_elliott_end', 'EW_structure'
        ]  # Wave_category is only relevant/valid for Rule 4
        self.types = [
            np.int, np.int, np.int, np.int, np.float, np.float, np.int, np.float, np.int, np.float, np.int,
            np.float, np.float, np.int, np.float, np.int, np.float,
            np.float, np.int, np.str, np.int,
            np.object, np.bool, np.object
        ]
        self.default = {'MW_start_index': 0, 'MW_end_index': 0, 'Start_candle_index': 0,
                        'End_candle_index': 0, 'Start_price': 0, 'End_price': 0, 'Max_candle_index': 0, 'Max_price': 0,
                        'Min_candle_index': 0, 'Min_price': 0, 'Duration': 0,
                        'Price_range': 0, 'Price_coverage': 0, 'Direction': 0, 'Slop': 0, 'Num_sub_monowave': 1,
                        'Prev_wave_retracement_ratio': 0,
                        'Next_wave_retracement_ratio': 0, 'Num_retracement_rule': 0, 'Num_condition': '-',
                        'Wave_category': 0,
                        'Structure_list_label': [], 'Candid_elliott_end': False, 'EW_structure': []
                        }
        # self.monowaves = pd.DataFrame(columns=self.cols)
        self.monowaves = df_empty(self.cols, self.types)

    def buildMonoWave(self, key='Price'):
        dataF_price_node = self.nodes
        start = 0
        num_candles = dataF_price_node.shape[0]
        curr_direction = dataF_price_node[key][1] - dataF_price_node[key][0]
        if curr_direction == 0: curr_direction = 1
        mw_cnt = 0
        while start < (num_candles - 2):
            #  find out where the current monowave ends
            for j in range(start + 1, num_candles - 1):
                next_direction = dataF_price_node[key][j + 1] - dataF_price_node[key][j]
                if next_direction == 0:
                    continue
                if curr_direction * next_direction < 0:
                    break
            # if curr_direction * next_direction > 0:
            #     j = j + 1
            price_range = abs(dataF_price_node[key][start] -
                              dataF_price_node[key][j]) + 0.001
            time = j - start
            sl = np.degrees(np.arctan(price_range / time))
            direction = 1 if (curr_direction > 0) else -1
            max_price = dataF_price_node[key][j] if (direction > 0) else dataF_price_node[key][start]
            min_price = dataF_price_node[key][j] if (direction < 0) else dataF_price_node[key][start]
            max_candle_index = j if (direction > 0) else start
            min_candle_index = j if (direction < 0) else start
            price_coverage = max_price - min_price
            vals = {
                'MW_start_index': mw_cnt,
                'MW_end_index': mw_cnt,
                'Start_candle_index': start,
                'End_candle_index': j,
                'Start_price': dataF_price_node[key][start],
                'End_price': dataF_price_node[key][j],
                'Max_candle_index': max_candle_index,
                'Min_candle_index': min_candle_index,
                'Max_price': max_price,
                'Min_price': min_price,
                'Duration': time,
                'Price_range': price_range,
                'Price_coverage': price_coverage,
                'Direction': direction,
                'Slop': sl,
                'Num_retracement_rule': 0,
            }
            default_vals = copy.deepcopy({**self.default, **vals})
            self.monowaves = self.monowaves.append(default_vals, ignore_index=True)
            mw_cnt = mw_cnt + 1
            curr_direction = next_direction
            start = j

        # if curr_direction * next_direction < 0:
        #     price_range = abs(dataF_price_node[key][start] - dataF_price_node[key][num_candles-1])
        #     time = num_candles - start - 1
        #     sl = np.degrees(np.arctan(price_range/time))
        #     direction = 1 if (curr_direction > 0) else -1
        #     start = self.monowaves.at[-1,"End_candle_index"]
        #     self.monowaves = self.monowaves.append([{'MW_start_index':mw_cnt,'MW_end_index':mw_cnt,'Start_candle_index':start,'End_candle_index':num_candles-1,'Start_price': dataF_price_node[key][start] , 'End_price': dataF_price_node[key][num_candles-1] ,'Duration':time,'Price_range':price_range,'Direction':direction,'Slop':sl}], ignore_index=True)
        # else :
        #     self.monowaves.at[-1,"End_candle_index"] = num_candles-1

    def buildMonoWaveFromNEO(self, mark, key='Price'):
        dataF_price_node = self.nodes
        start = 0
        num_candles = dataF_price_node.shape[0]

        pbar = tqdm(total=num_candles - 2, desc="Building Monowaves from candles")
        mw_cnt = 0
        for i in range(len(mark)):
            j = mark[i]
            price_range = abs(dataF_price_node[key][start] -
                              dataF_price_node[key][j]) + sys.float_info.epsilon
            time = j - start
            sl = np.degrees(np.arctan(price_range / time))
            curr_direction = dataF_price_node[key][j] - dataF_price_node[key][start]
            if curr_direction == 0: curr_direction = 1
            direction = 1 if (curr_direction > 0) else -1
            max_price = dataF_price_node[key][j] if (direction > 0) else dataF_price_node[key][start]
            min_price = dataF_price_node[key][j] if (direction < 0) else dataF_price_node[key][start]
            max_candle_index = j if (direction > 0) else start
            min_candle_index = j if (direction < 0) else start
            price_coverage = max_price - min_price
            vals = {
                'MW_start_index': mw_cnt,
                'MW_end_index': mw_cnt,
                'Start_candle_index': start,
                'End_candle_index': j,
                'Start_price': dataF_price_node[key][start],
                'End_price': dataF_price_node[key][j],
                'Max_candle_index': max_candle_index,
                'Min_candle_index': min_candle_index,
                'Max_price': max_price,
                'Min_price': min_price,
                'Duration': time,
                'Price_range': price_range,
                'Price_coverage': price_coverage,
                'Direction': direction,
                'Slop': sl,
                'Num_retracement_rule': 0,
            }
            default_vals = copy.deepcopy({**self.default, **vals})
            self.monowaves = self.monowaves.append(default_vals, ignore_index=True)
            mw_cnt = mw_cnt + 1

            pbar.update(j - start)
            start = j

        pbar.close()

    def convertToMonoWave(self, extremas_index, key='Price'):
        dataF_price_node = self.nodes
        start = 0
        num_candles = dataF_price_node.shape[0]
        curr_direction = dataF_price_node[key][extremas_index[1]] - dataF_price_node[key][extremas_index[0]]

        pbar = tqdm(total=num_candles - 2, desc="Convert Zigzag to Monowaves")
        mw_cnt = 0
        while start < (len(extremas_index) - 1):
            price_range = abs(dataF_price_node[key][extremas_index[start]] -
                              dataF_price_node[key][extremas_index[start + 1]])
            time = extremas_index[start + 1] - extremas_index[start]
            sl = np.degrees(np.arctan(price_range / time))
            direction = 1 if (curr_direction > 0) else -1
            max_price = dataF_price_node[key][extremas_index[start + 1]] if (direction > 0) else dataF_price_node[key][
                extremas_index[start]]
            min_price = dataF_price_node[key][extremas_index[start + 1]] if (direction < 0) else dataF_price_node[key][
                extremas_index[start]]
            max_candle_index = extremas_index[start + 1] if (direction > 0) else extremas_index[start]
            min_candle_index = extremas_index[start + 1] if (direction < 0) else extremas_index[start]
            price_coverage = max_price - min_price
            vals = {
                'MW_start_index': mw_cnt,
                'MW_end_index': mw_cnt,
                'Start_candle_index': extremas_index[start],
                'End_candle_index': extremas_index[start + 1],
                'Start_price': dataF_price_node[key][extremas_index[start]],
                'End_price': dataF_price_node[key][extremas_index[start + 1]],
                'Max_candle_index': max_candle_index,
                'Min_candle_index': min_candle_index,
                'Max_price': max_price,
                'Min_price': min_price,
                'Duration': time,
                'Price_range': price_range,
                'Price_coverage': price_coverage,
                'Direction': direction,
                'Slop': sl,
                'Num_retracement_rule': 0,
            }
            default_vals = copy.deepcopy({**self.default, **vals})
            self.monowaves = self.monowaves.append(default_vals, ignore_index=True)
            mw_cnt = mw_cnt + 1
            curr_direction = dataF_price_node[key][extremas_index[start + 1]] - dataF_price_node[key][
                extremas_index[start]]
            pbar.update(extremas_index[start + 1] - extremas_index[start])
            start = start + 1
        pbar.close()

    def build_hyper_monowaves(self, M1):
        """Return a list of hyper monowaves"""
        hyper_monowaves = []
        while M1 is not None:
            hyper_monowaves.append(M1)
            M1 = self.find_next(M1)

        return hyper_monowaves

    def find_next(self, M1):
        M1_idx = M1.MW_end_index
        M1_high = max(M1.Start_price, M1.End_price)
        M1_low = min(M1.Start_price, M1.End_price)
        M2_high = M1_low  # like finding max
        M2_low = M1_high  # like finding min
        local_low_index = -1
        local_high_index = -1

        hidden_max = -1
        hidden_min = np.finfo(np.float).max
        hidden_max_index = -1
        hidden_min_index = -1

        M2 = pd.Series(data=copy.deepcopy(self.default))
        for i in range(M1_idx + 1, self.monowaves.shape[0]):
            if self.monowaves.Num_sub_monowave[i] > 1:
                if hidden_max < self.monowaves.Num_sub_monowave[i].Max_Price:
                    hidden_max = self.monowaves.Num_sub_monowave[i].Max_Price
                    hidden_max_index = self.monowaves.Num_sub_monowave[i].Max_candle_index

                if hidden_min > self.monowaves.Num_sub_monowave[i].Min_Price:
                    hidden_min = self.monowaves.Num_sub_monowave[i].Min_Price
                    hidden_min_index = self.monowaves.Num_sub_monowave[i].Min_candle_index

            curr_mw_end_price = self.monowaves.End_price[i]
            if curr_mw_end_price > M2_high:
                M2_high = curr_mw_end_price
                local_high_index = i
            if curr_mw_end_price < M2_low:
                M2_low = curr_mw_end_price
                local_low_index = i
            if curr_mw_end_price > M1_high or curr_mw_end_price < M1_low:
                break

        try:
            n = i - M1_idx
        except NameError:
            return None
        if n > 2:
            if (local_low_index - M1_idx) % 2 != 0:
                i = local_low_index
            elif (local_high_index - M1_idx) % 2 != 0:
                i = local_high_index
        elif n == 2:
            i = M1_idx + 1  # m2 is confirmed complete somewhere within m1, since m3 exceeds m1 high/low

        M2.MW_start_index = M1.MW_end_index + 1
        M2.Start_price = M1.End_price
        M2.Start_candle_index = M1.End_candle_index
        if i < self.monowaves.shape[0]:
            M2.MW_end_index = self.monowaves.MW_end_index[i]
            M2.End_price = self.monowaves.End_price[i]
            M2.End_candle_index = self.monowaves.End_candle_index[i]
            M2.Price_range = abs(M2.End_price - M2.Start_price)
            M2.Duration = M2.End_candle_index - M2.Start_candle_index
            M2.Direction = -M1.Direction
            M2.Num_sub_monowave = i - M1_idx
            # max and min price/index
            M2.Min_price = min(M2.Start_price, M2.End_price, hidden_min)
            M2.Max_price = max(M2.Start_price, M2.End_price, hidden_max)
            M2.Min_candle_index = M2.Start_candle_index if np.argmin(
                [M2.Start_price, M2.End_price, hidden_min]) == 0 else M2.End_candle_index if np.argmin(
                [M2.Start_price, M2.End_price, hidden_min]) == 1 else hidden_min_index
            M2.Max_candle_index = M2.Start_candle_index if np.argmax(
                [M2.Start_price, M2.End_price, hidden_max]) == 0 else M2.End_candle_index if np.argmax(
                [M2.Start_price, M2.End_price, hidden_max]) == 1 else hidden_max_index
        else:
            M2.MW_end_index = self.monowaves.shape[0]

        return M2

    def find_prev(self, M1):
        M1_idx = M1.MW_start_index
        M1_high = max(M1.Start_price, M1.End_price)
        M1_low = min(M1.Start_price, M1.End_price)
        M0_high = M1_low  # like finding max
        M0_low = M1_high  # like finding min
        local_low_index = -1
        local_high_index = -1

        hidden_max = -1
        hidden_min = np.finfo(np.float).max
        hidden_max_index = -1
        hidden_min_index = -1

        M0 = pd.Series(data=copy.deepcopy(self.default))

        for i in range(M1_idx - 1, -1, -1):
            if self.monowaves.Num_sub_monowave[i] > 1:
                if hidden_max < self.monowaves.Num_sub_monowave[i].Max_Price:
                    hidden_max = self.monowaves.Num_sub_monowave[i].Max_Price
                    hidden_max_index = self.monowaves.Num_sub_monowave[i].Max_candle_index

                if hidden_min > self.monowaves.Num_sub_monowave[i].Min_Price:
                    hidden_min = self.monowaves.Num_sub_monowave[i].Min_Price
                    hidden_min_index = self.monowaves.Num_sub_monowave[i].Min_candle_index

            curr_mw_start_price = self.monowaves.Start_price[i]
            if curr_mw_start_price > M0_high:
                M0_high = curr_mw_start_price
                local_high_index = i
            if curr_mw_start_price < M0_low:
                M0_low = curr_mw_start_price
                local_low_index = i
            if curr_mw_start_price > M1_high or curr_mw_start_price < M1_low:
                break
        try:
            n = M1_idx - i
        except NameError:
            return None

        if n > 2:
            if (M1_idx - local_low_index) % 2 != 0:
                i = local_low_index
            elif (M1_idx - local_high_index) % 2 != 0:
                i = local_high_index
        elif n == 2:
            i = M1_idx - 1  # m2 is confirmed complete somewhere within m1, since m3 exceeds m1 high/low

        M0.MW_end_index = M1.MW_start_index - 1
        M0.End_price = M1.Start_price
        M0.End_candle_index = M1.Start_candle_index
        if i >= 0:
            M0.MW_start_index = self.monowaves.MW_start_index[i]
            M0.Start_price = self.monowaves.Start_price[i]
            M0.Start_candle_index = self.monowaves.Start_candle_index[i]
            M0.Price_range = abs(M0.End_price - M0.Start_price)
            M0.Duration = M0.End_candle_index - M0.Start_candle_index
            M0.Direction = -M1.Direction
            M0.Num_sub_monowave = M1_idx - i
            # max and min price/index
            M0.Min_price = min(M0.Start_price, M0.End_price, hidden_min)
            M0.Max_price = max(M0.Start_price, M0.End_price, hidden_max)
            M0.Min_candle_index = M0.Start_candle_index if np.argmin(
                [M0.Start_price, M0.End_price, hidden_min]) == 0 else M0.End_candle_index if np.argmin(
                [M0.Start_price, M0.End_price, hidden_min]) == 1 else hidden_min_index
            M0.Max_candle_index = M0.Start_candle_index if np.argmax(
                [M0.Start_price, M0.End_price, hidden_max]) == 0 else M0.End_candle_index if np.argmax(
                [M0.Start_price, M0.End_price, hidden_max]) == 1 else hidden_max_index

        else:
            M0.MW_start_index = -1

        return M0

    def EW_rules_single_wave(self, HMW, idx):
        M1 = HMW[idx]
        M0 = HMW[idx - 1] if (idx - 1 >= 0) else None
        M2 = HMW[idx + 1] if (idx + 1 < len(HMW)) else None
        M3 = HMW[idx + 2] if (idx + 2 < len(HMW)) else None
        M3retracement = 0
        m1_idx_e = M1.MW_end_index
        m1_idx_s = M1.MW_start_index

        if M2 is not None:

            if M2.MW_end_index < self.monowaves.shape[0]:
                M1.Next_wave_retracement_ratio = M2.Price_range / (M1.Price_range + 0.001)
                if (M1.Next_wave_retracement_ratio < (1 - fib_ratio)):
                    M1.Num_retracement_rule = 1
                elif (M1.Next_wave_retracement_ratio < (fib_ratio - fib_ratio_precision)):
                    M1.Num_retracement_rule = 2
                elif (M1.Next_wave_retracement_ratio < (fib_ratio + fib_ratio_precision)):
                    M1.Num_retracement_rule = 3
                elif (M1.Next_wave_retracement_ratio < 1):
                    M1.Num_retracement_rule = 4
                elif (M1.Next_wave_retracement_ratio < (1 + fib_ratio)):
                    M1.Num_retracement_rule = 5
                elif (M1.Next_wave_retracement_ratio <= (2 + fib_ratio)):
                    M1.Num_retracement_rule = 6
                else:
                    M1.Num_retracement_rule = 7

        if (M0 is not None):

            if M0.MW_start_index >= 0:
                M1.Prev_wave_retracement_ratio = M0.Price_range / M1.Price_range
                if (M1.Num_retracement_rule == 1):
                    if (M1.Prev_wave_retracement_ratio < fib_ratio):
                        M1.Num_condition = 'a'
                    elif (M1.Prev_wave_retracement_ratio < 1):
                        M1.Num_condition = 'b'
                    elif (M1.Prev_wave_retracement_ratio <= (1 + fib_ratio)):
                        M1.Num_condition = 'c'
                    else:
                        M1.Num_condition = 'd'

                elif (M1.Num_retracement_rule == 2):
                    if (M1.Prev_wave_retracement_ratio < (1 - fib_ratio)):
                        M1.Num_condition = 'a'
                    elif (M1.Prev_wave_retracement_ratio < fib_ratio):
                        M1.Num_condition = 'b'
                    elif (M1.Prev_wave_retracement_ratio < 1):
                        M1.Num_condition = 'c'
                    elif (M1.Prev_wave_retracement_ratio <= (1 + fib_ratio)):
                        M1.Num_condition = 'd'
                    else:
                        M1.Num_condition = 'e'

                elif (M1.Num_retracement_rule == 3):
                    if (M1.Prev_wave_retracement_ratio < (1 - fib_ratio)):
                        M1.Num_condition = 'a'
                    elif (M1.Prev_wave_retracement_ratio < fib_ratio):
                        M1.Num_condition = 'b'
                    elif (M1.Prev_wave_retracement_ratio < 1):
                        M1.Num_condition = 'c'
                    elif (M1.Prev_wave_retracement_ratio < (1 + fib_ratio)):
                        M1.Num_condition = 'd'
                    elif (M1.Prev_wave_retracement_ratio <= (2 + fib_ratio)):
                        M1.Num_condition = 'e'
                    else:
                        M1.Num_condition = 'f'

                elif (M1.Num_retracement_rule == 4):
                    if (M1.Prev_wave_retracement_ratio < (1 - fib_ratio)):
                        M1.Num_condition = 'a'
                    elif (M1.Prev_wave_retracement_ratio < 1):
                        M1.Num_condition = 'b'
                    elif (M1.Prev_wave_retracement_ratio < (1 + fib_ratio)):
                        M1.Num_condition = 'c'
                    elif (M1.Prev_wave_retracement_ratio <= (2 + fib_ratio)):
                        M1.Num_condition = 'd'
                    else:
                        M1.Num_condition = 'e'

                    if (M3 is not None):
                        M3retracement = M3.Price_range / M2.Price_range
                        if (M3retracement >= 1 and M3retracement < (1 + fib_ratio)):
                            M1.Wave_category = 1
                        elif (M3retracement >= (1 + fib_ratio) and M3retracement <= (2 + fib_ratio)):
                            M1.Wave_category = 2
                        elif (M3retracement > (2 + fib_ratio)):
                            M1.Wave_category = 3


                elif (M1.Num_retracement_rule == 5):
                    if (M1.Prev_wave_retracement_ratio < 1):
                        M1.Num_condition = 'a'
                    elif (M1.Prev_wave_retracement_ratio < (1 + fib_ratio)):
                        M1.Num_condition = 'b'
                    elif (M1.Prev_wave_retracement_ratio <= (2 + fib_ratio)):
                        M1.Num_condition = 'c'
                    else:
                        M1.Num_condition = 'd'

                elif (M1.Num_retracement_rule == 6):
                    if (M1.Prev_wave_retracement_ratio < 1):
                        M1.Num_condition = 'a'
                    elif (M1.Prev_wave_retracement_ratio < (1 + fib_ratio)):
                        M1.Num_condition = 'b'
                    elif (M1.Prev_wave_retracement_ratio <= (2 + fib_ratio)):
                        M1.Num_condition = 'c'
                    else:
                        M1.Num_condition = 'd'

                elif (M1.Num_retracement_rule == 7):
                    if (M1.Prev_wave_retracement_ratio < 1):
                        M1.Num_condition = 'a'
                    elif (M1.Prev_wave_retracement_ratio < (1 + fib_ratio)):
                        M1.Num_condition = 'b'
                    elif (M1.Prev_wave_retracement_ratio <= (2 + fib_ratio)):
                        M1.Num_condition = 'c'
                    else:
                        M1.Num_condition = 'd'
        return M1

    def EW_rules(self, hyper_monowaves):
        for i in range(len(hyper_monowaves)):
            hyper_monowaves[i] = self.EW_rules_single_wave(hyper_monowaves, i)

    # region Eliottwave Rules
    def EW_R1a(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M0 = hyper_monowaves[idx - 1] if (idx - 1 >= 0) else None
        M_1 = hyper_monowaves[idx - 2] if (idx - 2 >= 0) else None
        M_2 = hyper_monowaves[idx - 3] if (idx - 3 >= 0) else None
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None
        M4 = hyper_monowaves[idx + 3] if (idx + 3 < n) else None
        M5 = hyper_monowaves[idx + 4] if (idx + 4 < n) else None
        sw1 = 0
        sw2 = 0

        if (M2 is not None):
            if (M2.Duration >= M1.Duration):
                M1.Structure_list_label.append(':5')
                M1.EW_structure.append('1a:-')
                sw1 = 1
            elif (M3 is not None):
                if (M2.Duration >= M3.Duration):
                    M1.Structure_list_label.append(':5')
                    M1.EW_structure.append('1a:-')
                    sw1 = 1
            if (M4 is not None and M_1 is not None):
                if ((1 <= (M_1.Price_range / M0.Price_range) <= 1.618)
                        and (waves_are_fib_related(M0.Price_range, M1.Price_range, 0.618, order=True))
                        # and (M4.Direction == 1 and M4.End_price <= M0.End_price) or (M4.Direction == -1 and M4.End_price >= M0.End_price))
                        and not wave_beyond(M4, M0)):
                    # m1 may complete a Flat pattern within a Complex formation where m2 is an x-wave
                    M1.Structure_list_label.append(':s5')
                    M1.EW_structure.append('1a:wave-c of Flat within a complex formation')
                    M2.Structure_list_label.append('x.c3')
                    M2.EW_structure.append('1a:x-wave')

            if M0 is not None:
                if (M0.Num_sub_monowave >= 3 and self.wave_is_retraced(M0, M1)):
                    # m0 is probably the end of an important Elliott pattern
                    M0.Candid_elliott_end = True

                if (self.waves_are_similar(M0.Price_range, M2.Price_range, 0.618, order=False)
                        and self.waves_are_similar(M0.Duration, M2.Duration, 0.618, order=False)):
                    flag1 = False
                    if (M_1 is not None and M3 is not None):
                        if (M_1.Price_range / M1.Price_range >= 1.618):
                            if (wave_is_steeper(M3.Price_range, M3.Duration, M_1)):
                                flag1 = True
                            elif (M5 is not None and wave_is_steeper(abs(M5.End_price - M3.Start_price),
                                                                     (M5.End_candle_index - M3.Start_candle_index),
                                                                     M_1)):
                                flag1 = True
                            if (flag1):
                                # A Running Correction (any variation) is probably unfolding
                                if (sw1 == 0):
                                    M1.Structure_list_label.append(':5')
                                    M1.EW_structure.append('1a:Running Correction')
                                M1.Structure_list_label.append('[:c3]')
                                M1.EW_structure.append('1a:Running Correction')
                        else:
                            if (M_1.Price_range > M0.Price_range):
                                if (M3 is not None and M3.Price_range / M1.Price_range >= 1.618):
                                    flag1 = True
                                elif (M5 is not None and M5.Price_range / M1.Price_range >= 1.618):
                                    flag1 = True
                                if (flag1):
                                    if (M_2 is not None):
                                        if (M_2.Price_range >= M_1.Price_range):
                                            M_1.Structure_list_label.append(':sL3')
                                            M_1.EW_structure.append('1a:-')
                                        elif (M3 is not None and M3.Price_range / M1.Price_range <= 1.618):
                                            # ※ A Running Correction (complex Double Three variety) may be unfolding, which starts at mn2 and ends at m4
                                            M1.Structure_list_label.append('x.c3')
                                            M1.EW_structure.append('1a:Running Correction')
                                            sw2 = 1

                                    # A Running Correction (any variation), which concludes more than one pattern, might be under formation
                                    if (sw2 == 0):
                                        M1.Structure_list_label.append(':c3')
                                        M1.EW_structure.append('1a:Running Correction')
                    if (M3 is not None):
                        if (M3.Price_range / M1.Price_range < 1.618 and (M4 is None or self.wave_is_retraced(M3, M4))):
                            # ※ m1 may be part of a Complex Correction which will necessitate the use of an x-wave
                            if (sw1 == 0):
                                M1.Structure_list_label.append(':5')
                                M1.EW_structure.append('1a:Complex Correction')
                            if (M_2 is not None and M_2.Price_range > M_1.Price_range):
                                # ※ The x-wave is not at the end of m0
                                # if (sw1==0):
                                #    M1.Structure_list_label.append(':5')
                                pass
                            else:
                                M0.Structure_list_label.append('x.c3')
                                M0.EW_structure.append('1a:Complex Correction')

                            # M1.Structure_list_label.append(':?H:?')
                            if (M3.Price_range / M1.Price_range < 1.618):
                                # ※ The probabilities increase dramatically that the x-wave is hidden in the center of m1"
                                M1.Structure_list_label.append(':?H:?')
                                M1.EW_structure.append('1a:Hidden')


                elif ((not wave_overlap(M0, M2)) and M3 is not None and self.wave_not_shortest(M_1.Price_range,
                                                                                               M1.Price_range,
                                                                                               M3.Price_range)):
                    # ※ m1 may be part of a larger Trending Impulse pattern"
                    if (sw1 == 0):
                        M1.Structure_list_label.append(':5')
                        M1.EW_structure.append('1a:part of larger Impulse')

        if (idx - 2 >= 0): hyper_monowaves[idx - 2] = M_1
        if (idx - 1 >= 0): hyper_monowaves[idx - 1] = M0
        hyper_monowaves[idx] = M1
        # if(((M0.Price_range == M2.Price_range and M0.Duration == M2.Duration) \
        #     or (((fib_ratio - fib_ratio_precision) < (M0.Price_range / M2.Price_range) < (fib_ratio + fib_ratio_precision)) and ((fib_ratio - fib_ratio_precision) < (M0.Duration / M2.Duration) < (fib_ratio + fib_ratio_precision)))\
        #     or (((fib_ratio - fib_ratio_precision) < (M2.Price_range / M0.Price_range) < (fib_ratio + fib_ratio_precision)) and ((fib_ratio - fib_ratio_precision) < (M2.Duration / M0.Duration) < (fib_ratio + fib_ratio_precision))))\
        #     and ((M_1.Price_range / M1.Price_range) < fib_ratio)\
        #     and (M_1.Price_range > M0.Price_range)
        #     and (((M3.Price_range / M1.Price_range) >= (1 + fib_ratio)) or ((M5.Price_range / M1.Price_range) >= (1 + fib_ratio)))):
        #     M1.Structure_list_label.append(':c3')

    def EW_R1b(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M0 = hyper_monowaves[idx - 1] if (idx - 1 >= 0) else None
        M_1 = hyper_monowaves[idx - 2] if (idx - 2 >= 0) else None
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None
        M4 = hyper_monowaves[idx + 3] if (idx + 3 < n) else None
        M6 = hyper_monowaves[idx + 5] if (idx + 5 < n) else None

        # self.monowaves.loc[m1_idx, 'Structure_list_label'] = []
        M1.Structure_list_label = []
        # ※ Structure and progress labels of m1 would be :5
        M1.Structure_list_label.append(':5')
        M1.EW_structure.append('1b:-')
        if (M4 is not None and M_1 is not None):
            if (1 <= (M_1.Price_range / M0.Price_range) <= 1.618 and not (wave_beyond(M0, M4))):
                # ※ m1 may complete a Flat pattern within a Complex formation where m2 is an x-wave
                M1.Structure_list_label.append(':s5')
                M1.EW_structure.append('1b:wave-c of Flat within a complex formation')
                M2.Structure_list_label.append('x.c3?')
                M2.EW_structure.append('1b:x-wave')

        if (M0.Num_sub_monowave >= 3 and self.wave_is_retraced(M0, M1)):
            # ※ m0 might conclude an important Elliott pattern
            M0.Candid_elliott_end = True
        if (wave_overlap(M0, M2) and M3 is not None and M_1 is not None):
            if (wave_is_steeper(M3.End_price, M3.Duration, M1)):
                if (M_1.Price_range > M1.Price_range):
                    M1.Structure_list_label.append(':sL3')
                    M1.EW_structure.append('1b:-')
                elif (not (self.waves_are_similar(M0.Price_range, M2.Price_range)) or not (
                        self.waves_are_similar(M0.Duration, M2.Duration))):
                    if (M4 is not None and self.wave_retrace_beyond(M1, M4,
                                                                    (M3.End_candle_index - M1.Start_candle_index) // 2,
                                                                    M4.Duration)):
                        # A 5th Extension Terminal pattern may have completed with m3
                        M1.Structure_list_label.append(":c3")
                        M1.EW_structure.append('1b:Extension Terminal')
                    elif (M6 is not None and self.wave_retrace_beyond(M1, M4, (
                                                                                      M3.End_candle_index - M1.Start_candle_index) // 2,
                                                                      (M6.End_candle_index - M4.Start_candle_index))):
                        # A 5th Extension Terminal pattern may have completed with m3
                        M1.Structure_list_label.append(":c3")
                        M1.EW_structure.append('1b:Extension Terminal')
            if (M3.Price_range < M1.Price_range and M_1.Price_range > M0.Price_range and self.wave_not_shortest(
                    M_1.Price_range, M1.Price_range, M3.Price_range)
                    and self.wave_retrace_beyond(M1, M3, (M3.End_candle_index - M_1.Start_candle_index) // 2,
                                                 M3.Duration)):
                M1.Structure_list_label.append(":c3")
                M1.EW_structure.append('1b:-')

        if (idx - 1 >= 0): hyper_monowaves[idx - 1] = M0
        hyper_monowaves[idx] = M1
        if (idx + 1 < n): hyper_monowaves[idx + 1] = M2

    def EW_R1c(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M0 = hyper_monowaves[idx - 1] if (idx - 1 >= 0) else None
        M_1 = hyper_monowaves[idx - 2] if (idx - 2 >= 0) else None
        M_2 = hyper_monowaves[idx - 3] if (idx - 3 >= 0) else None
        M_3 = hyper_monowaves[idx - 4] if (idx - 4 >= 0) else None
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None
        M4 = hyper_monowaves[idx + 3] if (idx + 3 < n) else None

        # ※ Structure and progress notation of m1 would be :5
        if (M3 is not None and self.waves_almost_same(M0.Price_range, M1.Price_range) and
                self.waves_are_similar(M0.Duration, M1.Duration, fib_ratio) and wave_is_steeper(M3.Price_range,
                                                                                                M3.Duration, M1)
                and (M2.Duration >= M0.Duration or M2.Duration >= M1.Duration) and self.waves_almost_same(
                    M2.Price_range, (1 - fib_ratio) * M1.Price_range)
                and check_subitem_in_list(M0.Structure_list_label, ':F3')):
            M1.Structure_list_label.append('[:c3]')
            M1.EW_structure.append('1c:-')

        if (M4 is not None and M_2 is not None and wave_is_steeper(M3.Price_range, M3.Duration, M1)
                and (1 < M4.Price_range / M3.Price_range or M4.Price_range / M3.Price_range < fib_ratio)
                and self.waves_almost_same(M2.Price_range, (1 - fib_ratio) * M1.Price_range)
                and check_subitem_in_list(M0.Structure_list_label, ':c3') and M_3.Price_range > M_2.Price_range
                and (M_2.Price_range > M0.Price_range or M_1.Price_range > M0.Price_range)):
            M1.Structure_list_label.append('(:sL3)')
            M1.EW_structure.append('1c:-')

        hyper_monowaves[idx] = M1

    def EW_R1d(self, hyper_monowaves, idx):
        # ※ There is only one possibility
        M1 = hyper_monowaves[idx]
        M1.Structure_list_label.append(':5')
        M1.EW_structure.append('1d:-')
        hyper_monowaves[idx] = M1

    def EW_R2a(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M0 = hyper_monowaves[idx - 1] if (idx - 1 >= 0) else None
        M_1 = hyper_monowaves[idx - 2] if (idx - 2 >= 0) else None
        M_2 = hyper_monowaves[idx - 3] if (idx - 3 >= 0) else None
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None
        M4 = hyper_monowaves[idx + 3] if (idx + 3 < n) else None
        M5 = hyper_monowaves[idx + 4] if (idx + 4 < n) else None
        M6 = hyper_monowaves[idx + 5] if (idx + 5 < n) else None

        # ※ Structure and progress labels of m1 would be :5
        M1.Structure_list_label.append(':5')
        M1.EW_structure.append('2a:-')
        if (M0 is not None):
            if (M4 is not None):
                if (not (wave_beyond(M0, M4))):
                    # ※ m1 may be completing a Correction within a Complex formation where m2 is an x-wave
                    M1.Structure_list_label.append(':s5')
                    M1.EW_structure.append('2a:Complex Correction')
                    M2.Structure_list_label.append('x.c3?')
                    M2.EW_structure.append('2a:x-wave')
                if (M_1 is not None and self.wave_not_shortest(M_1.Price_range, M1.Price_range,
                                                               M3.Price_range) and self.wave_longer_fib(M_1.Price_range,
                                                                                                        M1.Price_range,
                                                                                                        M3.Price_range)
                        and M4.Price_range / M3.Price_range >= 0.618):
                    # ※ The market may be forming an Impulse pattern with m1 the center phase (wave 3)
                    M1.Structure_list_label.append(':5')
                    M1.EW_structure.append('2a:wave3 of impulse')
            if (M0.Num_sub_monowave >= 3 and self.wave_is_retraced(M0, M1)):
                # ※ m0 is probably the end of an important Elliott pattern
                M0.Candid_elliott_end = True
            if (M2 is not None and waves_are_fib_related(M0.Price_range, M2.Price_range) and self.waves_are_similar(
                    M0.Duration, M1.Duration)):
                if (M_1 is not None):
                    if (M3 is not None and M_1.Price_range / M1.Price_range >= (1 + fib_ratio)
                            and wave_is_steeper(M3.Price_range, M3.Duration, M_1)):
                        # A Running Correction (any variation) is probably unfolding which most likely started with m0 and concluded with m2
                        M1.Structure_list_label.append('[:c3]')
                        M1.EW_structure.append('2a:Running Correction')
            if (M3 is not None and M_1 is not None and self.waves_almost_same(M0.Duration,
                                                                              M2.Duration) and M3.Price_range / M1.Price_range < (
                    1 + fib_ratio)
                    and M_1.Price_range > M0.Price_range):
                # ※ m1 might be part of a Complex Correction which will necessitate the use of an x-wave
                if (M_2 is not None and M_2.Price_range < M_1.Price_range):
                    # ※ The x-wave might be at the end of m0
                    M0.Structure_list_label.append('x.c3?')
                    M0.EW_structure.append('2a:Hidden')
                elif (M4 is not None and M4.Price_range / M3.Price_range <= (1 + fib_ratio)):
                    # ※ The x-wave may be at the end of m2
                    M2.Structure_list_label.append('x.c3?')
                    M2.EW_structure.append('2a:Hidden')
                elif (M0.Price_range / M1.Price_range <= 0.5 and M1.Price_range > max(M_1.Price_range, M3.Price_range)):
                    # ※ The x-wave may be hidden in the center of m1, which is most rare case
                    M1.Structure_list_label.append(':?H:?')
                    M1.EW_structure.append('2a:Hidden')
            if (M_1 is not None and M4 is not None
                    and M_1.Price_range > M0.Price_range and M0.Price_range < M1.Price_range
                    and self.wave_not_shortest(M_1.Price_range, M1.Price_range, M3.Price_range)
                    and self.wave_is_retraced(M3, M4)):
                # ※ m1 may be wave 3 of a Terminal Impulse pattern
                M1.Structure_list_label.append(':c3')
                M1.EW_structure.append('2a:Terminal Impulse')

        if (idx - 1 >= 0): hyper_monowaves[idx - 1] = M0
        if (idx + 1 < n): hyper_monowaves[idx + 1] = M2
        hyper_monowaves[idx] = M1

    def EW_R2b(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M0 = hyper_monowaves[idx - 1] if (idx - 1 >= 0) else None
        M_1 = hyper_monowaves[idx - 2] if (idx - 2 >= 0) else None
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None
        M4 = hyper_monowaves[idx + 3] if (idx + 3 < n) else None

        # ※ Structure and progress labels of m1 would be :5
        M1.Structure_list_label.append(':5')
        M1.EW_structure.append('2b:-')
        if M0 is not None:
            if (M4 is not None and not (wave_beyond(M0, M4))):
                # ※ m1 may complete a Correction within a Complex formation where m2 is an x-wave
                M1.Structure_list_label.append(':s5')
                M1.EW_structure.append('2b:Complex Correction')
                M2.Structure_list_label.append('x.c3?')
                M2.EW_structure.append('2b:x-wave')

            if (M0.Num_sub_monowave >= 3 and self.wave_is_retraced(M0, M1)):
                # ※ m0 is probably the end of an important Elliott pattern
                M0.Candid_elliott_end = True

            if (M2 is not None and self.waves_are_similar(M0.Price_range, M2.Price_range) and self.waves_are_similar(
                    M0.Duration, M2.Duration)):
                if (M_1 is not None and M3 is not None and M_1.Price_range <= (1 + fib_ratio) * M1.Price_range
                        and wave_is_steeper(M3.Price_range, M3.Duration, M_1)):
                    # ※ A Running Correction (any variation) is probably unfolding which most likely started with m0 and concluded with m2
                    M1.Structure_list_label.append('[:c3]')
                    M1.EW_structure.append('2b:Running Correction')

            if (M4 is not None and self.waves_almost_same(M0.Price_range, M2.Price_range) and self.waves_almost_same(
                    M0.Duration, M2.Duration)
                    and M3.Price_range / M1.Price_range < (1 + fib_ratio)
                    and self.wave_is_retraced(M3, M4)):
                # ※ m1 may be part of a Complex Correction which will necessitate the use of an x-wave
                if (M3.Price_range / M1.Price_range < fib_ratio):
                    # ※ The probabilities increase dramatically that the x-wave, if any, is hidden in the center of m1
                    M1.Structure_list_label.append(':?H:?')
                    M1.EW_structure.append('2b:Hidden')
                else:
                    M0.Structure_list_label.append('x.c3?')
                    M0.EW_structure.append('2b:-')
                    M2.Structure_list_label.append('x.c3?')
                    M2.EW_structure.append('2b:-')

            if (M4 is not None and M_1 is not None and wave_overlap(M0, M2)
                    and (fib_ratio < M2.Duration / M0.Duration or M0.Duration / M2.Duration > fib_ratio)
                    and self.wave_not_shortest(M_1.Price_range, M1.Price_range, M3.Price_range)
                    and wave_beyond(M0, M4)):
                # ※ There is a chance m1 is an :sL3 which is part of a Terminal pattern
                M1.Structure_list_label.append(':sL3')
                M1.EW_structure.append('2b:Terminal')

        if (idx - 1 >= 0): hyper_monowaves[idx - 1] = M0
        if (idx + 1 < n): hyper_monowaves[idx + 1] = M2
        hyper_monowaves[idx] = M1

    def EW_R2c(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M0 = hyper_monowaves[idx - 1] if (idx - 1 >= 0) else None
        M_1 = hyper_monowaves[idx - 2] if (idx - 2 >= 0) else None
        M_2 = hyper_monowaves[idx - 3] if (idx - 3 >= 0) else None
        M_3 = hyper_monowaves[idx - 4] if (idx - 4 >= 0) else None
        M_4 = hyper_monowaves[idx - 5] if (idx - 5 >= 0) else None
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None
        M4 = hyper_monowaves[idx + 3] if (idx + 3 < n) else None

        M1.Structure_list_label.append(':5')
        M1.EW_structure.append('2c:-')
        if M0 is not None:
            if (M4 is not None and not (wave_beyond(M0, M4))):
                # ※ m1 may complete a Flat within a Complex formation where m2 is an x-wave
                M1.Structure_list_label.append(':s5')
                M1.EW_structure.append('2c:Flat within a Complex formation')
                M2.Structure_list_label.append('x.c3?')
                M2.EW_structure.append('2c:x-wave')

                if (M_2 is not None and M_2.Price_range < M_1.Price_range):
                    if (M_4 is not None and M_4.Price_range > M_3.Price_range):
                        # ※ There may be a Complex formation where m0 is x
                        M0.Structure_list_label.append('x.c3')
                        M0.EW_structure.append('2c:Flat')
                elif (M_1 is not None and M1.Price_range / M_1.Price_range >= 0.382):
                    # ※ There may be a Complex formation where m2 is x
                    M2.Structure_list_label.append('x.c3')
                    M2.EW_structure.append('2c:x-wave')
            if (M0.Num_sub_monowave >= 3 and self.wave_is_retraced(M0, M1)):
                # ※ m0 probably ends an important Elliott pattern
                M0.Candid_elliott_end = True
            if (M_1 is not None):
                ###########
                if (M4 is not None):
                    if (M0.Price_range < M_1.Price_range < 2.618 * M1.Price_range
                            and M3.Price_range < M1.Price_range and self.wave_retrace_beyond(M1, M4, M4.Duration,
                                                                                             M4.Duration)):
                        # ※ A Terminal pattern may have completed with m3
                        M1.Structure_list_label.append(':c3')
                        M1.EW_structure.append('2c:Terminal')

                if (M3 is not None):
                    if (self.wave_is_retraced(M2, M3) and wave_is_steeper(M3.Price_range, M3.Duration, M1)
                            and M_1.Price_range / M1.Price_range < (1 + fib_ratio)):
                        # ※ A Running Triangle may have terminated with m2
                        M1.Structure_list_label.append(':sL3')
                        M1.EW_structure.append('2c:Running Triangle')
                        if (M4 is not None):
                            if self.wave_is_retraced(M3, M4):
                                # ※ The Triangle is of the Limiting variety
                                M1.EW_structure[-1] += " Limiting"
                            if (not self.wave_is_retraced(M3,
                                                          M4) or M4.Price_range / M4.Duration < M3.Price_range / M3.Duration):
                                # ※ The Triangle is probably of the Non-Limiting variety or m3 will become part of a 5 segment Terminal formation
                                M1.EW_structure[-1] += " Non-Limiting"
                    if (M_1.Price_range > (1 + fib_ratio) * M1.Price_range and M3.Price_range > (
                            1 + fib_ratio) * M1.Price_range):
                        # ※ An Irregular Failure may have completed with m2
                        M1.Structure_list_label.append(':c3')
                        M1.EW_structure.append('2c:Irregular Failure')

        if (idx - 1 >= 0): hyper_monowaves[idx - 1] = M0
        if (idx + 1 < n): hyper_monowaves[idx + 1] = M2
        hyper_monowaves[idx] = M1

    def EW_R2d(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M0 = hyper_monowaves[idx - 1] if (idx - 1 >= 0) else None
        M_1 = hyper_monowaves[idx - 2] if (idx - 2 >= 0) else None
        M_2 = hyper_monowaves[idx - 3] if (idx - 3 >= 0) else None
        M_3 = hyper_monowaves[idx - 4] if (idx - 4 >= 0) else None
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None
        M4 = hyper_monowaves[idx + 3] if (idx + 3 < n) else None

        if (M2 is not None):
            if (M2.Duration >= M1.Duration):
                M1.Structure_list_label.append(':5')
                M1.EW_structure.append('2d:-')
            elif (M3 is not None):
                if (M2.Duration >= M3.Duration):
                    M1.Structure_list_label.append(':5')
                    M1.EW_structure.append('2d:-')
                if (wave_is_steeper(M3.Price_range, M3.Duration, M1)):
                    if (M0 is not None and M4 is not None and self.wave_is_retraced(M3, M4)
                            and self.waves_are_similar(M0.Duration, M1.Duration)
                            and (waves_are_fib_related(M2.Duration, M0.Duration, order=True) or waves_are_fib_related(
                                M2.Duration, M1.Duration, order=True))
                            and M0.Price_range / M1.Price_range <= 1.382):
                        # ※ A severe c-Failure Flat may have concluded with m2
                        M1.Structure_list_label.append(':c3')
                        M1.EW_structure.append('2d:c-Failure Flat')
                    if (M4 is not None and M_3 is not None):
                        if (M4.Price_range / M3.Price_range >= 1 or M4.Price_range / M3.Price_range <= (1 + fib_ratio)
                                and M_3.Price_range > M_2.Price_range
                                and (M_2.Price_range > M0.Price_range or M_1.Price_range > M0.Price_range)
                                and check_subitem_in_list(M0.Structure_list_label, ':c3')):
                            # ※ m1 may be the second-to-last leg of a Contracting Triangle
                            M1.Structure_list_label.append(':sL3')
                            M1.EW_structure.append('2d:Contracting Triangle')
        if (M0 is not None and M4 is not None):
            if (M3.Price_range < M1.Price_range and M4.Price_range / M3.Price_range >= fib_ratio
                    and M1.Duration < M0.Duration and M2.Duration > M1.Duration):
                # ※ m1 is probably part of a Zigzag which concludes with m3
                M1.Structure_list_label.append(':5')
                M1.EW_structure.append('2d:Zigzag')

        hyper_monowaves[idx] = M1

    def EW_R2e(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M0 = hyper_monowaves[idx - 1] if (idx - 1 >= 0) else None
        M_1 = hyper_monowaves[idx - 2] if (idx - 2 >= 0) else None
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None

        # ※ No matter what the circumstances, :5 is a very likely structure label for m1
        M1.Structure_list_label.append(':5')
        M1.EW_structure.append('2e:-')
        if (M3 is not None and M_1 is not None
                and self.wave_is_retraced(M2, M3)
                and wave_is_steeper(M3.Price_range, M3.Duration, M1)
                and not wave_overlap(M_1, M1)):
            # ※ The market may have completed a Complex Correction at m2 with a missing x-wave in the middle of m0
            M1.Structure_list_label.append(':c3')
            M1.EW_structure.append('2e:-')
            M0.Structure_list_label.append(':?H:?')
            M0.EW_structure.append('2e:-')

        if (idx - 1 >= 0): hyper_monowaves[idx - 1] = M0
        hyper_monowaves[idx] = M1

    def EW_R3a(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M0 = hyper_monowaves[idx - 1] if (idx - 1 >= 0) else None
        M_1 = hyper_monowaves[idx - 2] if (idx - 2 >= 0) else None
        M_2 = hyper_monowaves[idx - 3] if (idx - 3 >= 0) else None
        M_3 = hyper_monowaves[idx - 4] if (idx - 4 >= 0) else None
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None
        M4 = hyper_monowaves[idx + 3] if (idx + 3 < n) else None
        M5 = hyper_monowaves[idx + 4] if (idx + 4 < n) else None

        if (M3 is not None):
            if (M3.Price_range / M1.Price_range > 2.618):
                # ※ m1 most likely is the center portion of a running correction
                M1.Structure_list_label.append(':c3')
                M1.EW_structure.append('3a:center portion of a Running Correction')

                if M_1 is None or (M_1.Price_range / M1.Price_range < 1.618):
                    # ※ m1 could be the end of a zig-zag within a complex correction
                    M1.Structure_list_label.append('(:s5)')
                    M1.EW_structure.append('3a:end zigzag within a complex correction ')
                    # ////////////////////////remove EW_structure
                if (M_3 is not None and M1.Price_range > max(M_1.Price_range, M_3.Price_range)
                        and self.wave_breaking_trend(M_2.End_candle_index, M0.End_candle_index, M1.End_candle_index,
                                                     M2.End_candle_index)):
                    # ※ m1 may be the 5 of a 5x (5 extension) impulse pattern
                    M1.Structure_list_label.append('[:L5]')
                    M1.EW_structure.append('3a:wave5 of 5x impulse')
                if (M_1 is None or M_1.Price_range / M3.Price_range < 0.618):
                    # ※ More than one Elliott pattern may have completed at m2
                    M2.Candid_elliott_end = True

            elif (M3.Price_range / M1.Price_range >= 1.618):
                # ※ m1 may be the center portion of a 5x impulse pattern with a 5th wave Extension
                M1.Structure_list_label.append(':s5')
                if (M_1 is not None and M_1.Price_range > M1.Price_range):
                    # ※ m1 could be the c-wave of a zig-zag within a complex correction; m2 would be an x-wave which is most likely followed by wave-a of a contracting triangle
                    M1.EW_structure.append('3a:wave-c of zigzag within a complex correction')
                    M2.Structure_list_label.append('x.c3')
                    M2.EW_structure.append('3a:x-wave')
                    M3.Structure_list_label.append(':F3')
                    M3.EW_structure.append('3a:wave-a of contracting triangle')

                else:
                    M1.EW_structure.append('3a:wave3 of 5x(extension) impulse')
                # ※ m1 may be the first leg of a pattern within a complex correction
                M1.Structure_list_label.append(':F3')
                M1.EW_structure.append('3a:wave1 of complex correction')
                # ※ m1 may be the center portion of a running correction
                if M_1 is None or M_1.Price_range < M3.Price_range:
                    M1.Structure_list_label.append(':c3')
                    M1.EW_structure.append('3a:center of running correction')

                if (M_3 is not None and M1.Price_range > max(M_1.Price_range, M_3.Price_range)
                        and self.wave_breaking_trend(M_2.End_candle_index, M0.End_candle_index, M1.End_candle_index,
                                                     M2.End_candle_index)):
                    # ※ m1 may be the 5 of a 5x impulse pattern
                    M1.Structure_list_label.append('[:L5]')
                    M1.EW_structure.append('3a:wave5 of 5x impulse')

            elif (M3.Price_range / M1.Price_range >= 1):
                if M_1 is None or M0.Duration > min(M_1.Duration, M1.Duration):
                    # ※ m1 may be the center portion(wave 3) of a 5x impulse pattern with a 5th-wave Extension
                    M1.Structure_list_label.append(':s5')

                    if (M_1 is not None and M_1.Price_range > M1.Price_range):
                        # ※ m1 could only be the c-wave of a zig-zag within a complex correction; m2 would be an x-wave
                        M1.EW_structure.append('3a:wave-c of zigzag within a complex correction')
                        M2.Structure_list_label.append('x.c3')
                        M2.EW_structure.append('3a:x-wave')
                    else:
                        M1.EW_structure.append('3a:wave3 of 5x(extension) impulse')

                if (M_3 is not None and M1.Price_range > max(M_1.Price_range, M_3.Price_range)
                        and self.wave_breaking_trend(M_2.End_candle_index, M0.End_candle_index, M1.End_candle_index,
                                                     M2.End_candle_index)):
                    # ※ m1 may be the 5 of a 5x impulse pattern"
                    M1.Structure_list_label.append('[:L5]')
                    M1.EW_structure.append('3a:wave5 of 5x impulse')
                if M4 is None or (M4.Price_range > M3.Price_range):
                    # ※ m1 may be the first leg of a standard pattern within a complex correction
                    M1.Structure_list_label.append(':F3')
                    M1.EW_structure.append('3a:wave1 of complex correction')

            else:
                if (M4 is not None):
                    if self.wave_is_retraced(M3, M4):
                        # ※ An impulse pattern may have concluded with m3
                        M1.Structure_list_label.append(':5')
                        M1.EW_structure.append('3a:impulse')
                        # ※ complex correction may have concluded with m3
                        M1.Structure_list_label.append(':F3')
                        M1.EW_structure.append('3a:complex correction')
                        if (M_1 is not None and M1.Price_range > max(M_1.Price_range, M_3.Price_range)
                                and self.wave_breaking_trend(M_2.End_candle_index, M0.End_candle_index,
                                                             M1.End_candle_index, M2.End_candle_index)):
                            # ※ m1 may be the 5 of a 5x impulse pattern
                            M1.Structure_list_label.append('[:L5]')
                            M1.EW_structure.append('3a:wave5 of 5x impulse')
                    elif self.wave_is_retraced_slower(M3, M4):
                        # ※ m1 concludes a zig-zag which is part of a complex corrective pattern
                        M1.Structure_list_label.append(':s5')
                        M1.EW_structure.append('3a:end of zigzag in complex correction')
                        if (M_3 is not None and M1.Price_range > max(M_1.Price_range, M_3.Price_range)
                                and self.wave_breaking_trend(M_2.End_candle_index, M0.End_candle_index,
                                                             M1.End_candle_index, M2.End_candle_index)):
                            # ※ m1 may be the 5 of a 5x impulse pattern
                            M1.Structure_list_label.append('[:L5]')
                            M1.EW_structure.append('3a:wave5 of impulse')
                    if (M4.Price_range < M3.Price_range):
                        # ※ m1 may have completed a zig-zag which is part of a complex correction
                        M1.Structure_list_label.append(':s5')
                        M1.EW_structure.append('3a:end zigzag in a complex correction')
                        # ※ m1 is part of a terminal impulsive pattern
                        M1.Structure_list_label.append(':F3')
                        M1.EW_structure.append('3a:zigzag which is part of a Terminal Impulse')
                        if M5 is not None:
                            if M5.Price_range < M3.Price_range:
                                # ※ A complex corrective pattern may have concluded with m3
                                M1.Structure_list_label.append(':F3')
                                M1.EW_structure.append('3a:complex corrective pattern')
                        else:
                            # ※ A complex corrective pattern may have concluded with m3
                            M1.Structure_list_label.append(':F3')
                            M1.EW_structure.append('3a:complex corrective pattern')

                        if M_3 is not None and (M1.Price_range > max(M_1.Price_range, M_3.Price_range)
                                                and self.wave_breaking_trend(M_2.End_candle_index, M0.End_candle_index,
                                                                             M1.End_candle_index, M2.End_candle_index)):
                            # ※ m1 may be the 5 of a 5x impulse pattern
                            M1.Structure_list_label.append('[:L5]')
                            M1.EW_structure.append('3a:wave5 of impulse')

        hyper_monowaves[idx] = M1
        if M2 is not None:
            hyper_monowaves[idx + 1] = M2
        if M3 is not None:
            hyper_monowaves[idx + 2] = M3

    def EW_R3b(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M_1 = hyper_monowaves[idx - 2] if (idx - 2 >= 0) else None
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None
        M4 = hyper_monowaves[idx + 3] if (idx + 3 < n) else None
        M5 = hyper_monowaves[idx + 4] if (idx + 4 < n) else None

        if M3 is not None:
            if M3.Price_range / M1.Price_range > 2.618:
                # ※ m1 most likely is the center portion of an irregular failure pattern
                M1.Structure_list_label.append(':c3')
                M1.EW_structure.append('3b:center portion of an irregular failure')

                if M_1 is None or M_1.Price_range / M1.Price_range < 1.618:
                    # ※ m1 could be wave-c of a zig-zag within a complex correction
                    M1.Structure_list_label.append('(:s5)')
                    M1.EW_structure.append('3b:end zigzag within a complex correction')
                if M_1 is not None and M_1.Price_range / M3.Price_range < 0.618:
                    # ※ One or more Elliott patterns may end at m2
                    M2.Candid_elliott_end = True

            elif M3.Price_range / M1.Price_range >= 1.618:
                # ※ m1 may be the c-wave of a zig-zag within a complex correction
                M1.Structure_list_label.append(':s5')
                M1.EW_structure.append('3b:wave-c of zig-zag within a complex correction ')

                if M_1 is None or M_1.Price_range < M1.Price_range:
                    # ※ m1 may be the center portion of a 5x terminal impulse pattern
                    M1.Structure_list_label.append(':c3')
                    M1.EW_structure.append('3b:wave3 of 5x terminal impulse')

                # ※ m1 may be the center portion of an irregular failure flat
                M1.Structure_list_label.append(':c3')
                M1.EW_structure.append('3b:center portion of an irregular failure(running correction)')


            elif M3.Price_range / M1.Price_range >= 1:

                if M_1 is None or M_1.Price_range < M1.Price_range:
                    # ※ m1 may be the center portion of a 5x terminal impulse pattern
                    M1.Structure_list_label.append(':c3')
                    M1.EW_structure.append('3b:center portion of a 5x terminal impulse')

                if M4 is None or M4.Price_range > M3.Price_range:
                    # ※ m1 may be the first leg of a zig-zag within a complex correction
                    M1.Structure_list_label.append(':5')
                    M1.EW_structure.append('3b:wave-a zigzag within a complex correction')

                if M4 is None or not self.wave_is_retraced(M3, M4):
                    # ※ m1 may be the last leg of a zig-zag within a complex correction
                    M1.Structure_list_label.append(':s5')
                    M1.EW_structure.append('3b:wave-c of zigzag within a complex correction')
                    if M_1 is None or M_1.Price_range < M1.Price_range:
                        M2.Structure_list_label.append('x.c3?')
                        M2.EW_structure.append('-')  # temporary
            else:
                if M4 is not None:
                    if self.wave_is_retraced(M3, M4):
                        # ※ m3 may complete a complex correction
                        M1.Structure_list_label.append(':5')
                        M1.EW_structure.append('3b:complex correction')
                        if M_1 is not None and self.wave_retrace_beyond(M_1, M4, (M3.End_candle_index - M_1.Start_candle_index) // 2,
                                                    M4.Duration) \
                                and M_1.Price_range / M1.Price_range <= 2.618:
                            # ※ m1 may be a part of a terminal impulse pattern
                            M1.Structure_list_label.append(':c3')
                            M1.EW_structure.append('3b:terminal impulse')
                    elif self.wave_is_retraced_slower(M3, M4):
                        # ※ m1 may conclude a zig-zag within a complex correction
                        M1.Structure_list_label.append(':s5')
                        M1.EW_structure.append('3b:end of zigzag within a complex correction')
                    if M4.Price_range < M3.Price_range:
                        # ※ m1 may be wave-c of a zig-zag within a complex correction
                        M1.Structure_list_label.append(':s5')
                        M1.EW_structure.append('3b:end of zigzag within a complex correction')
                    if M5 is not None:
                        if M5.Price_range < M3.Price_range:
                            # ※ m1 may be part of a terminal impulse pattern
                            M1.Structure_list_label.append(':F3')
                            M1.EW_structure.append('3b:zigzag which is part of a terminal impulse')
                    else:
                        # ※ m1 may be part of a terminal impulse pattern
                        M1.Structure_list_label.append(':F3')
                        M1.EW_structure.append('3b:part of a terminal impulse')

        hyper_monowaves[idx] = M1
        if (idx + 1 >= 0): hyper_monowaves[idx + 1] = M2

    def EW_R3c(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M0 = hyper_monowaves[idx - 1] if (idx - 1 >= 0) else None
        M_1 = hyper_monowaves[idx - 2] if (idx - 2 >= 0) else None
        M_2 = hyper_monowaves[idx - 3] if (idx - 3 >= 0) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None
        M4 = hyper_monowaves[idx + 3] if (idx + 3 < n) else None
        M5 = hyper_monowaves[idx + 4] if (idx + 4 < n) else None

        if M3 is not None:
            if M3.Price_range / M1.Price_range > 2.618:
                if M_1 is not None:
                    if M_1.Price_range / M1.Price_range <= 1.618:
                        # ※ m2 probably completed a non-limiting triangle
                        M1.Structure_list_label.append(':sL3')
                        M1.EW_structure.append('3c:non-limiting triangle')
                else:
                    # ※ m2 probably completed a non-limiting triangle
                    M1.Structure_list_label.append(':sL3')
                    M1.EW_structure.append('3c:non-limiting triangle')
                if M_2 is not None:
                    if M_1.Price_range / M1.Price_range > 1.618 or M_2.Price_range / M_1.Price_range > 0.618:
                        # ※ m2 probably completed an irregular failure flat
                        M1.Structure_list_label.append(':c3')
                        M1.EW_structure.append('3c:irregular failure flat')
                else:
                    M1.Structure_list_label.append(':c3')
                    M1.EW_structure.append('3c:irregular failure flat')

            elif M3.Price_range / M1.Price_range >= 1.618:

                if M_1 is not None:
                    if M_1.Price_range / M1.Price_range <= 1.618:
                        # ※ m1 may be the second-to-last leg of a contracting triangle
                        M1.Structure_list_label.append(':sL3')
                        M1.EW_structure.append('3c:SL of contracting triangle')
                    if M_1.Price_range / M1.Price_range > 1.618 or M0.Price_range / M_1.Price_range < 0.618:
                        # ※ m1 may be the center portion of an irregular failure flat
                        M1.Structure_list_label.append(':c3')
                        M1.EW_structure.append('3c:center portion of irregular failure flat')
                else:
                    # ※ m1 may be the second-to-last leg of a contracting triangle
                    M1.Structure_list_label.append(':sL3')
                    M1.EW_structure.append('3c:SL of contracting triangle')
                    # ※ m1 may be the center portion of an irregular failure flat
                    M1.Structure_list_label.append(':c3')
                    M1.EW_structure.append('3c:center portion of irregular failure flat')
                if M4 is not None:
                    if M4.Price_range > M3.Price_range:
                        # ※ m1 may be the part of a complex correction
                        M1.Structure_list_label.append(':F3')
                        M1.EW_structure.append('3c:part of a complex correction')
                    if not self.wave_is_retraced(M3, M4):
                        # ※ m1 may be the part of a complex correction
                        M1.Structure_list_label.append(':s5')
                        M1.EW_structure.append('3c:part of a  complex correction')
                else:
                    # ※ m1 may be the part of a complex correction
                    M1.Structure_list_label.append(':F3')
                    M1.EW_structure.append('3c:part of a complex correction')
                    # ※ m1 may be the part of a complex correction
                    M1.Structure_list_label.append(':s5')
                    M1.EW_structure.append('3c:part of a complex correction')


            elif M3.Price_range / M1.Price_range >= 1:
                if M_1 is not None:
                    if M_1.Price_range / M1.Price_range <= 1.618:
                        # ※ m1 may be the second-to-last leg of a contracting triangle
                        M1.Structure_list_label.append(':sL3')
                        M1.EW_structure.append('3c:SL of ontracting triangle')
                    if M_1.Price_range / M1.Price_range > 1.618 or M0.Price_range / M_1.Price_range < 0.618:
                        # ※ m1 may be the center portion of an irregular failure flat
                        M1.Structure_list_label.append(':c3')
                        M1.EW_structure.append('3c:center portion of irregular failure flat')
                else:
                    # ※ m1 may be the second-to-last leg of a contracting triangle
                    M1.Structure_list_label.append(':sL3')
                    M1.EW_structure.append('3c:SL of contracting triangle')
                    # ※ m1 may be the center portion of an irregular failure flat
                    M1.Structure_list_label.append(':c3')
                    M1.EW_structure.append('3c:center portion of irregular failure flat')
                if M4 is not None:
                    if M4.Price_range > M3.Price_range:
                        # ※ m1 may be one of the legs of a complex correction
                        M1.Structure_list_label.append(':F3')
                        M1.EW_structure.append('3c:one of the legs of complex correction')
                        # ※ m1 may be the center leg of a 5x terminal pattern
                        M1.Structure_list_label.append(':c3')
                        M1.EW_structure.append('3c:center of 5x Terminal')

                    if not self.wave_is_retraced(M3, M4):
                        # ※ m1 may be one of the legs of a complex correction
                        M1.Structure_list_label.append(':s5')
                        M1.EW_structure.append('3c:one of the legs of complex correction')
                else:
                    # ※ m1 may be one of the legs of a complex correction
                    M1.Structure_list_label.append(':F3')
                    M1.EW_structure.append('3c:one of the legs of complex correction')
                    # ※ m1 may be the center leg of a 5x terminal pattern
                    M1.Structure_list_label.append(':c3')
                    M1.EW_structure.append('3c:center of 5x Terminal')
                    # ※ m1 may be one of the legs of a complex correction
                    M1.Structure_list_label.append(':s5')
                    M1.EW_structure.append('3c:one of the legs of complex correction')
            else:
                if M4 is not None:
                    if self.wave_is_retraced(M3, M4):
                        # ※ m3 may complete a terminal impulse
                        M1.Structure_list_label.append(':F3')
                        M1.EW_structure.append('3c:terminal impulse')
                        if M_1 is not None and (M_1.Price_range / M1.Price_range > 2.618 or M_1.Price_range / M1.Price_range < 1.382):
                            # ※ m3 may complete a complex correction
                            M1.Structure_list_label.append('[:c3]')
                            M1.EW_structure.append('3c:complex correction')
                        else:
                            # ※ m3 may complete a complex correction
                            M1.Structure_list_label.append(':c3')
                            M1.EW_structure.append('3c:complex correction')

                    if self.wave_is_retraced_slower(M3, M4):
                        # ※ m1 may be wave-a of a zig-zag within a complex correction
                        M1.Structure_list_label.append(':F3')
                        M1.EW_structure.append('3c:wave1 of zig-zag')

                        if M5 is not None:
                            if not self.wave_is_retraced(M4, M5):
                                # m1 may be wave-c of a zig-zag within a complex correction
                                M1.Structure_list_label.append('(:s5)')
                                M1.EW_structure.append('3c:wave3 of zig-zag')
                        else:
                            # m1 may be wave-c of a zig-zag within a complex correction
                            M1.Structure_list_label.append('(:s5)')
                            M1.EW_structure.append('3c:wave3 of zig-zag')

                    if M4.Price_range < M3.Price_range:
                        # ※ m1 may be one of the center legs of a running contracting triangle
                        M1.Structure_list_label.append(':c3')
                        M1.EW_structure.append('3c:one of the center legs of running contracting triangle')
                        if M_1 is not None:
                            if M_1.Price_range / M1.Price_range < 2.618:
                                # ※ m1 may be the last leg of a zig-zag or flat within a complex correction
                                M1.Structure_list_label.append(':s5')
                                M1.EW_structure.append('3c:wave3 of zig-zag or flat within a complex correction')
                        else:
                            # ※ m1 may be the last leg of a zig-zag or flat within a complex correction
                            M1.Structure_list_label.append(':s5')
                            M1.EW_structure.append('3c:wave3 of zig-zag or flat within a complex correction')

                        if M5 is not None:
                            if M5.Price_range < M3.Price_range:
                                # ※ m1 may be the first leg of a terminal impulse pattern
                                M1.Structure_list_label.append('(:F3)')
                                M1.EW_structure.append('3c:wave1 of terminal impulse')
                        else:
                            # ※ m1 may be the first leg of a terminal impulse pattern
                            M1.Structure_list_label.append('(:F3)')
                            M1.EW_structure.append('3c:wave1 of terminal impulse')

        hyper_monowaves[idx] = M1

    def EW_R3d(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M0 = hyper_monowaves[idx - 1] if (idx - 1 >= 0) else None
        M_1 = hyper_monowaves[idx - 2] if (idx - 2 >= 0) else None
        M_2 = hyper_monowaves[idx - 3] if (idx - 3 >= 0) else None
        M_3 = hyper_monowaves[idx - 4] if (idx - 4 >= 0) else None
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None
        M4 = hyper_monowaves[idx + 3] if (idx + 3 < n) else None
        M5 = hyper_monowaves[idx + 4] if (idx + 4 < n) else None

        if M3 is not None:
            if M3.Price_range / M2.Price_range > 2.618:
                if M3.Price_range / M1.Price_range < 1.618:
                    # ※ m1 may be the first leg of a zig-zag
                    M1.Structure_list_label.append(':5')
                    M1.EW_structure.append('3d:wave1 of zig-zag')

                if M_1 is not None:
                    if M_1.Price_range / M0.Price_range >= 0.618 and M_1.Price_range / M0.Price_range <= 1.618 \
                            and not self.wave_is_retraced_slower(M2, M3):
                        # ※ m1 may be the second-to-last leg of a triangle
                        M1.Structure_list_label.append('(:sL3)')
                        M1.EW_structure.append('3d:SL of triangle')
                else:
                    # ※ m1 may be the second-to-last leg of a triangle
                    M1.Structure_list_label.append('(:sL3)')
                    M1.EW_structure.append('3d:SL of triangle')

                if not self.wave_is_retraced_slower(M2, M3):
                    # ※ m1 may be the center section of a c-failure flat
                    M1.Structure_list_label.append(':c3')
                    M1.EW_structure.append('3d:center section of c-failure flat')

            elif M3.Price_range / M2.Price_range >= 1.618:
                if M_1 is not None and (
                        M_1.Price_range / M0.Price_range < 0.618 or M_1.Price_range / M0.Price_range > 1.618):
                    # ※ m1 may be the center section of a c-failure flat
                    M1.Structure_list_label.append(':c3')
                    M1.EW_structure.append('3d:center section of c-failure flat')

                if M_3 is not None:
                    if M_1.Price_range / M0.Price_range >= 0.618 and M_1.Price_range / M0.Price_range <= 1.618:
                        temp_Price = self.waves_price_coverage([M_3, M_2, M_1, M0])
                        if M1.Price_range / temp_Price > 0.382:
                            if M1.Price_range / temp_Price < 0.618:
                                # ※ m1 may be the second-to-last leg of a contracting triangle
                                M1.Structure_list_label.append('(:sL3)')
                                M1.EW_structure.append('3d:SL of contracting triangle')
                            else:
                                # ※ m1 may be the second-to-last leg of a contracting triangle
                                M1.Structure_list_label.append(':sL3')
                                M1.EW_structure.append('3d:SL of contracting triangle')
                else:
                    # ※ m1 may be the second-to-last leg of a contracting triangle
                    M1.Structure_list_label.append(':sL3')
                    M1.EW_structure.append('3d:SL of contracting triangle')

                if M4 is not None and M0 is not None and M4.Price_range / M0.Price_range < 0.618:
                    # ※ m1 may be the first leg of a zig-zag
                    M1.Structure_list_label.append('(:5)')
                    M1.EW_structure.append('3d:wave1 of zig-zag')
                else:
                    # ※ m1 may be the first leg of a zig-zag
                    M1.Structure_list_label.append(':5')
                    M1.EW_structure.append('3d:wave1 of zig-zag')


            elif M3.Price_range / M2.Price_range >= 1:
                if M4 is None or (M4 is not None and M4.Price_range < M3.Price_range):
                    # ※ m1 may be a leg in a triangle
                    M1.Structure_list_label.append('(:c3)')
                    M1.EW_structure.append('3d:triangle')
                    M1.Structure_list_label.append('[:F3]')
                    M1.EW_structure.append('3d:triangle')

                if M4 is None or (M4 is not None and M4.Price_range > M3.Price_range) or \
                        M5 is None or (M5 is not None and not self.wave_is_retraced(M4, M5)) or \
                        wave_is_steeper(M1.Price_range, M1.Duration, M5):
                    # ※ m1 is probably the first leg a zig-zag
                    M1.Structure_list_label.append(':5')
                    M1.EW_structure.append('3d:first of zig-zag')

        hyper_monowaves[idx] = M1

    def EW_R3e(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M0 = hyper_monowaves[idx - 1] if (idx - 1 >= 0) else None
        M_1 = hyper_monowaves[idx - 2] if (idx - 2 >= 0) else None
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None
        M4 = hyper_monowaves[idx + 3] if (idx + 3 < n) else None

        if M3 is not None:
            if M3.Price_range / M2.Price_range > 2.618:
                if not self.wave_is_retraced_slower(M2, M3):
                    if M_1 is None or (0.618 < (M_1.Price_range / M0.Price_range) < 1.618):
                        # ※ m1 may be the second-to-last leg of a triangle
                        M1.Structure_list_label.append('(:sL3)')
                        M1.EW_structure.append('3e:SL of triangle')

                    # ※ m1 may be the center section of a c-failure flat which concludes a complex correction with a missing x-wave in the middle of m0
                    M1.Structure_list_label.append(':c3')
                    M1.EW_structure.append('3e:center section of a c-failure flat')
                if M3.Price_range / M1.Price_range < 1.618:
                    # ※ m1 may be the first leg of a zig-zag
                    M1.Structure_list_label.append(':5')
                    M1.EW_structure.append('3e:wave1 of zigzag')

            elif M3.Price_range / M2.Price_range >= 1.618:
                if M3.Price_range / M1.Price_range < 1.618:
                    # ※ m1 may be the first leg of a zig-zag
                    M1.Structure_list_label.append(':5')
                    M1.EW_structure.append('3e:wave-a of zigzag')
                if not self.wave_is_retraced_slower(M2, M3):
                    # ※ m1 may be the center section of a c-failure flat which concludes a complex correction with a missing x-wave in the middle of m0
                    M1.Structure_list_label.append(':c3')
                    M1.EW_structure.append('3e:center section of a c-failure flat')
                    M0.Structure_list_label.append(':?H:?')
                    M0.EW_structure.append('3e:missing x-wave')

            elif M3.Price_range / M2.Price_range >= 1:
                # ※ m1 may be the first leg of a zig-zag
                M1.Structure_list_label.append(':5')
                M1.EW_structure.append('3e:wave1 of zigzag')
                # ※ m1 may be the first leg of a triangle
                M1.Structure_list_label.append('(:F3)')
                M1.EW_structure.append('3e:wave1 of triangle')
                if M4 is None or (M4.Num_sub_monowave > 1 or M4.Price_range <= M3.Price_range):
                    # ※ m1 may be the first leg of a triangle
                    M1.Structure_list_label.append('(:F3)')
                    M1.EW_structure.append('3e:wave1 of triangle')

        if (idx - 1 >= 0): hyper_monowaves[idx - 1] = M0
        hyper_monowaves[idx] = M1

    def EW_R3f(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M0 = hyper_monowaves[idx - 1] if (idx - 1 >= 0) else None
        M_1 = hyper_monowaves[idx - 2] if (idx - 2 >= 0) else None
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None
        M4 = hyper_monowaves[idx + 3] if (idx + 3 < n) else None

        if M3 is not None:
            if M3.Price_range / M2.Price_range > 2.618:
                if M3.Price_range / M1.Price_range <= 1.618:
                    # ※ m1 may be the first leg of a zig-zag
                    M1.Structure_list_label.append(':5')
                    M1.EW_structure.append('3f:wave-a of zigzag')
                if not self.wave_is_retraced_slower(M2, M3):
                    # ※ m1 may be the center section of a c-failure flat which concludes a complex correction with a missing x-wave in the middle of m0
                    M1.Structure_list_label.append('(:c3)')
                    M1.EW_structure.append('3f:center section of a c-failure flat')
                    # TODO check M1
                    # ///////////////////////
                    if M_1 is None or not wave_overlap(M1, M_1):
                        M0.Structure_list_label.append(':?H:?')
                        M0.EW_structure.append('3f:missing x-wave')

            elif M3.Price_range / M2.Price_range >= 1.618:
                if M3.Price_range < M2.Price_range and not self.wave_is_retraced_slower(M2, M3):
                    # ※ m1 may be the center section of a c-failure flat which concludes a complex correction with a missing x-wave in the middle of m0
                    M1.Structure_list_label.append('(:c3)')
                    M1.EW_structure.append('3f:center section of a c-failure flat')
                    # TODO check M1
                    # ///////////////////////
                    if M_1 is None or (M_1 is not None and not wave_overlap(M1, M_1)):
                        M0.Structure_list_label.append(':?H:?')
                        M0.EW_structure.append('3f:Hidden')

                if M3.Price_range / M1.Price_range < 1.618:
                    # ※ m1 may be the first leg of a zig-zag
                    M1.Structure_list_label.append(':5')
                    M1.EW_structure.append('3f:wave-a of zigzag')

            elif M3.Price_range / M2.Price_range >= 1:
                # ※ m1 may be the first leg of a zig-zag
                M1.Structure_list_label.append(':5')
                M1.EW_structure.append('3f:wave-a of zigzag')
                if M4 is None or (M4 is not None and M4.Num_sub_monowave > 1 or M4.Price_range <= M3.Price_range):
                    # ※ m1 may be the first leg of a triangle
                    M1.Structure_list_label.append('(:F3)')
                    M1.EW_structure.append('3f:wave-a of triangle')

        if (idx - 1 >= 0): hyper_monowaves[idx - 1] = M0
        hyper_monowaves[idx] = M1

    def EW_R4a(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M0 = hyper_monowaves[idx - 1] if (idx - 1 >= 0) else None
        M_1 = hyper_monowaves[idx - 2] if (idx - 2 >= 0) else None
        M_2 = hyper_monowaves[idx - 3] if (idx - 3 >= 0) else None
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None
        M4 = hyper_monowaves[idx + 3] if (idx + 3 < n) else None

        # Category iii
        if M3 is not None:
            if M3.Price_range / M2.Price_range > 2.618:
                if M_1 is not None and M_1.Price_range / M1.Price_range > 2.618:
                    # ※ There is virtually no chance m1 is the end of any Elliott formation
                    M1.Structure_list_label.append(':F3')
                    M1.EW_structure.append('4a:-')
                if M4 is not None:
                    if M4.Price_range / M3.Price_range >= 1:
                        # ※ It is extremely unlikely m1 is the end of any Elliott pattern
                        M1.Structure_list_label.append(':F3')
                        M1.EW_structure.append('4a:-')
                    else:
                        # ※ It is extremely unlikely m1 is the beginning of any Elliott pattern
                        M1.Structure_list_label.append(':s5')
                        M1.EW_structure.append('4a:-')

            # Category ii
            elif M3.Price_range / M2.Price_range >= 1.618:
                if M_1 is not None and M_1.Price_range / M1.Price_range > 2.618:
                    # ※ There is virtually no chance m1 is the end of any Elliott formation
                    M1.Structure_list_label.append(':F3')
                    M1.EW_structure.append('4a:-')
                if M4 is not None:
                    if M4.Price_range > M3.Price_range:
                        # ※ It is extremely unlikely m1 is the end of any Elliott pattern
                        M1.Structure_list_label.append(':F3')
                        M1.EW_structure.append('4a:-')
                    else:
                        if M2.Price_range / M1.Price_range > 0.7:
                            if wave_overlap(M0, M2) and self.wave_is_retraced(M3, M4):
                                # ※ m1 may be 3 of a 5x terminal Impulse pattern
                                M1.Structure_list_label.append(':s5')
                                M1.EW_structure.append('4a:wave3 of 5x terminal Impulse')
                            else:
                                # ※ It is most likely m1 terminated a Zigzag
                                M1.Structure_list_label.append(':s5')
                                M1.EW_structure.append('4a:wave-c of Zigzag')

                        else:
                            if M_1 is not None:
                                if M1.Price_range / M_1.Price_range > 2.618:
                                    # ※ The complex corrective scenario is the only proper choice
                                    M1.Structure_list_label.append(':s5')
                                    M1.EW_structure.append('4a:complex corrective')
                                elif M1.Price_range / M_1.Price_range >= 1.618:
                                    # ※ It becomes more likely that m1 is the end of a Zigzag inside of a complex correction with m2 the end of an x-wave;
                                    # But the 3rd wave idea is still possible as long as you identify the 3rd wave as part of a Double Extension Impulse pattern
                                    # with the 5th wave the longest
                                    M1.Structure_list_label.append(':s5')
                                    M1.EW_structure.append('4a:wave-c of Zigzag inside of a complex correction')
                                    M2.Structure_list_label.append('x.c3')
                                    M2.EW_structure.append('4a:x-wave')
                                elif M1.Price_range / M_1.Price_range >= 1:
                                    if M_2.Price_range > M_1.Price_range:
                                        if wave_overlap(M0, M2):
                                            # ※ m1 may conclude the 3 of a terminal 5x impulse pattern
                                            M1.Structure_list_label.append(':s5')
                                            M1.EW_structure.append('4a:wave3 of terminal 5x Impulse')
                                        else:
                                            # ※ m1 may conclude the 3 of a trending 5x impulse pattern
                                            M1.Structure_list_label.append(':s5')
                                            M1.EW_structure.append('4a:wave3 of trending 5x Impulse')
                                else:
                                    # ※ m1 can only be part of a Zigzag
                                    M1.Structure_list_label.append(':s5')
                                    M1.EW_structure.append('4a:wave-c of Zigzag')

                                    # Category i:
            elif M3.Price_range / M2.Price_range >= 1:
                if M4 is not None:
                    # //TODO CHECK
                    # //////////////
                    if self.wave_is_retraced_slower(M3, M4):
                        # ※ m1 should be the first leg of a correction which follows an x-wave(m0)
                        # ※ If :F3 is chosen, m1 is wave-a of a Flat
                        M1.Structure_list_label.append(':F3')
                        M1.EW_structure.append('4a:wave-a of Flat')
                        M0.Structure_list_label.append('x.c3')
                        M0.EW_structure.append('4a:x-wave')
                        if M_1 is None or (M_1 is not None and M1.Price_range / M_1.Price_range > 0.618) \
                                or (M_1 is not None and M0.Price_range > min(M_1.Price_range, M1.Price_range)):
                            # ※ m1 should be end of a corrective phase which is part of a larger formation
                            # ※ If :s5 is appropriate, m1 is the end of a Zigzag
                            M1.Structure_list_label.append(':s5')
                            M1.EW_structure.append('4a:wave-c of Zigzag')
                    elif self.wave_is_retraced(M3, M4):
                        # ※ There is virtually no chance m1 completed an Elliott pattern
                        # ※ If :F3 is used, m1 would be wave-a of a correction within a larger complex formation, and m0 would be an x-wave
                        M1.Structure_list_label.append(':F3')
                        M1.EW_structure.append('4a:wave-a of a correction within a larger complex formation')
                        M0.Structure_list_label.append('x.c3')
                        M0.EW_structure.append('4a:x-wave')
                        if wave_overlap(M0, M2):
                            # ※ If :c3 is still a possibility, m1 may be part of an Expanding Triangle or a Terminal Impulse pattern
                            M1.Structure_list_label.append(':c3')
                            M1.EW_structure.append('4a:part of an Expanding Triangle or Terminal Impulse')
                        if M_1 is not None and M2.Price_range / M1.Price_range <= 0.7 and not wave_overlap(M0, M2) \
                                and waves_are_fib_related(M3.Price_range, M1.Price_range, 1.618, True) \
                                and (M0.Duration > M_1.Duration or M0.Duration > M1.Duration):
                            # ※ If :s5 is a possibility, m1 would be 3 of a 5th Extension Impulse pattern
                            M1.Structure_list_label.append(':s5')
                            M1.EW_structure.append('4a:wave3 of 5x Impulse')
                    # /////////////
                    else:
                        # //TODO CHECK
                        # //////////////
                        # ※ If :F3 is chosen, m1 is wave-a of a Flat or Triangle
                        M1.Structure_list_label.append(':F3')
                        M1.EW_structure.append('4a:wave-a of a Flat or Triangle')
                        if M_2 is not None and M2.Num_sub_monowave >= 3 and self.wave_is_retraced(M2, M3) \
                                and M2.Duration > M1.Duration and self.wave_breaking_trend(M_2.End_candle_index,
                                                                                           M0.End_candle_index,
                                                                                           M1.End_candle_index,
                                                                                           M2.End_candle_index):
                            # ※ m1 may be the end of a Zigzag within an Irregular or Running Correction
                            M1.Structure_list_label.append(':L5')
                            M1.EW_structure.append('4a:wave-c of Zigzag within an Irregular or Running Correction')

                        if M_1 is not None and M0.Price_range > min(M_1.Price_range, M1.Price_range):
                            # ※ If :s5 is appropriate, m1 is the end of a Zigzag
                            M1.Structure_list_label.append(':s5')
                            M1.EW_structure.append('4a:wave-c of a Zigzag')
                    # ////////////////////
        if (idx - 1 >= 0): hyper_monowaves[idx - 1] = M0
        hyper_monowaves[idx] = M1
        if (idx + 1 >= 0): hyper_monowaves[idx + 1] = M2

    def EW_R4b(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M0 = hyper_monowaves[idx - 1] if (idx - 1 >= 0) else None
        M_1 = hyper_monowaves[idx - 2] if (idx - 2 >= 0) else None
        M_2 = hyper_monowaves[idx - 3] if (idx - 3 >= 0) else None
        M_3 = hyper_monowaves[idx - 4] if (idx - 4 >= 0) else None
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None
        M4 = hyper_monowaves[idx + 3] if (idx + 3 < n) else None
        M5 = hyper_monowaves[idx + 4] if (idx + 4 < n) else None
        M6 = hyper_monowaves[idx + 5] if (idx + 5 < n) else None

        sw = 0

        if M3 is not None:
            # Category iii
            if M3.Price_range / M2.Price_range > 2.618:
                if M_1 is not None:
                    if M_1.Price_range / M1.Price_range > 2.618:
                        # ※ There is virtually no chance m1 is the end of any Elliott formation
                        M1.Structure_list_label.append('(:F3)')
                        M1.EW_structure.append('4b:-')
                        sw = 1
                        if self.wave_formation_beyond(M1, M2):
                            M1.Structure_list_label.append('x.c3')
                            M1.EW_structure.append('4b:-')
                        else:
                            M1.Structure_list_label.append(':c3')
                            M1.EW_structure.append('4b:-')

                    elif M_1.Price_range / M1.Price_range >= 1.618:
                        if self.wave_is_retraced_slower(M0, M1):
                            if M1.Duration / M0.Duration >= 1.618:
                                # ※ It is almost certain m0-m2 form an Irregular Failure Flat
                                M1.Structure_list_label.append('(:F3)')
                                M1.EW_structure.append('4b:m0-m2 form an Irregular Failure Flat')
                                sw = 1
                                if self.wave_formation_beyond(M1, M2):
                                    M1.Structure_list_label.append('x.c3')
                                    M1.EW_structure.append('4b:-')
                                else:
                                    M1.Structure_list_label.append(':c3')
                                    M1.EW_structure.append('4b:-')
                    if M_3 is not None and M1.Price_range > max(M_1.Price_range, M_3.Price_range) \
                            and self.wave_breaking_trend(M_2.End_candle_index, M0.End_candle_index, M1.End_candle_index,
                                                         M2.End_candle_index):
                        # ※ m1 may be the 5 of a 5x impulse pattern
                        M1.Structure_list_label.append('[:L5]')
                        M1.EW_structure.append('4b:wave5 of 5x impulse')
                        sw = 1
                if M4 is not None and M4.Price_range / M3.Price_range < 0.618:
                    # ※ It is extremely unlikely m1 is the beginning of any Elliott pattern
                    # ※ An elongated flat begins with the start of m1
                    M1.Structure_list_label.append(':F3')
                    M1.EW_structure.append('4b:wave-a of elongated flat')
                    sw = 1
                    if M_3 is not None and M1.Price_range > max(M_1.Price_range, M_3.Price_range) \
                            and self.wave_breaking_trend(M_2.End_candle_index, M0.End_candle_index, M1.End_candle_index,
                                                         M2.End_candle_index):
                        # ※ m1 may be the 5 of a 5x impulse pattern
                        M1.Structure_list_label.append('[:L5]')
                        M1.EW_structure.append('4b:wave5 of 5x impulse')

                    if M_1 is not None and M0.Price_range > min(M_1.Price_range, M1.Price_range):
                        # ※ It is extremely unlikely m1 is the beginning of any Elliott pattern
                        M1.Structure_list_label.append('(:s5)')
                        M1.EW_structure.append('4b:-')

                    if self.wave_formation_beyond(M1, M2):
                        M1.Structure_list_label.append('x.c3')
                        M1.EW_structure.append('4b:-')
                    else:
                        # ※ It is extremely unlikely m1 is the beginning of any Elliott pattern
                        M1.Structure_list_label.append(':c3')
                        M1.EW_structure.append('4b:-')

                    if sw == 0:
                        if (M4 is None) or (M4.Price_range / M3.Price_range > 0.618):
                            M1.Structure_list_label.append(':F3')
                            M1.EW_structure.append('4b:-')
                        if (M_1 is None) or ((M0.Price_range > min(M_1.Price_range, M1.Price_range) and
                                              M1.Price_range / M_1.Price_range > 0.618)):
                            M1.Structure_list_label.append(':s5')
                            M1.EW_structure.append('4b:-')
                        if self.wave_formation_beyond(M1, M2):
                            M1.Structure_list_label.append('x.c3')
                            M1.EW_structure.append('4b:-')
                        else:
                            M1.Structure_list_label.append(':c3')
                            M1.EW_structure.append('4b:-')

                        M1.Structure_list_label.append(':sL3')
                        M1.EW_structure.append('4b:-')

                        if M_3 is not None and M1.Price_range > max(M_1.Price_range, M_3.Price_range) \
                                and self.wave_breaking_trend(M_2.End_candle_index, M0.End_candle_index,
                                                             M1.End_candle_index, M2.End_candle_index):
                            # ※ m1 may be the 5 of a 5x impulse pattern
                            M1.Structure_list_label.append('[:L5]')
                            M1.EW_structure.append('4b:wave5 of 5x impulse')

            # Category ii
            elif M3.Price_range / M2.Price_range >= 1.618:
                sw = 0
                if M_1 is not None:
                    if M_1.Price_range / M1.Price_range > 2.618:
                        # ※ There is virtually no chance m1 is the end of any Elliott formation
                        M1.Structure_list_label.append(':F3')
                        M1.EW_structure.append('4b:-')
                        sw = 1
                        if self.wave_formation_beyond(M1, M2):
                            M1.Structure_list_label.append('x.c3')
                            M1.EW_structure.append('4b:-')
                        else:
                            M1.Structure_list_label.append(':c3')
                            M1.EW_structure.append('4b:-')
                    if M_3 is not None and M1.Price_range > max(M_1.Price_range, M_3.Price_range) \
                            and self.wave_breaking_trend(M_2.End_candle_index, M0.End_candle_index, M1.End_candle_index,
                                                         M2.End_candle_index):
                        # ※ m1 may be the 5 of a 5x impulse pattern
                        M1.Structure_list_label.append('[:L5]')
                        M1.EW_structure.append('4b:wave5 of 5x impulse')
                        sw = 1
                if M4 is not None and M4.Price_range / M3.Price_range < 0.618:
                    # ※ It is extremely unlikely m1 is the beginning of any Elliott pattern
                    sw = 1  # since at least one label used
                    if (M5 is None) or ((abs(M5.End_price - M3.Start_price) / M1.Price_range > 1.618)
                                        and not self.wave_is_retraced_slower(M2, M3)):
                        # ※ If :sL3 is used, the Triangle (which concludes with m2) is Non-Limiting
                        # //TODO//////////////////
                        M1.Structure_list_label.append('(:sL3)')
                        M1.EW_structure.append('4b:Non-Limiting triangle')
                    if (M_1 is None) or (M0.Duration > min(M_1.Duration, M1.Duration)):
                        M1.Structure_list_label.append('(:s5)')
                        M1.EW_structure.append('4b:-')
                    if self.wave_formation_beyond(M1, M2):
                        M1.Structure_list_label.append('x.c3')
                        M1.EW_structure.append('4b:-')
                    else:
                        M1.Structure_list_label.append(':c3')
                        M1.EW_structure.append('4b:-')
                if sw == 0:
                    if (M4 is None) or (M4.Price_range / M3.Price_range > 0.618):
                        M1.Structure_list_label.append(':F3')
                        M1.EW_structure.append('4b:-')
                        if (M_1 is None) or ((M0.Price_range > min(M_1.Price_range, M1.Price_range)
                                              and M1.Price_range / M_1.Price_range > 0.618)):
                            M1.Structure_list_label.append(':s5')
                            M1.EW_structure.append('4b:-')
                        if ((M_1 is None) or (M1.Price_range > min(M_1.Price_range, M3.Price_range))
                                and M4 is not None and self.wave_is_retraced(M3, M4)):
                            M1.Structure_list_label.append(':c3')
                            M1.EW_structure.append('4b:-')
                        if self.wave_formation_beyond(M1, M2):
                            M1.Structure_list_label.append('x.c3')
                            M1.EW_structure.append('4b:-')
                        if not self.wave_is_retraced_slower(M2, M3):
                            M1.Structure_list_label.append(':sL3')
                            M1.EW_structure.append('4b:-')
                        if M_3 is not None and M1.Price_range > max(M_1.Price_range, M_3.Price_range) \
                                and self.wave_breaking_trend(M_2.End_candle_index, M0.End_candle_index,
                                                             M1.End_candle_index, M2.End_candle_index):
                            # ※ m1 may be the 5 of a 5x impulse pattern
                            M1.Structure_list_label.append('[:L5]')
                            M1.EW_structure.append('4b:wave5 of 5x impulse')

            # Category i
            elif M3.Price_range / M2.Price_range >= 1:
                if M4 is not None:
                    if self.wave_is_retraced(M3, M4):
                        # ※ There is virtually no chance m1 is the end of any Elliott formation
                        M1.Structure_list_label.append(':F3')
                        M1.EW_structure.append('4b:-')
                        # ※ If :c3 is the preferred choice, m1 may be part of a Terminal Impulse pattern
                        M1.Structure_list_label.append(':c3')
                        M1.EW_structure.append('4b:part of a Terminal Impulse')
                        # TODO If the end of m3 is exceeded before the end of m0
                        if M_3 is not None and M1.Price_range > max(M_1.Price_range, M_3.Price_range) \
                                and self.wave_breaking_trend(M_2.End_candle_index, M0.End_candle_index,
                                                             M1.End_candle_index, M2.End_candle_index):
                            # ※ m1 may be the 5 of a 5x impulse pattern
                            M1.Structure_list_label.append('[:L5]')
                            M1.EW_structure.append('4b:wave5 of 5x Impulse')

                    if self.wave_is_retraced_slower(M3, M4):
                        if (M_1 is None) or (
                                M_1.Price_range / M1.Price_range < 1.618 or M4.Price_range / M3.Price_range >= 0.618):
                            M1.Structure_list_label.append(':F3')
                            M1.EW_structure.append('4b:-')
                        if (M_1 is None) or (
                                M1.Price_range / M_1.Price_range > 0.618 and M0.Duration > min(M_1.Duration,
                                                                                               M1.Duration)):
                            M1.Structure_list_label.append(':s5')
                            M1.EW_structure.append('4b:-')
                        if self.wave_formation_beyond(M1, M2):
                            M1.Structure_list_label.append('x.c3')
                            M1.EW_structure.append('4b:-')
                        else:
                            M1.Structure_list_label.append(':c3')
                            M1.EW_structure.append('4b:-')

                        # TODO If the end of m3 is exceeded before the end of m0
                        if M_3 is not None and M1.Price_range > max(M_1.Price_range, M_3.Price_range) \
                                and self.wave_breaking_trend(M_2.End_candle_index, M0.End_candle_index,
                                                             M1.End_candle_index, M2.End_candle_index):
                            # ※ m1 may be the 5 of a 5x impulse pattern
                            M1.Structure_list_label.append('[:L5]')
                            M1.EW_structure.append('4b:wave5 of 5x Impulse')

                    if M4.Price_range / M3.Price_range < 1:
                        # ※ It is extremely unlikely m1 is the beginning of any Elliott pattern

                        if self.wave_formation_beyond(M2, M1):
                            M1.Structure_list_label.append('x.c3')
                            M1.EW_structure.append('4b:-')
                        elif M_2 is not None and M_2.Price_range < M_1.Price_range:
                            if (M6 is None) or self.wave_is_retraced(M5, M6):
                                M1.Structure_list_label.append(':c3')
                                M1.EW_structure.append('4b:-')
                                # ※ If :c3 is still a possibility, m1 may be the x-wave of a Complex Correction
                                M1.Structure_list_label.append('x.c3?')
                                M1.EW_structure.append('4b:x-wave of Complex Correction')

                        if (M_1 is None) or (M0.Price_range > min(M_1.Price_range, M1.Price_range)):
                            M1.Structure_list_label.append(':s5')
                            M1.EW_structure.append('4b:-')

                        if M_2 is not None and M2.Num_sub_monowave >= 3 and self.wave_is_retraced(M2, M3) \
                                and M2.Duration > M1.Duration and M_1.Price_range / M0.Price_range >= 1.618 \
                                and self.wave_breaking_trend(M_2.End_candle_index, M0.End_candle_index,
                                                             M1.End_candle_index, M2.End_candle_index):
                            # ※ m1 may be the end of a Zigzag within an Irregular or Running Correction
                            M1.Structure_list_label.append(':L5')
                            M1.EW_structure.append('4b:wave-c of Zigzag within an Irregular or Running Correction')
                    if M4.Price_range / M3.Price_range < 0.618:
                        # ※ It is extremely unlikely m1 is the beginning of any Elliott pattern
                        if self.wave_formation_beyond(M1, M2):
                            M1.Structure_list_label.append('x.c3')
                            M1.EW_structure.append('4b:-')
                        elif M_2 is not None and M_2.Price_range < M_1.Price_range:
                            M1.Structure_list_label.append(':c3')
                            M1.EW_structure.append('4b:-')
                            # ※ If :c3 is still a possibility, m1 may be the x-wave of a Complex Correction
                            M1.Structure_list_label.append('x.c3?')
                            M1.EW_structure.append('4b:Complex Correction')

                        if ((M5 is None) or abs(M5.End_price - M3.Start_price) / M1.Price_range > 1.618) \
                                and self.wave_is_retraced(M2, M3):
                            M1.Structure_list_label.append(':sL3')
                            M1.EW_structure.append('4b:-')
                        if (M_1 is None) or M0.Duration > min(M_1.Duration, M1.Duration):
                            M1.Structure_list_label.append(':s5')
                            M1.EW_structure.append('4b:-')
                        if M_3 is not None and M1.Price_range > max(M_1.Price_range, M_3.Price_range) \
                                and self.wave_breaking_trend(M_2.End_candle_index, M0.End_candle_index,
                                                             M1.End_candle_index, M2.End_candle_index):
                            # ※ m1 may be the 5 of a 5x impulse pattern
                            M1.Structure_list_label.append('[:L5]')
                            M1.EW_structure.append('4b:wave5 of 5x Impulse')

        hyper_monowaves[idx] = M1

    def EW_R4c(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None
        M4 = hyper_monowaves[idx + 3] if (idx + 3 < n) else None

        if M3 is not None:
            # Category iii
            if M3.Price_range / M2.Price_range > 2.618:
                if self.wave_is_retraced(M2, M3):
                    # ※ It is almost certain m1 is the center section of a c-Failure Flat or a Non-Limiting Contracting Triangle
                    if self.wave_formation_beyond(M1, M2):
                        M1.Structure_list_label.append('x.c3')
                        M1.EW_structure.append('4c:-')
                    else:
                        M1.Structure_list_label.append(':c3')
                        M1.EW_structure.append(
                            '4c:center section of a c-Failure Flat or a Non-Limiting Contracting Triangle')
                    if M4 is not None and self.wave_is_retraced(M3, M4, retraced_ratio=0.618):
                        # ※ The only way [:F3] should be considered is if m3 is retraced more than 61.8% within a period of time equal to or less than m3
                        M1.Structure_list_label.append('[:F3]')
                        M1.EW_structure.append('4c:-')
            # Category ii
            elif M3.Price_range / M2.Price_range >= 1.618:
                if self.wave_is_retraced(M2, M3) and M3.Price_range / M1.Price_range > 1.618:
                    if self.wave_formation_beyond(M1, M2):
                        M1.Structure_list_label.append('x.c3')
                        M1.EW_structure.append('4c:-')
                    else:
                        # ※ The chances are better that m1 was the center section of a c-Failure Flat or of a Contracting Triangle
                        M1.Structure_list_label.append(':c3')
                        M1.EW_structure.append('4c:center section of a c-Failure Flat or of a Contracting Triangle')
                    # ※ If the lower probability (:F3) is correct, m1 is part of an Elongated Flat
                    M1.Structure_list_label.append('(:F3)')
                    M1.EW_structure.append('4c:Elongated Flat')
                else:
                    M1.Structure_list_label.append(':F3')
                    M1.EW_structure.append('4c:-')
                    M1.Structure_list_label.append(':c3')
                    M1.EW_structure.append('4c:-')
                    M1.Structure_list_label.append('x.c3')
                    M1.EW_structure.append('4c:-')
            # Category i
            elif M3.Price_range / M2.Price_range >= 1:
                M1.Structure_list_label.append(':F3')
                M1.EW_structure.append('4c:-')

                if self.wave_formation_beyond(M1, M2):
                    M1.Structure_list_label.append('x.c3')
                    M1.EW_structure.append('4c:-')
                else:
                    M1.Structure_list_label.append(':c3')
                    M1.EW_structure.append('4c:-')

        hyper_monowaves[idx] = M1

    def EW_R4d(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M0 = hyper_monowaves[idx - 1] if (idx - 1 >= 0) else None
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None
        M4 = hyper_monowaves[idx + 3] if (idx + 3 < n) else None
        M5 = hyper_monowaves[idx + 4] if (idx + 4 < n) else None
        M6 = hyper_monowaves[idx + 5] if (idx + 5 < n) else None

        sw = 0

        if M3 is not None:
            # Category iii
            if M3.Price_range / M2.Price_range > 2.618:
                if M3.Duration <= M1.Duration and self.wave_is_retraced(M2, M3):
                    # ※ There is a strong possibility of a missing x-wave hidden toward the middle of m0
                    if self.wave_formation_beyond(M1, M2):
                        M1.Structure_list_label.append('x.c3')
                        M1.EW_structure.append('4d:-')
                    else:
                        M1.Structure_list_label.append(':c3')
                        M1.EW_structure.append('4d:-')
                        M0.Structure_list_label.append(':?H:?')
                        M0.EW_structure.append('4d:Hidden')
                if M4 is not None and M4.Price_range / M3.Price_range >= 0.618:
                    # ※ It is possible m1 is the first leg of a Flat
                    M1.Structure_list_label.append(':F3')
                    M1.EW_structure.append('4d:wave1 of Flat')
                if M3.Duration > M1.Duration:
                    M1.Structure_list_label.append(':F3')
                    M1.EW_structure.append('4d:-')
                    if self.wave_formation_beyond(M1, M2):
                        M1.Structure_list_label.append('x.c3')
                        M1.EW_structure.append('4d:-')
                    else:
                        M1.Structure_list_label.append(':c3')
                        M1.EW_structure.append('4d:-')

            # Category ii , i
            elif M3.Price_range / M2.Price_range >= 1:
                if M4 is not None and self.wave_is_retraced(M2, M3) \
                        and M4.Price_range / M3.Price_range <= 0.618:
                    flag1 = False
                    if wave_is_steeper(M3.Price_range, M3.Duration, M1, 1.618):
                        flag1 = True
                    elif M5 is not None and wave_is_steeper(abs(M5.End_price - M3.Start_price),
                                                            (M5.End_candle_index - M3.Start_candle_index), M1, 1.618):
                        flag1 = True
                    if (flag1):
                        # ※ m1 may be part of a Complex Correction where the x-wave is hidden in m0
                        M1.Structure_list_label.append(':F3')
                        M1.EW_structure.append('4d:Complex Correction')
                        M1.Structure_list_label.append('[:c3]')
                        M1.EW_structure.append('4d:Complex Correction')
                        # TODO Hidden
                        M0.Structure_list_label.append(':F3?')
                        M0.EW_structure.append('4d:-')
                        M0.Structure_list_label.append(':?H:?')
                        M0.EW_structure.append('4d:Hidden')
                elif self.wave_is_retraced_slower(M2, M3):
                    # ※ A Flat or Triangle is probably involved
                    if M4 is not None:
                        if self.wave_is_retraced(M3, M4) \
                                or 0.618 <= (M4.Price_range / M3.Price_range) < 1:
                            # ※ :F3 is the only reasonable choice for m1
                            M1.Structure_list_label.append(':F3')
                            M1.EW_structure.append('4d:Flat or Triangle')
                            sw = 1
                        elif (M4.Price_range / M3.Price_range) < 0.618:
                            M1.Structure_list_label.append(':F3')
                            if M5 is not None and M5.Price_range < max(M1.Price_range, M3.Price_range):
                                if M6 is not None and self.wave_is_retraced(M5, M6):
                                    # ※ m1 may be part of a Terminal pattern
                                    M1.EW_structure.append('4d:Terminal')
                                else:
                                    M1.EW_structure.append('4d:-')
                            else:
                                # ※ m1 may be part of a Complex Double Flat where m4 is an x-wave
                                M1.EW_structure.append('4d:Complex Double Flat')

                    if sw == 0:
                        if self.wave_formation_beyond(M1, M2):
                            M1.Structure_list_label.append('x.c3')
                            M1.EW_structure.append('4d:-')
                        else:
                            M1.Structure_list_label.append(':c3')
                            M1.EW_structure.append('4d:Flat or Triangle')

        if (idx - 1 >= 0): hyper_monowaves[idx - 1] = M0
        hyper_monowaves[idx] = M1

    def EW_R4e(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M0 = hyper_monowaves[idx - 1] if (idx - 1 >= 0) else None
        M_1 = hyper_monowaves[idx - 2] if (idx - 2 >= 0) else None
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None
        M4 = hyper_monowaves[idx + 3] if (idx + 3 < n) else None
        M5 = hyper_monowaves[idx + 4] if (idx + 4 < n) else None

        if M3 is not None:
            # Category iii
            if M3.Price_range / M2.Price_range > 2.618:
                if M3.Duration <= M1.Duration and self.wave_is_retraced(M2, M3):
                    # ※ There is a strong possibility of a missing x-wave hidden toward the middle of m0
                    M1.Structure_list_label.append('x.c3')
                    M1.EW_structure.append('4e:-')
                    M0.Structure_list_label.append(':?H:?')
                    M0.EW_structure.append('4e:Hidden')
                if M5 is not None and not self.waves_exceed_start_W1(M0, [M3, M4,
                                                                          M5]) and M4.Price_range / M3.Price_range >= 0.618:
                    # ※ m1 may be the first leg of an Elongated Flat
                    M1.Structure_list_label.append(':F3')
                    M1.EW_structure.append('4e:wave1 of Elongated Flat')

                    # Category ii , i
            elif M3.Price_range / M2.Price_range >= 1:
                if M4 is not None:
                    if self.wave_is_retraced(M3, M4):  # ////////
                        # ※ :F3 is the only reasonable choice
                        M1.Structure_list_label.append(':F3')
                        M1.EW_structure.append('4e:-')
                    if M3.Price_range / M2.Price_range <= 1.618 and M4.Price_range / M3.Price_range < 1 \
                            and self.wave_is_retraced(M3, M4):
                        # ※ m1 could be the x-wave of a Complex Correction
                        M1.Structure_list_label.append('x.c3')
                        M1.EW_structure.append('4e:Complex Correction')
                        if M_1 is not None and M_1.Price_range / M0.Price_range > 0.618:
                            # ※ m0 would be missing an x-wave toward its center
                            M0.Structure_list_label.append(':?H:?')
                            M0.EW_structure.append('4e:Hidden')

                    if M_1 is not None:
                        if self.wave_is_retraced(M2, M3):
                            if M_1.Price_range / M0.Price_range > 0.618 and M4.Price_range / M3.Price_range <= 0.618:
                                if wave_is_steeper(M3.Price_range, M3.Duration, M1) or (
                                        M5 is not None and wave_is_steeper(abs(M5.End_price - M3.Start_price), (
                                        M5.End_candle_index - M3.Start_candle_index), M1)):
                                    # ※ m1 may be part of a Complex Correction where m0 contains a missing x-wave toward its center, or m1 is the x-wave following a Zigzag
                                    M1.Structure_list_label.append(':F3')
                                    M1.EW_structure.append('4e:Complex Correction')
                                    M1.Structure_list_label.append('[:c3]')
                                    M1.EW_structure.append('4e:Complex Correction')
                                    M0.Structure_list_label.append(':?H:?')
                                    M0.EW_structure.append('4e:Hidden')
                                    if self.wave_formation_beyond(M1, M2):
                                        M1.Structure_list_label.append('x.c3')
                                        M1.EW_structure.append('4e:-')
                        elif self.wave_is_retraced_slower(M2, M3):
                            # ※ A Flat or Triangle is probably involved
                            M1.Structure_list_label.append(':F3')
                            M1.EW_structure.append('4e:Flat or Triangle')
                            if M_1.Price_range / M0.Price_range <= 0.618 and M4.Price_range / M3.Price_range <= 0.618:
                                if wave_is_steeper(M3.Price_range, M3.Duration, M1, 1.618) or (
                                        M5 is not None and wave_is_steeper(abs(M5.End_price - M3.Start_price), (
                                        M5.End_candle_index - M3.Start_candle_index), M1, 1.618)):
                                    # ※ m1 may be part of a Complex Correction where m0 contains a missing x-wave toward its center
                                    M1.Structure_list_label.append(':F3')
                                    M1.EW_structure.append('4e:Complex Correction')
                                    M1.Structure_list_label.append('[:c3]')
                                    M1.EW_structure.append('4e:Complex Correction')
                                    M0.Structure_list_label.append(':?H:?')
                                    M0.EW_structure.append('4e:Hidden')
                                    if self.wave_formation_beyond(M1, M2):
                                        M1.Structure_list_label.append('x.c3')
                                        M1.EW_structure.append('4e:-')

                if M0.Num_sub_monowave >= 3 or check_subitem_in_list(M0.Structure_list_label, ':?H:?'):
                    # ※ m1 may be an x-wave of a Complex Correction
                    M1.Structure_list_label.append('x.c3')
                    M1.EW_structure.append('4e:Complex correction')
                if M_1 is not None and M_1.Price_range / M0.Price_range <= 0.618:
                    # ※ m1 may be an x-wave of a Complex Correction
                    M1.Structure_list_label.append('x.c3')
                    M1.EW_structure.append('4e:Complex correction')

        if (idx - 1 >= 0): hyper_monowaves[idx - 1] = M0
        hyper_monowaves[idx] = M1

    def EW_R5a(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M0 = hyper_monowaves[idx - 1] if (idx - 1 >= 0) else None
        M_1 = hyper_monowaves[idx - 2] if (idx - 2 >= 0) else None
        M_2 = hyper_monowaves[idx - 3] if (idx - 3 >= 0) else None
        M_3 = hyper_monowaves[idx - 4] if (idx - 4 >= 0) else None
        M_4 = hyper_monowaves[idx - 5] if (idx - 5 >= 0) else None
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None
        M4 = hyper_monowaves[idx + 3] if (idx + 3 < n) else None

        if M2 is not None:
            if M2.Num_sub_monowave > 3:
                if not self.wave_ret_n_subwaves_fib_ratio(M1, M2):
                    # ※ m1 may be 3 of a 5th Failure Impulse pattern
                    M1.Structure_list_label.append(':5')
                    M1.EW_structure.append('5a:wave3 of a 5th Failure Impulse(Trending or Terminal)')
                    # ※ A complex correction may be unfolding with the first wave of m2 representing an x-wave
                    M1.Structure_list_label.append(':s5')
                    M1.EW_structure.append('5a:complex correction')
                    # ※ m1 contains a missing x-wave or missing b-wave in its center
                    M1.Structure_list_label.append('x.c3')
                    M1.EW_structure.append('5a:missing x-wave or missing b-wave')
                    if self.wave_ret_n_subwaves_fib_ratio(M1, M2, .25):
                        M1.Structure_list_label.append(':F3')
                        M1.EW_structure.append('5a:-')
                else:
                    # ※ m1 may have completed wave-a of a Flat with a complex b-wave
                    M1.Structure_list_label.append(':F3')
                    M1.EW_structure.append('5a:wave-a of a Flat with a complex b-wave')
                    # ※ m1 may be 3 of a 5th failure impulse pattern
                    M1.Structure_list_label.append(':5')
                    M1.EW_structure.append('5a:wave3 of a 5th Failure Impulse')

            else:
                if self.wave_is_retraced(M1, M2):
                    if M_2 is not None:
                        if M2.Price_range < M_2.Price_range:
                            # ※ A Flat or Zigzag may have concluded with m1
                            M1.Structure_list_label.append(':L5')
                            M1.EW_structure.append('5a:Flat or Zigzag')
                        else:
                            if M_3 is not None:
                                if not wave_overlap(M0, M_2) and not self.waves_are_similar(M0.Price_range,
                                                                                            M_2.Price_range) \
                                        and not self.waves_are_similar(M0.Duration, M_2.Duration) \
                                        and self.wave_not_shortest(M_3.Price_range, M_1.Price_range, M1.Price_range):
                                    # ※ A Trending Impulse pattern may have concluded with m1
                                    M1.Structure_list_label.append(':L5')
                                    M1.EW_structure.append('5a:Trending Impulse')

                            if M_4 is not None:
                                if M_4.Price_range > M_3.Price_range:
                                    # ※ A Flat or Zigzag may have concluded with m1
                                    M1.Structure_list_label.append(':L5')
                                    M1.EW_structure.append('5a:Flat or Zigzag')
                                elif M_3.Price_range > M_2.Price_range:
                                    M_2.Structure_list_label.append('x.c3?')
                                    M_2.EW_structure.append('5a:x-wave')
                                    # ※ m1 may be the end of a Standard Elliott pattern which is part of a Complex Correction where mn2 is an x-wave
                                    M1.Structure_list_label.append(':L5')
                                    if M_1.Price_range / M0.Price_range >= 1.618:
                                        # the Standard Correction unfolding is probably a Zigzag
                                        M1.EW_structure.append('5a:end of Elliott-Zigzag')
                                    elif M_1.Price_range / M0.Price_range >= 1:
                                        # the Standard Correction is probably a Flat
                                        M1.EW_structure.append('5a:end of Elliott-Flat')
                                    else:
                                        M1.EW_structure.append('5a:end of Elliott')
                    if M3 is not None:
                        if M3.Price_range / M2.Price_range <= 0.618:
                            if M_3 is not None and M_2.Price_range < M_1.Price_range and self.wave_not_shortest(
                                    M1.Price_range, M_1.Price_range, M_3.Price_range) \
                                    and self.market_goes_beyond_w1_start(M_3, M1.End_candle_index, 0.5 * (
                                    M1.End_candle_index - M_3.Start_candle_index)) \
                                    and not self.market_goes_beyond_w1_end(M1, 4 * (
                                    M1.End_candle_index - M_3.Start_candle_index)) \
                                    and M4 is not None and self.waves_price_coverage([M2, M3, M4]) >= 2 * (
                                    M1.Max_price - M1.Min_price) \
                                    and check_subitem_in_list(M_1.Structure_list_label, ':c3'):
                                # ※ A Terminal Impulse may have completed at the end of m1
                                M1.Structure_list_label.append(':L3')
                                M1.EW_structure.append('5a:Terminal')
                        elif M3.Price_range / M2.Price_range <= 1:
                            # ※ m1 may be part of an Irregular Failure Flat
                            M1.Structure_list_label.append(':F3')
                            M1.EW_structure.append('5a:Irregular Failure Flat')
                        else:
                            if M0.Price_range / M2.Price_range >= 1.618 \
                                    and M4 is not None and self.wave_is_retraced(M3, M4):
                                # ※ m1 may be part of an Irregular Failure Flat
                                M1.Structure_list_label.append(':F3')
                                M1.EW_structure.append('5a:Irregular Failure Flat')

                if self.wave_is_retraced_slower(M1, M2):
                    if M3 is not None and M_1 is not None:
                        if M3.Price_range < M2.Price_range:
                            if (M3.Price_range / abs(M_1.Start_price - M1.End_price)) <= 0.618:
                                # ※ The market may be concluding a Complex Correction in which m1 will be
                                # the most extreme price obtained by the market for a period at least twice that of the combined times of m0-m2
                                M1.Structure_list_label.append(':F3')
                                M1.EW_structure.append('5a:Complex Correction')
                            if M_1.Price_range / M1.Price_range >= 0.618 \
                                    and M4 is not None and self.wave_is_retraced(M3, M4):
                                # ※ m1 may be part of a Flat which concludes a larger pattern
                                M1.Structure_list_label.append(':F3')
                                M1.EW_structure.append('5a:Flat')
                        else:
                            if (M2.Price_range / abs(M_1.Start_price - M1.End_price)) <= 0.618:
                                # ※ The market could be forming a Complex Correction or an Expanding Triangle
                                M1.Structure_list_label.extend([':F3', ':c3', ':L5'])
                                M1.EW_structure.extend(['5a:Complex Correction or an Expanding Triangle'] * 3)

                    if M_2 is not None:
                        if M2.Price_range < M_2.Price_range:
                            # ※ A Zigzag, which is part of a Contracting Triangle, may have concluded with m1
                            M1.Structure_list_label.append(':L5')
                            M1.EW_structure.append('5a:Zigzag(part of a Contracting Triangle)')
                if M4 is not None:
                    if M3.Price_range > M2.Price_range:
                        if M4.Price_range > M3.Price_range:
                            if M0.Price_range / M1.Price_range < 0.618:
                                # ※ m1 may have begun an Expanding Triangle
                                M1.Structure_list_label.append(':F3')
                                M1.EW_structure.append('5a:Expanding Triangle')
                            elif M0.Price_range / M1.Price_range <= 1:
                                # ※ The market may be forming an Expanding Triangle
                                M1.Structure_list_label.append(':c3')
                                M1.EW_structure.append('5a:Expanding Triangle')

        if (idx - 3 >= 0): hyper_monowaves[idx - 3] = M_2
        hyper_monowaves[idx] = M1

    def EW_R5b(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M0 = hyper_monowaves[idx - 1] if (idx - 1 >= 0) else None
        M_1 = hyper_monowaves[idx - 2] if (idx - 2 >= 0) else None
        M_2 = hyper_monowaves[idx - 3] if (idx - 3 >= 0) else None
        M_3 = hyper_monowaves[idx - 4] if (idx - 4 >= 0) else None
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None
        M4 = hyper_monowaves[idx + 3] if (idx + 3 < n) else None
        M5 = hyper_monowaves[idx + 4] if (idx + 4 < n) else None
        sw_have_label = 0
        if M3 is not None:
            if M3.Price_range > M2.Price_range:
                if M0 is not None:
                    if abs(M1.Price_range - M0.Price_range) < abs(1.618 * M1.Price_range - M0.Price_range):
                        M1.Structure_list_label.append(':c3')
                        M1.EW_structure.append('5b:-')
                        sw_have_label = 1
                        if M_1 is not None:
                            M1.Structure_list_label.append('x.c3')
                            if M_1.Price_range > M0.Price_range:
                                # ※ m1 may be the wave-b of a Flat
                                M1.EW_structure.append('5b:wave-b of Flat')
                            else:
                                # ※ m1 may be the x-wave of a Complex Correction
                                M1.EW_structure.append('5b:Complex Correction')
                    else:
                        M1.Structure_list_label.append(':F3')
                        M1.EW_structure.append('5b:-')
                        sw_have_label = 1
                        if M_1 is not None:
                            if M_1.Price_range > M0.Price_range:
                                # ※ m2 is probably the end of a Zigzag
                                M1.Structure_list_label.append('x.c3')
                                M1.EW_structure.append('5b:wave-b of Zigzag')
                            else:
                                # ※ m1 may be an x-wave of a Complex Correction which ends with m4
                                M1.Structure_list_label.append('x.c3')
                                M1.EW_structure.append('5b:Complex Correction')
            elif M3.Price_range / M2.Price_range <= 0.618:
                if M0 is not None and M5 is not None:
                    if wave_overlap(M1, M3) and M4.Price_range / M2.Price_range <= 2.618 \
                            and self.wave_not_shortest(M0.Price_range, M2.Price_range,
                                                       M4.Price_range) and self.wave_is_retraced(M4, M5) \
                            and self.market_goes_beyond_w1_start(M0, M4.End_candle_index,
                                                                 0.5 * (M4.End_candle_index - M0.Start_candle_index)):
                        # ※ The market possibly completed a Terminal pattern at m4
                        M1.Structure_list_label.append(':c3')
                        M1.EW_structure.append('5b:-')
                        sw_have_label = 1

                if self.wave_is_retraced(M1, M2):
                    if M_1 is not None and M4 is not None:
                        if M1.Price_range / M_1.Price_range <= 1.618 \
                                and self.waves_almost_same(M2.Price_range, 1.618 * M1.Price_range) \
                                and self.waves_price_coverage([M2, M3, M4]) > M0.Price_coverage:
                            # ※ m1 may have completed a Flat
                            M1.Structure_list_label.append(':L5')
                            M1.EW_structure.append('5b:Flat')
                            sw_have_label = 1

                        if M_3 is not None:
                            if self.waves_almost_same(M2.Price_range,
                                                      1.618 * M1.Price_range) and M_1.Price_range / M0.Price_range >= 0.618 \
                                    and 0.618 <= M_2.Price_range / M_1.Price_range <= 1.618 \
                                    and 0.618 <= M_3.Price_range / M_2.Price_range <= 1.618 \
                                    and self.waves_price_coverage([M2, M3, M4]) > M0.Price_coverage:
                                # ※ m1 may have completed a Contracting Triangle
                                M1.Structure_list_label.append(':L3')
                                M1.EW_structure.append('5b:Contracting Triangle')
                                sw_have_label = 1

            elif M3.Price_range / M2.Price_range <= 1:
                if not self.wave_formation_beyond(M2, M3) and M3.Price_range / M1.Price_range >= 0.618:
                    M1.Structure_list_label.append(':F3')
                    M1.EW_structure.append('5b:-')
                    sw_have_label = 1

            if M3.Price_range / M1.Price_range >= 0.618 and not self.wave_formation_beyond(M2, M3) \
                    and self.waves_almost_same(M2.Price_range, 0.618 * M0.Price_range):
                sw_have_label = 1
                if check_subitem_in_list(M1.Structure_list_label, ':c3') == 0:
                    # ※ m1 may be the first leg of an Irregular Failure Flat
                    M1.Structure_list_label.append(':F3')
                    M1.EW_structure.append('5b:wave1 of Irregular Failure Flat')
                else:
                    M1.Structure_list_label.append('[:F3]')
                    M1.EW_structure.append('5b:wave1 of Irregular Failure Flat')

            if M_2 is not None and M_1.Price_range < M0.Price_range and self.wave_is_retraced(M2, M3) \
                    and self.wave_not_shortest(M_2.Price_range, M0.Price_range, M2.Price_range) \
                    and self.market_goes_beyond_w1_start(M_2, M2.End_candle_index,
                                                         int(0.5 * (M2.End_candle_index - M_2.Start_candle_index))):
                # ※ A Terminal Impulse pattern could have completed at the end of m2
                M1.Structure_list_label.append(':sL3')
                M1.EW_structure.append('5b:Terminal Impulse')
                sw_have_label = 1

            if M1.Num_sub_monowave == 1 and sw_have_label == 0:
                M1.Structure_list_label.extend([':c3', ':F3', ':L3', ':L5'])
                M1.EW_structure.extend(['-'] * 4)
            elif M1.Num_sub_monowave > 1 and sw_have_label == 0:  # //TODO m1 is a compacted polywave (or higher) pattern, just move on to the section entitled
                # "Implementation of Position Indicators" and use surrounding Structure labels to decide the Position
                # Indicator which belongs in front of m1 's compacted Structure label.
                pass

        hyper_monowaves[idx] = M1

    def EW_R5c(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M0 = hyper_monowaves[idx - 1] if (idx - 1 >= 0) else None
        M_1 = hyper_monowaves[idx - 2] if (idx - 2 >= 0) else None
        M_2 = hyper_monowaves[idx - 3] if (idx - 3 >= 0) else None
        M_3 = hyper_monowaves[idx - 4] if (idx - 4 >= 0) else None
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None
        M4 = hyper_monowaves[idx + 3] if (idx + 3 < n) else None
        M5 = hyper_monowaves[idx + 4] if (idx + 4 < n) else None
        M6 = hyper_monowaves[idx + 5] if (idx + 5 < n) else None
        sw = 0
        if M3 is not None:
            if 1 < M3.Price_range / M2.Price_range <= 1.618:
                # ※ There is the unkikely possibility an Expanding Triangle is forming
                M1.Structure_list_label.append(':c3')
                M1.EW_structure.append('5c:-')
                sw = 1
            if self.wave_is_retraced(M2, M3):
                if M_2 is not None:
                    if M_1.Price_range < M0.Price_range and self.wave_not_shortest(M_2.Price_range, M0.Price_range,
                                                                                   M2.Price_range) \
                            and wave_overlap(M_1, M1) and self.market_goes_beyond_w1_start(M_2, M2.End_candle_index,
                                                                                           int(0.5 * (
                                                                                                   M2.End_candle_index - M_2.Start_candle_index))):
                        # ※ A Terminal Impulse pattern may be concluded with m2
                        M1.Structure_list_label.append(':sL3')
                        M1.EW_structure.append('5c:Terminal pattern ends at m2')
                        sw = 1
            elif M3.Price_range / M2.Price_range <= 0.618:
                if M4 is not None:
                    if M5 is not None and M0 is not None:
                        if wave_overlap(M1, M3) and M4.Price_range < M2.Price_range \
                                and self.wave_is_retraced(M4, M5) \
                                and self.market_goes_beyond_w1_start(M0, M4.End_candle_index, int(
                            0.5 * (M4.End_candle_index - M0.Start_candle_index))):
                            # ※ The market possibly completed a Terminal pattern at m4
                            M1.Structure_list_label.append(':c3')
                            M1.EW_structure.append('5c:Terminal pattern ends at m4')
                            sw = 1
                    if M_1 is not None:
                        if self.wave_is_retraced(M1, M2) \
                                and self.waves_almost_same(M2.Price_range, 1.618 * M1.Price_range) \
                                and self.waves_price_coverage([M2, M3, M4]) > M0.Price_coverage:
                            if self.waves_almost_same(M1.Price_range, 0.618 * M0.Price_range) \
                                    and M1.Price_range / M_1.Price_range <= 1.618:
                                # ※ m1 may have completed a Flat
                                M1.Structure_list_label.append(':L5')
                                M1.EW_structure.append('5c:Flat')
                                sw = 1
                            if M_3 is not None and M_1.Price_range / M0.Price_range >= 0.618 \
                                    and 0.618 <= M_2.Price_range / M_1.Price_range <= 1.618 \
                                    and 0.618 <= M_3.Price_range / M_2.Price_range <= 1.618:
                                # ※ m1 may have completed a Contracting Triangle
                                M1.Structure_list_label.append(':L3')
                                M1.EW_structure.append('5c:Contracting Triangle')
                                sw = 1

            if M6 is not None and M0 is not None:
                if 0.618 <= M3.Price_range / M1.Price_range <= 1.618 \
                        and M2.Price_range / M0.Price_range < 0.618 \
                        and M4.Price_range / M2.Price_range >= 1 \
                        and (
                        M4.Price_range / M0.Price_range >= 1 or (M6.End_price - M4.Start_price) / M0.Price_range >= 1):
                    # ※ m1 may be the first leg of an Irregular Flat (either variation) or a Running Triangle
                    M1.Structure_list_label.append(':F3')
                    M1.EW_structure.append('5c:wave1 of Irregular Flat or Running Triangle')
                    sw = 1
        if sw == 0:
            M1.Structure_list_label.append(':F3')
            M1.EW_structure.append('5c:-')

        hyper_monowaves[idx] = M1

    def EW_R5d(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M0 = hyper_monowaves[idx - 1] if (idx - 1 >= 0) else None
        M_1 = hyper_monowaves[idx - 2] if (idx - 2 >= 0) else None
        M_2 = hyper_monowaves[idx - 3] if (idx - 3 >= 0) else None
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None
        M4 = hyper_monowaves[idx + 3] if (idx + 3 < n) else None
        M5 = hyper_monowaves[idx + 4] if (idx + 4 < n) else None
        M6 = hyper_monowaves[idx + 5] if (idx + 5 < n) else None
        sw = 0
        if M2 is not None and M2.Num_sub_monowave >= 3:
            M1.Structure_list_label.append(':F3')
            M1.EW_structure.append('5d:-')
        if M3 is not None:
            if self.wave_is_retraced(M2, M3) \
                    and M_2 is not None and M_2.Price_range < M0.Price_range \
                    and self.market_goes_beyond_w1_start(M_2, M2.End_candle_index,
                                                         (M2.End_candle_index - M_2.Start_candle_index) // 2):
                # ※ There is the outside possibility of a 3rd Extension Terminal pattern completing with m2
                M1.Structure_list_label.append(':sL3')
                M1.EW_structure.append('5d:3rd Extension Terminal pattern completing with m2')
                sw = 1
            if 0.618 <= M3.Price_range / M2.Price_range <= 1:
                if M4 is not None and M0 is not None and M4.Price_range / M0.Price_range < 0.618:
                        if M1.Duration < M0.Duration:
                            # ※ m1 may be an x-wave within a Complex Correction
                            M1.Structure_list_label.append('x.c3')
                            M1.EW_structure.append('5d:x-wave')
                            sw = 1
                else:
                    M1.Structure_list_label.append(':F3')
                    M1.EW_structure.append('5d:-')
                    sw = 1
            elif M3.Price_range / M2.Price_range < 0.618:
                M1.Structure_list_label.extend([':F3', ':c3'])
                M1.EW_structure.extend(['5d:-'] * 2)
                sw = 1

                if M5 is not None and wave_overlap(M1, M3) and M4.Price_range < M2.Price_range \
                        and self.wave_is_retraced(M4, M5) \
                        and self.market_goes_beyond_w1_start(M0, M4.End_candle_index,
                                                             int(0.5 * (M4.End_candle_index - M0.Start_candle_index))):
                    # ※ The market possibly completed a Terminal pattern at m4
                    M1.Structure_list_label.append(':c3')
                    M1.EW_structure.append('5d:Terminal pattern completed at m4')
                    sw = 1
                if M4 is not None:
                    tmp_price_range = self.waves_price_coverage([M2, M3, M4])
                    if self.wave_is_steeper(tmp_price_range, M4.End_candle_index - M2.Start_candle_index, M0):
                        if M_2 is not None and M_1.Price_range / M0.Price_range >= 0.618:
                            # ※ There is a remote chance m1 completed a Contracting Triangle
                            M1.Structure_list_label.append('(:L3)')
                            M1.EW_structure.append('5d:Contracting Triangle')
                            sw = 1
                        if M_1 is not None and self.waves_almost_same(M_1.Price_range, M0.Price_range) \
                                and M1.Duration >= M_1.Duration and M0.Duration > M_1.Duration and M0.Duration > M1.Duration:
                            # ※ There is a remote chance m1 completed a severe c-Failure Flat
                            M1.Structure_list_label.append('[:L5]')
                            M1.EW_structure.append('5d:severe c-Failure Flat')
                            sw = 1
            if M6 is not None and M3.Price_range / M1.Price_range >= 0.618 and M3.Price_range / M2.Price_range < 1 \
                    and M4.Price_range >= M2.Price_range \
                    and (M4.Price_range / M0.Price_range >= 0.618 or abs(
                M6.End_price - M4.Start_price) / M0.Price_range >= 0.618) \
                    and not self.wave_formation_beyond(M3, M4) and not self.wave_formation_beyond(M3,
                                                                                                  M5) and not self.wave_formation_beyond(
                M3, M6):
                # ※ There is a good chance m1 is the first leg of an Irregular Failure Flat
                M1.Structure_list_label.append(':F3')
                M1.EW_structure.append('5d:wave1 of Irregular Failure Flat')
                sw = 1

        if sw == 0:
            M1.Structure_list_label.append(':F3')
            M1.EW_structure.append('5d:-')

        hyper_monowaves[idx] = M1

    def EW_R6a(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M0 = hyper_monowaves[idx - 1] if (idx - 1 >= 0) else None
        M_1 = hyper_monowaves[idx - 2] if (idx - 2 >= 0) else None
        M_2 = hyper_monowaves[idx - 3] if (idx - 3 >= 0) else None
        M_3 = hyper_monowaves[idx - 4] if (idx - 4 >= 0) else None
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None
        M4 = hyper_monowaves[idx + 3] if (idx + 3 < n) else None

        if M2 is not None:
            if M2.Num_sub_monowave >= 3:
                if not self.wave_ret_n_subwaves_fib_ratio(M1, M2, 0.618):
                    # ※ m1 may be 3 of a 5th Failure Impulse pattern
                    M1.Structure_list_label.append(':5')
                    M1.EW_structure.append('6a:wave3 of a 5th Failure Impulse(Trending or Terminal)')
                    # ※ First wave of m2 may be an x-wave, or m1 may be hiding an x-wave
                    M1.Structure_list_label.append(':s5')
                    M1.EW_structure.append('6a:complex correction')
                    M1.Structure_list_label.append('x.c3')
                    M1.EW_structure.append('6a:missing x-wave')

                else:
                    # ※ m1 may have completed wave-a of a Flat with a complex b-wave
                    M1.Structure_list_label.append(':F3')
                    M1.EW_structure.append('6a:wave-a of a Flat with a complex b-wave')
                    # ※ m1 may have completed wave-3 of a 5th Failure Impulse pattern
                    M1.Structure_list_label.append(':5')
                    M1.EW_structure.append('6a:wave3 of a 5th Failure Impulse')
            else:
                if M3 is not None:
                    if M3.Price_range / M2.Price_range < 0.618:
                        M1.Structure_list_label.append(':L5')
                        M1.EW_structure.append('6a:-')
                        if M_2 is not None and wave_overlap(M_2, M0):
                            M1.Structure_list_label.append(':L3')
                            M1.EW_structure.append('6a:-')
                    else:
                        M1.Structure_list_label.append(':L5')
                        M1.EW_structure.append('6a:-')
                if self.wave_is_retraced(M1, M2):
                    # ※ A Trending Impulse pattern may have completed with m1
                    M1.Structure_list_label.append(':L5')
                    M1.EW_structure.append('6a:Trending Impulse')
                    if M4 is not None and M_3 is not None:
                        if M3.Price_range < M2.Price_range and (
                                self.wave_retrace_beyond(M_3, M2, (M1.End_candle_index - M_3.Start_candle_index) // 2,
                                                         M2.Duration) or
                                self.wave_retrace_beyond(M_3, M2, (M1.End_candle_index - M_3.Start_candle_index) // 2,
                                                         M4.End_candle_index - M2.Start_candle_index)) \
                                and wave_overlap(M_2, M0):
                            # ※ m1 may have completed a Terminal Impulse pattern
                            M1.Structure_list_label.append('(:L3)')
                            M1.EW_structure.append('6a:Terminal Impulse')
                            if 0.618 < M3.Price_range / M2.Price_range < 1:
                                # ※ m2 is probably an x-wave or the Terminal pattern which completed with m1 is within a larger Triangle
                                M2.Structure_list_label.append('x.c3?')
                                M2.EW_structure.append('6a:x-wave or Terminal')
                elif self.wave_is_retraced_slower(M1, M2):
                    if M_2 is not None and not wave_beyond(M_2, M2) and M_1.Price_range / M1.Price_range >= 0.618 \
                            and M_2.Price_range < M_1.Price_range:
                        # ※ m1 may be wave-a of a Flat pattern which concludes a Complex Correction and m0 is the x-wave of the pattern
                        M1.Structure_list_label.append(':F3')
                        M1.EW_structure.append('6a:wave-a of a Flat')
                        M0.Structure_list_label.append('x.c3?')
                        M0.EW_structure.append('6a:x-wave')

        if (idx - 1 >= 0): hyper_monowaves[idx - 1] = M0
        if (idx + 1 < n): hyper_monowaves[idx + 1] = M2
        hyper_monowaves[idx] = M1

    def EW_R6b(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M0 = hyper_monowaves[idx - 1] if (idx - 1 >= 0) else None
        M_1 = hyper_monowaves[idx - 2] if (idx - 2 >= 0) else None
        M_2 = hyper_monowaves[idx - 3] if (idx - 3 >= 0) else None
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None

        if M3 is not None:
            if M3.Num_sub_monowave > 3:
                if not self.wave_ret_n_subwaves_fib_ratio(M2, M3):
                    M1.Structure_list_label.append(':5')
                    M1.EW_structure.append('6b:wave3 of a 5th Failure Impulse(Trending or Terminal)')
                    # ※ First wave of m2 may be an x-wave, or m2 may be hiding an x-wave
                    M1.Structure_list_label.append(':s5')
                    M1.EW_structure.append('6b:complex correction')
                    M1.Structure_list_label.append('x.c3')
                    M1.EW_structure.append('6b:missing x-wave')
                    # TODO for the "missing" wave scenario, circle the center of m2 and place ":5?"to the left of the circle and ":F3/x:c3?"
                else:
                    # ※ m2 may have completed wave-a of a Flat with a complex wave-b
                    # ※ m1 may have completed wave-3 of a 5th Failure Impulse pattern
                    M1.Structure_list_label.extend([':F3', ':5'])
                    M1.EW_structure.extend(
                        ['6b:wave-a of a Flat with a complex b-wave', '6b:wave-3 of a 5th Failure Impulse'])
            else:
                if (M1.Duration <= M0.Duration or M1.Duration <= M2.Duration) \
                        and (M_2 is None or M_2.Price_range < M_1.Price_range):
                    # ※ m1 may be the x-wave of a Complex Correction
                    M1.Structure_list_label.append('x.c3')
                    M1.EW_structure.append('6b:x-wave of a Complex Correction')
                if M0 is not None:
                    if (M1.Duration >= M0.Duration or M1.Duration >= M2.Duration) \
                            and self.waves_almost_same(M0.Price_range, 1.618 * M1.Price_range):
                        # ※ m1 may be part of a Zigzag or Impulse pattern
                        M1.Structure_list_label.append(':F3')
                        M1.EW_structure.append('6b:part of a Zigzag or Impulse')
                else:
                    M1.Structure_list_label.append(':F3')
                    M1.EW_structure.append('6b:part of a Zigzag or Impulse')
                if M_1 is not None:
                    if self.wave_is_retraced(M1, M2):
                        if (M3.Price_range < 0.618 * M2.Price_range or self.wave_is_retraced(M2, M3)) \
                                and (M_1.Duration >= 0.618 * M1.Duration or M_1.Price_range >= 0.618 * M1.Price_range) \
                                and self.wave_formation_beyond(M0, M1):
                            # ※ There is a chance m1 completed the c-wave of a Flat
                            M1.Structure_list_label.append(':L5')
                            M1.EW_structure.append('6b:c-wave of a Flat')
                        if M3.Price_range < 0.618 * M2.Price_range \
                                and M_1.Duration >= 0.618 * M0.Duration and M_1.Price_range >= 0.618 * M0.Price_range:
                            # ※ There is a chance m1 completed a Contracting Triangle or one of several Flat variations
                            M1.Structure_list_label.append(':L3')
                            M1.EW_structure.append('6b:Contracting Triangle')
                            if not self.wave_formation_beyond(M0, M1):
                                M1.Structure_list_label.append(':L5')
                                M1.EW_structure.append('6b:Flat')
                    elif self.wave_is_retraced_slower(M1, M2) and M2.Num_sub_monowave >= 3 \
                            and M0.Price_range <= M2.Price_range >= M_1.Price_range:
                        # ※ m1 may be one of the middle legs of a Triangle
                        M1.Structure_list_label.append(':c3')
                        M1.EW_structure.append('6b:middle legs of a Triangle')
                if self.wave_is_retraced(M2, M3):
                    if M_2 is not None and self.wave_not_shortest(M_2.Price_range, M0.Price_range, M2.Price_range) \
                            and self.market_goes_beyond_w1_start(M_2, M2.End_candle_index,
                                                                 (M2.End_candle_index - M_2.Start_candle_index) // 2):
                        # ※ A Terminal pattern may have concluded with m2
                        M1.Structure_list_label.append(':sL3')
                        M1.EW_structure.append('6b:Terminal')
                if 1.01 <= M3.Price_range / M2.Price_range <= 1.618:
                    # TODO remove and then append [:F3]
                    # ※ An Expanding Triangle may be forming
                    M1.Structure_list_label.append(':c3')
                    M1.EW_structure.append('6b:Expanding Triangle')

        hyper_monowaves[idx] = M1

    def EW_R6c(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M0 = hyper_monowaves[idx - 1] if (idx - 1 >= 0) else None
        M_1 = hyper_monowaves[idx - 2] if (idx - 2 >= 0) else None
        M_2 = hyper_monowaves[idx - 3] if (idx - 3 >= 0) else None
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None

        M1.Structure_list_label.append(':F3')
        M1.EW_structure.append('-')
        if M3 is not None and M_1 is not None and self.wave_is_retraced(M1, M2):
            # secondary uses of wave_is_retraced
            if M3.Price_range < 0.618 * M2.Price_range \
                    and self.wave_is_retraced(M0, M2) \
                    and 0.618 < M_1.Price_range / M0.Price_range < 1.618 and self.wave_is_steeper(M2.Price_range,
                                                                                                  M2.Duration, M0):
                # ※ m1 may have completed a Contracting Triangle or a severe C-Failure Flat
                M1.Structure_list_label.append(':L3')
                M1.EW_structure.append('6c:Contracting Triangle')
                M1.Structure_list_label.append('(:L5)')
                M1.EW_structure.append('6c:severe C-Failure Flat')
        if M3 is not None and M_2 is not None and self.wave_is_retraced(M2, M3):
            if wave_overlap(M_1, M1) and self.wave_not_shortest(M_2.Price_range, M0.Price_range, M2.Price_range) \
                    and self.market_goes_beyond_w1_start(M_2, M2.End_candle_index,
                                                         (M2.End_candle_index - M_2.Start_candle_index) // 2):
                # ※ A Terminal pattern may have concluded with m2
                M1.Structure_list_label.append(':sL3')
                M1.EW_structure.append('6c:Terminal concluded with m2')
        if M3 is not None and M2 is not None and 1.01 <= M3.Price_range / M2.Price_range <= 1.618:
            # ※ There is the unlikely possibility that an Expanding Triangle is forming
            M1.Structure_list_label.append(':c3')
            M1.EW_structure.append('6c:Expanding Triangle')

        hyper_monowaves[idx] = M1

    def EW_R6d(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M0 = hyper_monowaves[idx - 1] if (idx - 1 >= 0) else None
        M_1 = hyper_monowaves[idx - 2] if (idx - 2 >= 0) else None
        M_2 = hyper_monowaves[idx - 3] if (idx - 3 >= 0) else None
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None
        M4 = hyper_monowaves[idx + 3] if (idx + 3 < n) else None

        if M0 is not None and M2 is not None:
            if (M0.Duration <= M1.Duration or M2.Duration <= M1.Duration) and M1.Duration >= min(M0.Duration,
                                                                                                 M2.Duration):
                # ※ m1 is either the first phase of a larger correction or the completion of a correction within a Zigzag or Impulse pattern
                M1.Structure_list_label.append(':F3')
                M1.EW_structure.append('6d:a larger correction or a Zigzag or Impulse pattern')
            if M4 is not None and M3.Price_range < 0.618 * M2.Price_range:
                temp_price = self.waves_price_coverage([M2, M3, M4])
                if temp_price <= M0.Price_range \
                        and self.wave_is_steeper(temp_price, (M4.End_candle_index - M2.Start_candle_index), M0):
                    # ※ There is a small chance that m1 completed a Contracting Triangle or a severe C-Failure Flat
                    M1.Structure_list_label.append('(:L3)')
                    M1.EW_structure.append('6d:Contracting Triangle')
                    M1.Structure_list_label.append('[:L5]')
                    M1.EW_structure.append('6d:severe C-Failure Flat')
            if M_2 is not None and M3 is not None and self.wave_is_retraced(M2, M3):
                if wave_overlap(M_1, M1) and self.wave_not_shortest(M_2.Price_range, M0.Price_range, M2.Price_range) \
                        and self.market_goes_beyond_w1_start(M_2, M2.End_candle_index,
                                                             (M2.End_candle_index - M_2.Start_candle_index) // 2):
                    # ※ A Terminal pattern may have concluded with m2
                    M1.Structure_list_label.append(':sL3')
                    M1.EW_structure.append('6d:Terminal concluded with m2')

        hyper_monowaves[idx] = M1

    def EW_R7a(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M0 = hyper_monowaves[idx - 1] if (idx - 1 >= 0) else None
        M_1 = hyper_monowaves[idx - 2] if (idx - 2 >= 0) else None
        M_2 = hyper_monowaves[idx - 3] if (idx - 3 >= 0) else None
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None

        if M2 is not None:
            if M2.Num_sub_monowave > 3:
                if not self.wave_ret_n_subwaves_fib_ratio(M1, M2, 0.618):
                    # ※ First wave of m2 may be an x-wave, or m1 may be hiding an x-wave or m1 may be 3 of a 5th Failure Impulse pattern (Trending or Terminal)
                    M1.Structure_list_label.append(':5')
                    M1.EW_structure.append('7a:wave3 of a 5th Failure Impulse(Trending or Terminal)')
                    M1.Structure_list_label.append(':s5')
                    M1.EW_structure.append('7a:complex correction')
                    M2.Structure_list_label.append('x.c3')
                    M2.EW_structure.append('7a:missing x-wave')
                else:
                    # ※ m1 may have completed wave-a of a Flat with a complex b-wave or wave-3 of a 5th Failure Impulse pattern
                    M1.Structure_list_label.append(':F3')
                    M1.EW_structure.append('7a:wave-a of a Flat with a complex b-wave')
                    M1.Structure_list_label.append(':5')
                    M1.EW_structure.append('7a:wave3 of a 5th Failure Impulse')
            else:
                # ※ No matter what the surrounding evidence, a :L5 is very likely
                M1.Structure_list_label.append(':L5')
                M1.EW_structure.append('7a:-')
                if M3 is not None and M_2 is not None:
                    if M3.Price_range < 0.618 * M2.Price_range and M_2.Price_range < M_1.Price_range \
                            and wave_overlap(M_2, M0):
                        # ※ There is the possibility a Terminal Impulse pattern completed with m1
                        M1.Structure_list_label.append(':L3')
                        M1.EW_structure.append('7a:Terminal')

        if (idx + 1 < n): hyper_monowaves[idx + 1] = M2
        hyper_monowaves[idx] = M1

    def EW_R7b(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M0 = hyper_monowaves[idx - 1] if (idx - 1 >= 0) else None
        M_1 = hyper_monowaves[idx - 2] if (idx - 2 >= 0) else None
        M_2 = hyper_monowaves[idx - 3] if (idx - 3 >= 0) else None
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None
        M4 = hyper_monowaves[idx + 3] if (idx + 3 < n) else None

        if M3 is not None:
            if M3.Num_sub_monowave > 3:
                if not self.wave_ret_n_subwaves_fib_ratio(M2, M3, 0.618):
                    # ※ First wave of m3 may be an x-wave, or m2 may be hiding a wave-b, or m2 may be 3 of a 5th Failure Impulse pattern(Trending or Terminal)
                    # TODO
                    M1.Structure_list_label.extend([':c3', ':L3'])
                    M1.EW_structure.extend(['7b:-', '7b:5th Failure Impulse'])
                    if M3.Num_sub_monowave <= 5 or not self.wave_ret_n_subwaves_fib_ratio(M2, M3, 0.618,
                                                                                          M3.Num_sub_monowave):
                        M1.Structure_list_label.append(':F3')
                        M1.EW_structure.append('7b:-')
                    M2.Structure_list_label.extend('x.c3')
                    M2.EW_structure.append('7b:-')
                    M3.Structure_list_label.extend('x.c3')
                    M3.EW_structure.append('7b:-')
                else:
                    # ※ m2 may have completed wave-a of a Flat with a complex wave-b
                    # ※ m1 may have completed wave-3 of a 5th Failure Impulse pattern
                    M1.Structure_list_label.extend([':F3', ':5'])
                    M1.EW_structure.extend(
                        ['7b:wave-a of a Flat with a complex b-wave', '7b:wave-3 of a 5th Failure Impulse'])
            else:
                if M0.Price_range / M1.Price_range >= 0.618 \
                        and 1 <= M3.Price_range / M2.Price_range <= 2.618:
                    # ※ m1 may be part of an Expanding Triangle
                    M1.Structure_list_label.append(':c3')
                    M1.EW_structure.append('7b:Expanding Triangle')
                    if M4 is not None and M4.Price_range / M3.Price_range >= 0.618:
                        M1.Structure_list_label.append(':F3')
                        M1.EW_structure.append('7b:-')
                if M1.Price_range / M0.Price_range <= 0.618 \
                        and ((M3.Price_range / M2.Price_range < 0.618 and M3.Duration <= M2.Duration) \
                             or self.wave_is_retraced(M2, M3)) \
                        and self.wave_is_retraced(M0, M2) \
                        and self.wave_is_steeper(M2.Price_range, M2.Duration, M0):
                    # "※ There is a good chance m1 completed a Contracting Triangle or a c-Failure Flat
                    M1.Structure_list_label.extend([':L3', ':L5'])
                    M1.EW_structure.extend(['7b:Contracting Triangle', '7b:c-Failure Flat'])
                if 0.618 <= M3.Price_range / M2.Price_range <= 1:
                    # ※ An Elongated Flat is the most likely pattern which concluded with m2
                    M1.Structure_list_label.append(':c3')
                    M1.EW_structure.append('7b:Elongated Flat concluded with m2')
                if self.wave_is_retraced(M2, M3):
                    # ※ A Trending Impulse pattern may have concluded with m2
                    M1.Structure_list_label.append(':L5')
                    M1.EW_structure.append('7b:Trending Impulse concluded with m2')
                    if (M_2 is not None and M_1.Price_range < M0.Price_range and self.wave_not_shortest(M_2.Price_range, M0.Price_range, M2.Price_range)
                            and self.market_goes_beyond_w1_start(M_2, M2.End_candle_index, (M2.End_candle_index - M_2.Start_candle_index) // 2) ):
                        # ※ A 5th Extension Terminal may have completed with m2
                        M1.Structure_list_label.append(':sL3')
                        M1.EW_structure.append('7b:5th Extension Terminal completed with m2')

        if M2 is not None: hyper_monowaves[idx + 1] = M2
        if M3 is not None: hyper_monowaves[idx + 2] = M3
        hyper_monowaves[idx] = M1

    def EW_R7c(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M0 = hyper_monowaves[idx - 1] if (idx - 1 >= 0) else None
        M_1 = hyper_monowaves[idx - 2] if (idx - 2 >= 0) else None
        M_2 = hyper_monowaves[idx - 3] if (idx - 3 >= 0) else None
        M_3 = hyper_monowaves[idx - 4] if (idx - 4 >= 0) else None
        M_4 = hyper_monowaves[idx - 5] if (idx - 5 >= 0) else None
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None

        if M2 is not None:
            if M1.Duration >= M0.Duration or M1.Price_range >= M2.Price_range:
                M1.Structure_list_label.append(':F3')
                M1.EW_structure.append('7c:-')
            if M_2 is not None:
                if self.wave_is_retraced(M0, M2) \
                        and self.wave_is_steeper(M2.Price_range, M2.Duration, M0):
                    if M_4 is not None and M_4.Price_range >= M_2.Price_range:
                        # ※ m1 may have completed a Contracting Triangle
                        M1.Structure_list_label.append(':L3')
                        M1.EW_structure.append('7c:Contracting Triangle')
                    if M_2.Price_range / M0.Price_range >= 1.618 \
                            and M_2.Price_range / M2.Price_range >= 0.618 \
                            and check_subitem_in_list(M_1.Structure_list_label, ':F3'):
                        # ※ m1 may have completed an Irregular Failure Flat
                        M1.Structure_list_label.append(':L5')
                        M1.EW_structure.append('7c:Irregular Failure Flat')
                if M3 is not None and self.wave_is_retraced(M2, M3):
                    if self.market_goes_beyond_w1_start(M_2, M2.End_candle_index,
                                                        (M2.End_candle_index - M_2.Start_candle_index) // 2) \
                            and M0.Price_range > M_2.Price_range:
                        # ※ An Expanding Terminal Impulse pattern may have concluded with m2
                        M1.Structure_list_label.append(':sL3')
                        M1.EW_structure.append('7c:Expanding Terminal Impulse concluded with m2')
                if self.wave_is_retraced(M1, M2) and M_3 is not None and M2.Price_range / M0.Price_range >= 1.618 and \
                        beyond_trendline(M_3, M_1, M1):
                    # ※ A Running Correction could have completed with m1
                    M1.Structure_list_label.append(':L5')
                    M1.EW_structure.append('7c:Running Correction')

        hyper_monowaves[idx] = M1

    def EW_R7d(self, hyper_monowaves, idx):
        n = len(hyper_monowaves)
        M1 = hyper_monowaves[idx]
        M0 = hyper_monowaves[idx - 1] if (idx - 1 >= 0) else None
        M_1 = hyper_monowaves[idx - 2] if (idx - 2 >= 0) else None
        M_2 = hyper_monowaves[idx - 3] if (idx - 3 >= 0) else None
        M2 = hyper_monowaves[idx + 1] if (idx + 1 < n) else None
        M3 = hyper_monowaves[idx + 2] if (idx + 2 < n) else None
        M4 = hyper_monowaves[idx + 3] if (idx + 3 < n) else None

        if M2 is not None and M0 is not None:
            if (M0.Duration <= M1.Duration or M2.Duration <= M1.Duration) \
                    and M1.Duration >= min(M0.Duration, M2.Duration):
                # ※ m1 may be part of a Zigzag or Impulse pattern
                M1.Structure_list_label.append(':F3')
                M1.EW_structure.append('7d:-')
            if (M1.Duration <= M0.Duration or M1.Duration <= M2.Duration):
                M1.Structure_list_label.append(':c3')
                M1.EW_structure.append('7d:-')
                if M_1 is not None:
                    if M4 is not None:
                        if M_2 is not None and M_2.Price_range / M_1.Price_range >= 1.618 \
                                and M_1.Price_range < M0.Price_range \
                                and M1.Price_range < 0.618 * abs(M0.End_price - M_2.Start_price):
                            if M3.Price_range > M2.Price_range:
                                if M4.Price_range < M3.Price_range:
                                    # //TODO
                                    # ※ m1 may be the x-wave of a Double Zigzag or a Complex correction which begins with a Zigzag
                                    M1.Structure_list_label.append('x.c3')
                                    M1.EW_structure.append('7d:-')
                        if 1 <= M0.Price_range / M_1.Price_range <= 1.618 and M2.Price_range / M0.Price_range <= 1.618 \
                                and M4.Price_range / M2.Price_range >= 0.382 \
                                and (M3.Price_range < M2.Price_range or (
                                M3.Price_range > M2.Price_range and M4.Price_range < M3.Price_range)):
                            # ※ m1 may be the x-wave of a Complex correction which starts with a Flat and ends with a Flat or Triangle
                            M1.Structure_list_label.append('x.c3')
                            M1.EW_structure.append('7d:-')
                    if M_2 is not None:
                        if self.waves_are_similar(M_1.Price_range, M1.Price_range) or self.waves_are_similar(
                                M_1.Duration, M1.Duration) \
                                and M_1.Price_range < M0.Price_range and self.wave_not_shortest(M_2.Price_range,
                                                                                                M0.Price_range,
                                                                                                M2.Price_range):
                            # TODO
                            if M0.Price_range <= max(M_2.Price_range, M2.Price_range):
                                if M1.Structure_list_label and not check_subitem_in_list(M1.Structure_list_label,
                                                                                         ':c3'):
                                    M_1.Structure_list_label.append('x.c3')
                                    M_1.EW_structure.append('7d:-')
                                else:
                                    # ※ m1 may be part of a Complex Double Zigzag
                                    M1.Structure_list_label.append('x.c3')
                                    M1.EW_structure.append('7d:-')
                            else:
                                M0.Structure_list_label.append(':?H:?')
                                M0.EW_structure.append('7d:-')
                                # TODO
        if M3 is not None and M_1 is not None:
            if self.wave_is_retraced(M1, M2) \
                    and self.waves_are_similar(M_1.Price_range, M1.Price_range) and self.waves_are_similar(M_1.Duration,
                                                                                                           M1.Duration) \
                    and M2.Price_range / M0.Price_range >= 1.618:
                if not wave_overlap(M_1, M1) and not self.wave_is_retraced(M2, M3):
                    # ※ m1 may have completed a Running Correction
                    M1.Structure_list_label.append(':L5')
                    M1.EW_structure.append('7d:Running Correction')
                if M_2 is not None and M_2.Price_range / M0.Price_range < 1.618 and M3.Price_range < 0.618 * M2.Price_range \
                        and check_subitem_in_list(M1.Structure_list_label, ':L5'):
                    # ※ m1 simultaneously terminates more than one Elliott pattern, each of consecutively larger degree
                    M1.Structure_list_label.append(':L5')
                    M1.EW_structure.append('7d:m1 terminates more than one Elliott')

            if M3.Price_range < 0.618 * M2.Price_range:
                if self.wave_is_steeper(M2.Price_range, M2.Duration, M0) and M_1.Price_range / M0.Price_range <= 1.618:
                    if wave_overlap(M_1, M1) \
                            and (check_subitem_in_list(M0.Structure_list_label, ':c3') or check_subitem_in_list(
                        M0.Structure_list_label, ':sL3')):
                        # ※ There is small chance m1 completed a Contracting Triangle
                        M1.Structure_list_label.append('(:L3)')
                        M1.EW_structure.append('7d:small chance of a Contracting Triangle')

                    if (self.waves_are_similar(M_1.Price_range, M1.Price_range) or self.waves_are_similar(M_1.Duration,
                                                                                                          M1.Duration)) \
                            and wave_overlap(M_1, M1):
                        # ※ m1 may have completed an Irregular or c-Failure Flat
                        M1.Structure_list_label.append(':L5')
                        M1.EW_structure.append('7d:Irregular or c-Failure Flat')
                if 0.618 * M0.Price_range <= M2.Price_range <= 1.618 * M0.Price_range and M_1.Price_range < M0.Price_range \
                        and M_1.Price_range / M0.Price_range <= 1.618:
                    # ※ m1 may be an x-wave of a Complex Corrective pattern
                    M1.Structure_list_label.append('x.c3')
                    M1.EW_structure.append('7d:-')
            if M4 is not None and M_2 is not None:
                if self.wave_is_retraced(M2, M3):
                    if M4.Price_range < 0.618 * M3.Price_range and M_1.Price_range < M0.Price_range \
                            and wave_overlap(M_1, M1) and self.wave_not_shortest(M_2.Price_range, M0.Price_range,
                                                                                 M2.Price_range) \
                            and self.wave_retrace_beyond(M_2, M3, (M2.End_candle_index - M_2.Start_candle_index) // 2,
                                                         M3.Duration):
                        # ※ A Terminal pattern may have concluded with m2
                        M1.Structure_list_label.append(':sL3')
                        M1.EW_structure.append('7d:Terminal Pattern')

        if (idx - 2 >= 0): hyper_monowaves[idx - 2] = M_1
        if (idx - 1 >= 0): hyper_monowaves[idx - 1] = M0
        hyper_monowaves[idx] = M1

    # region utility functions
    def market_goes_beyond_w1_end(self, W1, dur):
        """Returns True if the market exceeds the end of W1 in the same amount of time (or less) than [dur]"""
        # TODO make loop on monowaves
        for i in range(W1.End_candle_index + 1, len(self.nodes)):
            if (i > W1.End_candle_index + dur):
                return False

            if (W1.Direction == 1):
                if (self.nodes.Price[i] > W1.End_price):
                    return True
            else:
                if (self.nodes.Price[i] < W1.End_price):
                    return True
        return False

    def market_goes_beyond_w1_start(self, W1, offset, dur):
        """Returns True if the market exceeds the start of W1 in the same amount of time (or less) than [dur] from [offset]"""
        # TODO make loop on monowaves
        for i in range(offset + 1, len(self.nodes)):
            if (i > offset + dur):
                return False

            if (W1.Direction == 1):
                if (self.nodes.Price[i] < W1.Start_price):
                    return True
            else:
                if (self.nodes.Price[i] > W1.Start_price):
                    return True
        return False

    def waves_price_coverage(self, waves: list) -> float:
        """Returns price range number which is coverd by the list of waves"""
        return max([w.Max_price for w in waves]) - min([w.Min_price for w in waves])

    def wave_retrace_beyond(self, W1, W2, dur=np.iinfo(np.intp).max, d2=np.iinfo(np.intp).max):
        """Returns True if the end of wave 2 exceeds the start of wave 1 (W1 and W2 are in the opposite direction)"""
        W2End = self.nodes.Price[W2.Start_candle_index + min(dur, d2)]
        return (W2End - W2.Start_price) * (W2End - W1.Start_price) > 0

    def wave_formation_beyond(self, W1, W2):
        """Returns True if the max/min of wave 2 exceeds the end of wave 1 (W2 could have same/opposite direction)"""
        tmp_price = W2.Max_price if W1.Direction > 0 else W2.Min_price
        return (W1.End_price - W1.Start_price) * (tmp_price - W1.End_price) > 0

    def waves_exceed_start_W1(self, W1, waves_list):
        """Returns True if the max/min of list of waves_list exceeds the start of wave 1 (W1 and waves_list are in the opposite direction)"""
        tmp_price = max([w.Max_price for w in waves_list]) if W1.Direction < 0 else min(
            [w.Min_price for w in waves_list])
        return (W1.End_price - W1.Start_price) * (tmp_price - W1.Start_price) < 0

    def wave_is_retraced(self, W1, W2, retraced_ratio=1):
        """Returns True if W2 retraces all of W1 in the same amount of time (or less [dur]) that W1 took to form.
            This function also has an alternative use when W1 and W2 are in the same direction"""
        dur = W1.Duration
        d2 = W2.Duration
        return abs(self.nodes.Price[W2.Start_candle_index + min(dur, d2)] - W2.Start_price) / (
                W1.Price_range * retraced_ratio) >= 1

    def wave_is_retraced_slower(self, W1, W2):
        """Returns True if W2 retraces all of W1 in the same amount of time (or more [dur]) that W1 took to form"""
        if (W2.End_price - W2.Start_price) * (W2.End_price - W1.Start_price) > 0 and W2.Duration > W1.Duration:
            return (self.nodes.Price[W2.Start_candle_index + W1.Duration] - W2.Start_price) * (
                    self.nodes.Price[W2.Start_candle_index + W1.Duration] - W1.Start_price) <= 0
        return False

    def wave_ret_n_subwaves(self, W1, W2, n=3):
        """Returns retracement range of first (n) subwaves of W2 with respect of W1"""
        if (W2.Num_sub_monowave >= n):
            end_idx = list(range(W2.MW_start_index, W2.MW_start_index + n))
            if W1.Direction == 1:
                return max([abs(self.monowaves.Min_price[idx] - W2.Start_price) for idx in end_idx])
            else:
                return max([abs(self.monowaves.Max_price[idx] - W2.Start_price) for idx in end_idx])
        return 0.0

    def wave_ret_n_subwaves_fib_ratio(self, W1, W2, fib_ratio=fib_ratio, n=3):
        """Returns True if the first (n) subwaves of W2 retrace more than fibo_ratio percent of W1 (W1 and W2 are in the opposite direction)"""
        return self.wave_ret_n_subwaves(W1, W2, n) >= fib_ratio * W1.Price_range

    def waves_almost_same(self, pd1, pd2, tol=1.1):
        """Returns True if the value of pd1 and pd2 are almost equal, where pd is price or duration"""
        return (pd1 / pd2) < tol or (pd2 / pd1) < tol

    def waves_are_similar(self, pd1, pd2, fib_r=fib_ratio, order=False):
        """Returns True if the value of pd1 and pd2 are equal or related by fib_ratios, where pd is price or duration"""
        return self.waves_almost_same(pd1, pd2) or waves_are_fib_related(pd1, pd2, fib_r, order)

    def wave_not_shortest(self, p1, p2, p3):
        """Returns True if the value of p2 is equal or more than price of min(p1,p3)"""
        return p2 >= min(p1, p3)

    def wave_longer_fib(self, p1, p2, p3):
        """Returns True if the longest of these waves is about 1.68 greater than the second"""
        flag = False
        max_temp = max(p1, max(p2, p3))
        if (p1 == max_temp):
            if (p1 >= (1 + fib_ratio) * max(p2, p3)):
                flag = True
        elif (p2 == max_temp):
            if (p2 >= (1 + fib_ratio) * max(p1, p3)):
                flag = True
        else:
            if (p3 >= (1 + fib_ratio) * max(p1, p2)):
                flag = True

        return flag

    def waves_relative_slope(self, p1, d1, W2):
        """Returns the slop proportion of wave 1(p1, d1) to wave 2(W2)"""
        return (p1 * W2.Duration) / (W2.Price_range * d1)

    def wave_is_steeper(self, p1, d1, W2, retraced_ratio=1):
        """Returns True if wave 1(p1,d1) is steeper and have a larger Price_range (W1 and W2 are in the same or opposite direction)"""
        return self.waves_relative_slope(p1, d1, W2) > 1 and p1 >= (W2.Price_range * retraced_ratio)

    def wave_breaking_trend(self, mn2e, m0e, m1e, m2e):
        """Returns True if M2 breaks a trendline drawn across the low of M(-2) and M0 in a period equal to or less than that taken by Ml"""
        xr, yr = intersection(mn2e, self.nodes.Price[mn2e], m0e, self.nodes.Price[m0e], m1e, self.nodes.Price[m1e], m2e,
                              self.nodes.Price[m2e])
        if xr is None: return False
        progress = min(m1e - m0e, m2e - m1e)  # minimum between len M1 and M2
        # print(m1e, progress, xr) #for test
        return m1e <= xr <= m1e + progress

    def price_ratio(self, W1, W2, ratio):
        """Returns True if W1 Price range is almost higher than W2 Price range with respect to a ratio"""
        return W1.Price_range / W2.Price_range >= (ratio * 0.95)

    def check_smallest(self, waves: list, idx):
        """Return True if (idx)th wave in waves is the smallest one"""
        for w in waves:
            if w.Price_range <= waves[idx].Price_range:
                return False
        return True

    def check_largest(self, waves: list, idx):
        """Return True if (idx)th wave in waves is the largest one"""
        for w in waves:
            if w.Price_range >= waves[idx].Price_range:
                return False
        return True

    # endregion

    # region remove_labels functions (page 54 pdf Glenn-Neely)
    def rem_f3(self, HMW, idx):

        if not check_subitem_in_list(HMW[idx].Structure_list_label, ':F3'):
            return

        n = len(HMW)
        M1 = HMW[idx]
        M0 = HMW[idx - 1] if (idx - 1 >= 0) else None
        M2 = HMW[idx + 1] if (idx + 1 < n) else None
        M3 = HMW[idx + 2] if (idx + 2 < n) else None
        M4 = HMW[idx + 3] if (idx + 3 < n) else None

        if M2 is not None and M0 is not None:
            if (check_subitem_in_list(M0.Structure_list_label, ':5') and check_subitem_in_list(M2.Structure_list_label,
                                                                                               ':L5') and self.price_ratio(
                M2, M0, (1 - fib_ratio))) \
                    or (check_subitem_in_list(M0.Structure_list_label, ':F3') or check_subitem_in_list(
                M2.Structure_list_label, ':F3')) \
                    or (check_subitem_in_list(M0.Structure_list_label, ':s5') and check_subitem_in_list(
                M2.Structure_list_label, ':L5') and self.price_ratio(M2, M0, 1)):
                return

        if M3 is not None:
            if (check_subitem_in_list(M0.Structure_list_label, '?') and check_subitem_in_list(M2.Structure_list_label,
                                                                                              ':c3') and check_subitem_in_list(
                M3.Structure_list_label, ':L5')) \
                    or (check_subitem_in_list(M0.Structure_list_label, '?') and check_subitem_in_list(
                M2.Structure_list_label, ':c3') and check_subitem_in_list(M3.Structure_list_label, ':c3')) \
                    or (check_subitem_in_list(M0.Structure_list_label, 'x.c3') and check_subitem_in_list(
                M2.Structure_list_label, ':c3') and check_subitem_in_list(M3.Structure_list_label, ':L5')) \
                    or (check_subitem_in_list(M0.Structure_list_label, 'x.c3') and check_subitem_in_list(
                M2.Structure_list_label, ':c3') and check_subitem_in_list(M3.Structure_list_label, ':c3')) \
                    or (check_subitem_in_list(M0.Structure_list_label, ':5') and check_subitem_in_list(
                M2.Structure_list_label, ':5') and check_subitem_in_list(M3.Structure_list_label,
                                                                         'x.c3') and self.price_ratio(M2, M0,
                                                                                                      (1 - fib_ratio))) \
                    or (check_subitem_in_list(M0.Structure_list_label, ':5') and check_subitem_in_list(
                M2.Structure_list_label, ':s5') and check_subitem_in_list(M3.Structure_list_label,
                                                                          'x.c3') and self.price_ratio(M2, M0, (
                    1 - fib_ratio))):
                return

        if M4 is not None:
            if (check_subitem_in_list(M0.Structure_list_label, ':5') and check_subitem_in_list(M2.Structure_list_label,
                                                                                               ':5') and check_subitem_in_list(
                M3.Structure_list_label, ':F3') and check_subitem_in_list(M4.Structure_list_label,
                                                                          ':L5') and self.price_ratio(M2, M0, (
                    1 - fib_ratio))):
                return

        HMW[idx].Structure_list_label = remove_subitem_in_list(M1.Structure_list_label, ':F3')

    def rem_c3(self, HMW, i):

        n = len(HMW)

        if not check_subitem_in_list(HMW[i].Structure_list_label, ':c3'):
            return

        if i == 0 or i == n - 1:
            HMW[i].Structure_list_label = remove_subitem_in_list(HMW[i].Structure_list_label, ':c3')
            return

        M1 = HMW[i]
        M0 = HMW[i - 1] if (i - 1 >= 0) else None
        M_1 = HMW[i - 2] if (i - 2 >= 0) else None
        M2 = HMW[i + 1] if (i + 1 < n) else None
        M3 = HMW[i + 2] if (i + 2 < n) else None

        if M2 is not None:
            # 2. F3-c3-5 : 5 must be larger than c3; if 5 is 161.8% or more of F3, 5 should be retraced 61.8% or more
            if (check_subitem_in_list(M0.Structure_list_label, ':F3') and check_subitem_in_list(M2.Structure_list_label,
                                                                                                ':5') and M2.Price_range > M1.Price_range):
                if (self.price_ratio(M2, M0, 1 + fib_ratio)):
                    if (self.price_ratio(M2, M1, fib_ratio)):
                        return
                else:
                    return

            # 4. F3-c3-L5
            if (check_subitem_in_list(M0.Structure_list_label, ':F3') and check_subitem_in_list(M2.Structure_list_label,
                                                                                                ':L5')):
                return
            # 8. :3-c3-:3 : c3 should be less than 61.8% or more than 161.8% of the first :3
            if (check_subitem_in_list(M0.Structure_list_label, ':3') and check_subitem_in_list(M2.Structure_list_label,
                                                                                               ':3')):
                if self.price_ratio(M0, M1, 1 + fib_ratio) or self.price_ratio(M1, M0, 1 + fib_ratio):
                    M1.Structure_list_label.append('x.c3')  # maybe need to remove :c3
                    return

        if M3 is not None:
            # 1. F3-c3-c3-c3: second or third c3 must be smallest or largest of all four
            if (check_subitem_in_list(M0.Structure_list_label, ':F3') and check_subitem_in_list(M2.Structure_list_label,
                                                                                                ':c3') and check_subitem_in_list(
                M3.Structure_list_label, ':c3')):
                if (self.check_smallest(HMW[i - 1:i + 2], 1) or self.check_smallest(HMW[i - 1:i + 2],
                                                                                    2) or self.check_largest(
                    HMW[i - 1:i + 2], 1) or self.check_largest(HMW[i - 1:i + 2], 2)):
                    return
            # 9 and 11. 5-c3-5-F3 : c3 must be smaller than 5
            if ((check_subitem_in_list(M0.Structure_list_label, ':5') or check_subitem_in_list(M0.Structure_list_label,
                                                                                               ':s5')) and check_subitem_in_list(
                M2.Structure_list_label, ':5') and check_subitem_in_list(M3.Structure_list_label, ':F3')):
                if M1.Price_range < M0.Price_range:
                    M1.Structure_list_label.append('x.c3')  # maybe need to remove :c3
                    return

            # 10 and 12. 5-c3-F3-c3 : c3 must be smaller than 5
            if ((check_subitem_in_list(M0.Structure_list_label, ':5') or check_subitem_in_list(M0.Structure_list_label,
                                                                                               ':s5')) and check_subitem_in_list(
                M2.Structure_list_label, ':F3') and check_subitem_in_list(M3.Structure_list_label, ':c3')):
                if M1.Price_range < M0.Price_range:
                    M1.Structure_list_label.append('x.c3')  # maybe need to remove :c3
                    return
                # 13. 5-c3-F3-c3 : c3 must be smaller than 5 and F3 must be smaller than c3)
                if M2.Price_range < M1.Price_range > M0.Price_range:
                    M1.Structure_list_label.append('x.c3')  # maybe need to remove :c3
                    return

        if M_1 is not None and M3 is not None:
            # 5. F3-c3-c3-c3-L3 : last c3 or L3 should be smallest or largest of all five Structure labels
            if (check_subitem_in_list(M_1.Structure_list_label, ':F3') and check_subitem_in_list(
                    M0.Structure_list_label, ':c3') and check_subitem_in_list(M2.Structure_list_label,
                                                                              ':c3') and check_subitem_in_list(
                M3.Structure_list_label, ':L3')):
                if (self.check_smallest(HMW[i - 2:i + 2], 3) or self.check_smallest(HMW[i - 2:i + 2],
                                                                                    4) or self.check_largest(
                    HMW[i - 2:i + 2], 3) or self.check_largest(HMW[i - 2:i + 2], 4)):
                    return

            # 6. F3-c3-c3-sl3-L3 : L3 must be the smallest of all five Structure labels
            if (check_subitem_in_list(M_1.Structure_list_label, ':F3') and check_subitem_in_list(
                    M0.Structure_list_label, ':c3') and check_subitem_in_list(M2.Structure_list_label,
                                                                              ':sl3') and check_subitem_in_list(
                M3.Structure_list_label, ':L3')):
                if (self.check_smallest(HMW[i - 2:i + 2], 4)):
                    return

        if M_1 is not None and M2 is not None:
            # 7. c3-c3-c3-L3 : L3 must be smallest with the last c3 (the next smallest) OR L3 or last c3 must be the longest of all four
            if (check_subitem_in_list(M_1.Structure_list_label, ':c3') and check_subitem_in_list(
                    M0.Structure_list_label, ':c3') and check_subitem_in_list(M2.Structure_list_label, ':L3')):
                if ((self.check_smallest(HMW[i - 2:i + 1], 3) and self.check_smallest(HMW[i - 2:i], 2)) or (
                        self.check_largest(HMW[i - 2:i + 1], 3) or self.check_largest(HMW[i - 2:i + 1], 2))):
                    return

        HMW[i].Structure_list_label = remove_subitem_in_list(M1.Structure_list_label, ':c3')

    def rem_x_c3(self, HMW, i):

        n = len(HMW)

        if not check_subitem_in_list(HMW[i].Structure_list_label, 'x.c3'):
            return

        if i == 0 or i == n - 1:
            HMW[i].Structure_list_label = remove_subitem_in_list(HMW[i].Structure_list_label, 'x.c3')
            return

        M1 = HMW[i]
        M0 = HMW[i - 1] if (i - 1 >= 0) else None
        M2 = HMW[i + 1] if (i + 1 < n) else None
        M3 = HMW[i + 2] if (i + 2 < n) else None

        # 3. :3*-x.c3-:3* : (last 3* is termination of pattern)
        # 4. :3*-x.c3-:3*-x.c3-:3* : (last 3* is termination of pattern) .
        # 9. s5-x.c3-:3 : (last :3 terminates pattern OR rare Triple Combination pattern forming, if so, after :3 another x.c3 would occur)
        if ((check_subitem_in_list(M0.Structure_list_label, ':3') or check_subitem_in_list(M0.Structure_list_label,
                                                                                           ':s5')) and check_subitem_in_list(
            M2.Structure_list_label, ':3')):
            return

        if M3 is not None:
            # 1. L3-x.c3-F3-c3 : extremely rare, c3 must be larger than L3 and F3
            # 2. L3-x.c3-5-c3 : virtually Impossible, c3 must be larger than L3 and 5)
            if (check_subitem_in_list(M0.Structure_list_label, ':L3') and (
                    check_subitem_in_list(M2.Structure_list_label, ':F3') or check_subitem_in_list(
                M2.Structure_list_label, ':5')) and check_subitem_in_list(M3.Structure_list_label, ':c3')):
                if (M3.Price_range > M0.Price_range and M3.Price_range > M2.Price_range):
                    return

            # 5. 5-x.c3-5-F3 : (x.c3 must be smaller than both 5's)
            # 6. 5-x.c3-F3-c3 : (x.c3 must be smaller than 5 and F3)
            # 7. s5-x.c3-5-F3 : (x.c3 must be smaller than s5 and 5)
            # 8. s5-x.c3-F3-c3 : (x.c3 must be smaller than s5 and F3)
            if (check_subitem_in_list(M0.Structure_list_label, ':5') and ((check_subitem_in_list(
                    M2.Structure_list_label, ':F3') and check_subitem_in_list(M3.Structure_list_label, ':c3')) or (
                                                                                  check_subitem_in_list(
                                                                                      M2.Structure_list_label,
                                                                                      ':5') and check_subitem_in_list(
                                                                              M3.Structure_list_label, ':F3')))):
                if (M1.Price_range < M0.Price_range and M1.Price_range < M2.Price_range):
                    return

            # 10. L5-x.c3-F3-c3 : (x.c3 must be larger than L5 and F3)
            if (check_subitem_in_list(M0.Structure_list_label, ':L5') and check_subitem_in_list(M2.Structure_list_label,
                                                                                                ':F3') and check_subitem_in_list(
                M3.Structure_list_label, ':c3')):
                if (M1.Price_range > M0.Price_range and M1.Price_range > M2.Price_range):
                    return

        HMW[i].Structure_list_label = remove_subitem_in_list(HMW[i].Structure_list_label, 'x.c3')

    def rem_sL3(self, HMW, i):

        n = len(HMW)

        if not check_subitem_in_list(HMW[i].Structure_list_label, ':sL3'):
            return

        if i == 0 or i == n - 1:
            HMW[i].Structure_list_label = remove_subitem_in_list(HMW[i].Structure_list_label, ':sL3')
            return

        M1 = HMW[i]
        M0 = HMW[i - 1] if (i - 1 >= 0) else None
        M2 = HMW[i + 1] if (i + 1 < n) else None

        # 1. c3-sL3-L3-? : (L3 should not be more than 61.8% of sl3 OR it should be more than 100% of sl3)
        if check_subitem_in_list(M0.Structure_list_label, ':c3') and check_subitem_in_list(M2.Structure_list_label,
                                                                                           ':L3'):
            if self.price_ratio(M1, M2, 1 + fib_ratio) or self.price_ratio(M2, M1, 1):
                return

        HMW[i].Structure_list_label = remove_subitem_in_list(HMW[i].Structure_list_label, ':sL3')

    def rem_L3(self, HMW, i):

        if not check_subitem_in_list(HMW[i].Structure_list_label, ':L3'):
            return

        n = len(HMW)
        M1 = HMW[i]
        M0 = HMW[i - 1] if (i - 1 >= 0) else None
        M_1 = HMW[i - 2] if (i - 2 >= 0) else None
        M_2 = HMW[i - 3] if (i - 3 >= 0) else None
        M_3 = HMW[i - 4] if (i - 4 >= 0) else None
        M2 = HMW[i + 1] if (i + 1 < n) else None
        M3 = HMW[i + 2] if (i + 2 < n) else None
        M4 = HMW[i + 3] if (i + 3 < n) else None

        if M_3 is not None:
            # 1. F3-c3-c3-c3-L3-? : (L3 must be larger than second OR larger than third c3, circle end of L3)
            if check_subitem_in_list(M_3.Structure_list_label, ':F3') and check_subitem_in_list(
                    M_2.Structure_list_label, ':c3') and check_subitem_in_list(M_1.Structure_list_label,
                                                                               ':c3') and check_subitem_in_list(
                M0.Structure_list_label, ':c3'):
                if M4.Price_range > M1.Price_range or M4.Price_range > M2.Price_range:
                    return
            # 2. F3-c3-c3-sL3-L3-? : (L3 must be the smallest wave,it must be violently retraced)
            if check_subitem_in_list(M_3.Structure_list_label, ':F3') and check_subitem_in_list(
                    M_2.Structure_list_label, ':c3') and check_subitem_in_list(M_1.Structure_list_label,
                                                                               ':c3') and check_subitem_in_list(
                M0.Structure_list_label, ':sL3'):
                if (self.check_smallest(HMW[i - 4:i], 4)):
                    return

        # 3. sL3-L3-x.c3-F3 : (sL3 and c3 must both be larger [or sL3 and c3 must both be smaller] than L3))
        if M0 is not None and M3 is not None:
            if check_subitem_in_list(M0.Structure_list_label, ':sL3') and check_subitem_in_list(M2.Structure_list_label,
                                                                                                'x.c3') and check_subitem_in_list(
                M3.Structure_list_label, ':F3'):
                if (M0.Price_range > M1.Price_range and M2.Price_range > M1.Price_range) or (
                        M0.Price_range < M1.Price_range and M2.Price_range < M1.Price_range):
                    return

        HMW[i].Structure_list_label = remove_subitem_in_list(HMW[i].Structure_list_label, ':L3')

    def rem_5(self, HMW, i):

        if not check_subitem_in_list(HMW[i].Structure_list_label, ':5'):
            return

        n = len(HMW)
        M1 = HMW[i]
        M0 = HMW[i - 1] if (i - 1 >= 0) else None
        M2 = HMW[i + 1] if (i + 1 < n) else None
        M3 = HMW[i + 2] if (i + 2 < n) else None
        M4 = HMW[i + 3] if (i + 3 < n) else None

        if M0 is not None and M3 is not None:
            #  1. ?-5-F3-5
            if check_subitem_in_list(M2.Structure_list_label, ':F3') and check_subitem_in_list(M3.Structure_list_label,
                                                                                               ':5'):
                return

            # 3. F3-5-F3-L5 : (the two F3's cannot share any similar price territory and L5 must be longer than 5)
            if check_subitem_in_list(M0.Structure_list_label, ':F3') and check_subitem_in_list(M2.Structure_list_label,
                                                                                               ':F3') and check_subitem_in_list(
                M3.Structure_list_label, ':L5'):
                if not wave_overlap(M0, M2) and M3.Price_range > M1.Price_range:
                    return
            # 4. F3-5-x.c3-F3 : (x.c3 and first F3 must be smaller than 5; second F3 almost always longer than x.c3)
            if check_subitem_in_list(M0.Structure_list_label, ':F3') and check_subitem_in_list(M2.Structure_list_label,
                                                                                               'x.c3') and check_subitem_in_list(
                M3.Structure_list_label, ':F3'):
                if M2.Price_range < M1.Price_range and M0.Price_range < M1.Price_range and M3.Price_range > M2.Price_range:
                    return
            # 5. F3-5-x.c3-5 : (x.c3 and F3 must be smaller than first 5; second 5 must be larger than x.c3)
            if check_subitem_in_list(M0.Structure_list_label, ':F3') and check_subitem_in_list(M2.Structure_list_label,
                                                                                               'x.c3') and check_subitem_in_list(
                M3.Structure_list_label, ':5'):
                if M2.Price_range < M1.Price_range and M0.Price_range < M1.Price_range and M3.Price_range > M2.Price_range:
                    return
            # 6. c3-5-x.c3-F3 : (x.c3 is either 161.8% or more of 5 or less than 61.8% of 5; if x.c3 is larger than 5 then F3 must be smaller than x.c3; if x.c3 is smaller than 5, then F3 would almost always be larger than x.c3)
            if check_subitem_in_list(M0.Structure_list_label, ':c3') and check_subitem_in_list(M2.Structure_list_label,
                                                                                               'x.c3') and check_subitem_in_list(
                M3.Structure_list_label, ':F3'):
                if (self.price_ratio(M2, M1, 1 + fib_ratio) or self.price_ratio(M1, M2, 1 + fib_ratio)):
                    if (M2.Price_range > M1.Price_range and M3.Price_range < M2.Price_range) or (
                            M2.Price_range < M1.Price_range and M3.Price_range < M2.Price_range):
                        return

            if M4 is not None:
                # 2. ?-5-F3-s5-F3 : (s5 must be longer than 5 and both F3's are shorter than the previous Structure label)
                if check_subitem_in_list(M2.Structure_list_label, ':F3') and check_subitem_in_list(
                        M3.Structure_list_label, ':s5') and check_subitem_in_list(M4.Structure_list_label, ':F3'):
                    if M3.Price_range > M1.Price_range and M2.Price_range < M1.Price_range and M4.Price_range < M3.Price_range:
                        return
                # 2. ?-5-F3-s5-x.c3 : (x.c3 must be shorter than s5 and F3 must be shorter than both 5 and s5)
                if check_subitem_in_list(M2.Structure_list_label, ':F3') and check_subitem_in_list(
                        M3.Structure_list_label, ':s5') and check_subitem_in_list(M4.Structure_list_label, 'x.c3'):
                    if M4.Price_range < M3.Price_range and M2.Price_range < M1.Price_range and M2.Price_range < M3.Price_range:
                        return

        HMW[i].Structure_list_label = remove_subitem_in_list(HMW[i].Structure_list_label, ':5')

    def rem_s5(self, HMW, i):

        if not check_subitem_in_list(HMW[i].Structure_list_label, ':s5'):
            return

        n = len(HMW)
        M1 = HMW[i]
        M0 = HMW[i - 1] if (i - 1 >= 0) else None
        M_1 = HMW[i - 2] if (i - 2 >= 0) else None
        M2 = HMW[i + 1] if (i + 1 < n) else None
        M3 = HMW[i + 2] if (i + 2 < n) else None

        if M_1 is not None and M3 is not None:
            # 1. 5-F3-s5-x.c3-F3 : (x.c3 and the first F3 must be smaller than s5)
            if check_subitem_in_list(
                    M_1.Structure_list_label, ':5') and check_subitem_in_list(
                M0.Structure_list_label,
                ':F3') and check_subitem_in_list(
                M2.Structure_list_label,
                'x.c3') and check_subitem_in_list(
                M3.Structure_list_label, ':F3'):
                if M2.Price_range < M1.Price_range and M0.Price_range < M1.Price_range:
                    return
            # 2. 5-F3-s5-F3-L5 : (both F3's must be smaller than s5 and L5 must be longer than s5)
            if check_subitem_in_list(
                    M_1.Structure_list_label, ':5') and check_subitem_in_list(
                M0.Structure_list_label,
                ':F3') and check_subitem_in_list(
                M2.Structure_list_label,
                ':F3') and check_subitem_in_list(
                M3.Structure_list_label, ':L3'):
                if M2.Price_range < M1.Price_range and M0.Price_range < M1.Price_range and M3.Price_range > M1.Price_range:
                    return
            # 3. F3-c3-s5-x.c3-F3 : (both c3 and x.c3 must be smaller than s5; F3 will usually be larger than x.c3)
            if check_subitem_in_list(
                    M_1.Structure_list_label, ':F3') and check_subitem_in_list(
                M0.Structure_list_label,
                ':c3') and check_subitem_in_list(
                M2.Structure_list_label,
                ':x.c3') and check_subitem_in_list(
                M3.Structure_list_label, ':F3'):
                if M0.Price_range < M1.Price_range and M2.Price_range < M1.Price_range:  # and M3.Price_range > M2.Price_range
                    return

        HMW[i].Structure_list_label = remove_subitem_in_list(
            HMW[i].Structure_list_label, ':s5')

    def rem_L5(self, HMW, i):

        if not check_subitem_in_list(HMW[i].Structure_list_label, ':L5'):
            return

        n = len(HMW)
        M1 = HMW[i]
        M0 = HMW[i - 1] if (i - 1 >= 0) else None
        M_1 = HMW[i - 2] if (i - 2 >= 0) else None
        M2 = HMW[i + 1] if (i + 1 < n) else None
        M3 = HMW[i + 2] if (i + 2 < n) else None

        if M0 is not None and M2 is not None:

            # 1. 5-F3-L5-? : (F3 must be shorter than both 5 and L5; circle end of L5)
            if check_subitem_in_list(M_1.Structure_list_label, ':5') and check_subitem_in_list(M0.Structure_list_label,
                                                                                               ':F3'):
                if M0.Price_range < M_1.Price_range and M0.Price_range < M1.Price_range:
                    return
            # 2. s5-F3-L5-? : (LS must be longer than s5, (preferably L5 will be 161.8% or more of s5; circle end of L5))
            if check_subitem_in_list(M0.Structure_list_label, ':s5') and check_subitem_in_list(M1.Structure_list_label,
                                                                                               ':F3'):
                if M1.Price_range > M_1.Price_range:  # self.price_ratio(M1, M_1,  1 + fib_ratio)
                    return
            # 3. F3-c3-L5-? : (if c3 is 138.2% or more of F3, L5 will almost certainly be shorter than c3; circle end of LS)
            if check_subitem_in_list(M_1.Structure_list_label, ':F3') and check_subitem_in_list(M0.Structure_list_label,
                                                                                                ':c3'):
                if self.price_ratio(M0, M_1, 2 - fib_ratio) and M1.Price_range < M0.Price_range:
                    return
            # 4. F3-c3-L5-x.c3-F3 : (both c3 and x.c3 must be larger than L5, F3 must be smaller than x.c3)
            if M3 is not None:
                if check_subitem_in_list(M_1.Structure_list_label, ':F3') and check_subitem_in_list(
                        M0.Structure_list_label, ':c3') and check_subitem_in_list(M2.Structure_list_label,
                                                                                  'x.c3') and check_subitem_in_list(
                    M3.Structure_list_label, ':F3'):
                    if M0.Price_range > M1.Price_range and M2.Price_range > M1.Price_range and M3.Price_range < M2.Price_range:
                        return

        HMW[i].Structure_list_label = remove_subitem_in_list(HMW[i].Structure_list_label, ':L5')

    # endregion
    # page 55,56 pdf Glenn Neely
    def pattern_isolation(self, HMW):
        pairs = []
        for i in range(3, len(HMW)):
            M1 = HMW[i]

            # Todo : the first wave which contains only an ":L5" or an ":L3" or both
            if check_subitem_in_list(M1.Structure_list_label, ':L5') or check_subitem_in_list(M1.Structure_list_label,
                                                                                              ':L3'):

                M_2 = HMW[i - 3]
                M_1 = HMW[i - 2]
                M0 = HMW[i - 1]
                if check_subitem_in_list(M0.Structure_list_label, ':L3') or check_subitem_in_list(
                        M_1.Structure_list_label, ':L3') or check_subitem_in_list(M0.Structure_list_label,
                                                                                  ':L5') or check_subitem_in_list(
                    M_1.Structure_list_label, ':L5'):
                    continue
                if len(M_2.Structure_list_label) >= 1 and (
                        check_subitem_in_list(M_2.Structure_list_label, ':F3') or check_subitem_in_list(
                    M_2.Structure_list_label, 'x.c3') or check_subitem_in_list(M_2.Structure_list_label,
                                                                               ':L3') or check_subitem_in_list(
                    M_2.Structure_list_label, ':s5') or check_subitem_in_list(M_2.Structure_list_label, ':L5')):
                    pairs.append((i - 2, i))
                    continue

                for j in range(i - 4, -1, -1):
                    if len(HMW[j].Structure_list_label) >= 1 and check_subitem_in_list(HMW[j].Structure_list_label,
                                                                                       ':F3'):
                        if (i - j) % 2 == 0:
                            pairs.append((j, i))
                            break
                    if len(HMW[j].Structure_list_label) >= 1 and (
                            check_subitem_in_list(HMW[j].Structure_list_label, 'x.c3') or check_subitem_in_list(
                        HMW[j].Structure_list_label, ':L3') or check_subitem_in_list(HMW[j].Structure_list_label,
                                                                                     ':s5') or check_subitem_in_list(
                        HMW[j].Structure_list_label, ':L5')):
                        if (i - j) % 2 == 1:
                            pairs.append((j + 1, i))
                            break
        return pairs

    def save(self, path=".\\outputs\\"):
        self.monowaves.to_csv(path + 'monowaves.csv', index=False, encoding='utf-8', sep=';')

    def Flat_prediction_zone_label_Mc(self, hyper_monowaves):
        pred1_yc = []
        pred2_yc = []
        pred3_yc = []
        pred_xc = []
        pred_xb = []
        pred_yb = []
        hmw_index = []

        for index in range(len(hyper_monowaves) - 1):
            Ma = hyper_monowaves[index]
            Mb = hyper_monowaves[index + 1]

            if (check_subitem_in_list(Ma.Structure_list_label, '3') and check_subitem_in_list(Mb.Structure_list_label,
                                                                                              '3')
                    and not check_subitem_in_list(Ma.Structure_list_label, 'L3') and not check_subitem_in_list(
                        Ma.Structure_list_label, 'L5')
                    and not check_subitem_in_list(Mb.Structure_list_label, 'L3') and not check_subitem_in_list(
                        Mb.Structure_list_label, 'L5')):
                xb = Mb.End_candle_index
                yb = Mb.End_price

                if Ma.Duration < Mb.Duration and Mb.Price_range > 0.618 * Ma.Price_range:
                    if Ma.Duration + 1 >= Mb.Duration:
                        xc = xb + Ma.Duration + Mb.Duration
                        pred_xc.append(xc)
                    else:
                        xc = xb + int((Ma.Duration + Mb.Duration) / 2)
                        pred_xc.append(xc)

                    pred1_C_price_range = Ma.Price_range
                    pred2_C_price_range = 1.618 * Ma.Price_range
                    pred3_C_price_range = 2.618 * Ma.Price_range

                    pred1_C_end_price = yb + (pred1_C_price_range * Ma.Direction)
                    pred2_C_end_price = yb + (pred2_C_price_range * Ma.Direction)
                    pred3_C_end_price = yb + (pred3_C_price_range * Ma.Direction)

                    pred1_yc.append(pred1_C_end_price)
                    pred2_yc.append(pred2_C_end_price)
                    pred3_yc.append(pred3_C_end_price)
                    pred_xb.append(xb)
                    pred_yb.append(yb)

                    hmw_index.append(index)

        return hmw_index, pred_xb, pred_yb, pred_xc, pred1_yc, pred2_yc, pred3_yc

    def Zigzag_prediction_zone_label_Mc(self, hyper_monowaves):
        pred1_yc = []
        pred2_yc = []
        pred3_yc = []
        pred_xc = []
        pred_xb = []
        pred_yb = []
        hmw_index = []

        for index in range(len(hyper_monowaves) - 2):
            Ma = hyper_monowaves[index]
            Mb = hyper_monowaves[index + 1]

            if (check_subitem_in_list(Ma.Structure_list_label, '5') and check_subitem_in_list(Mb.Structure_list_label,
                                                                                              '3')
                    and not check_subitem_in_list(Ma.Structure_list_label, 'L3') and not check_subitem_in_list(
                        Ma.Structure_list_label, 'L5')
                    and not check_subitem_in_list(Mb.Structure_list_label, 'L3') and not check_subitem_in_list(
                        Mb.Structure_list_label, 'L5')):
                xb = Mb.End_candle_index
                yb = Mb.End_price
                ya = Ma.End_price

                if Ma.Duration <= Mb.Duration and Mb.Price_range <= 0.618 * Ma.Price_range:
                    xc = xb + Mb.Duration
                    pred_xc.append(xc)

                    pred1_C_price_range = 0.618 * Ma.Price_range
                    pred2_C_price_range = Ma.Price_range
                    pred3_C_price_range = 1.618 * Ma.Price_range

                    pred1_C_end_price = yb + (pred1_C_price_range * Ma.Direction)
                    if Ma.Direction > 0 and ya > yb + (pred1_C_price_range * Ma.Direction):
                        pred1_C_end_price = ya
                    elif Ma.Direction < 0 and ya < yb + (pred1_C_price_range * Ma.Direction):
                        pred1_C_end_price = ya

                    pred2_C_end_price = yb + (pred2_C_price_range * Ma.Direction)
                    pred3_C_end_price = yb + (pred3_C_price_range * Ma.Direction)

                    pred1_yc.append(pred1_C_end_price)
                    pred2_yc.append(pred2_C_end_price)
                    pred3_yc.append(pred3_C_end_price)
                    pred_xb.append(xb)
                    pred_yb.append(yb)

                    hmw_index.append(index)

        return hmw_index, pred_xb, pred_yb, pred_xc, pred1_yc, pred2_yc, pred3_yc

    def Impulse_In_prediction_zone_label_M4(self, hyper_monowaves, step):

        pred_y1 = []
        pred_y2 = []
        pred_y3 = []
        pred_y4 = []
        preds = []
        pred_x1 = []
        pred_x2 = []

        pred4_price_range2 = []
        pred4_price_range3 = []
        pred4_price_range4 = []
        start_candle_index = []
        start_price = []
        hmw_index = []
        validation = []
        ii = -1

        for index in range(len(hyper_monowaves) - 3):
            if index == 101:
                y = 1

            M1 = hyper_monowaves[index]
            M2 = hyper_monowaves[index + 1]
            M3 = hyper_monowaves[index + 2]

            if (check_subitem_in_list(M1.Structure_list_label, ':5') and check_subitem_in_list(M2.Structure_list_label,':F3')
                    and (check_subitem_in_list(M3.Structure_list_label, ':5') or check_subitem_in_list(M3.Structure_list_label, ':s5'))
                    and not check_subitem_in_list(M1.Structure_list_label, ':L3') and not check_subitem_in_list(M1.Structure_list_label, ':L5')
                    and not check_subitem_in_list(M2.Structure_list_label, ':L3') and not check_subitem_in_list(M2.Structure_list_label, ':L5')
                    and not check_subitem_in_list(M3.Structure_list_label, ':L3') and not check_subitem_in_list(M3.Structure_list_label, ':L5')
                    and M1.Price_range >= M2.Price_range and M2.Price_range <= M3.Price_range):
                start_x = M1.Start_candle_index
                start_y = M1.Start_price
                x1 = M3.End_candle_index
                y1 = M3.End_price
                x2 = x1 + int(step / 2)
                ii += 1
                pred4_price_range = abs(1 - M2.Price_range / M1.Price_range) * M3.Price_range
                # pred4_price_range2 = M2.Price_range
                # pred4_price_range2_1 = 1.62 * M2.Price_range
                # pred4_price_range3 = 0.382 * M3.Price_range
                # pred4_price_range3_1 = 0.5 * M3.Price_range
                # pred4_price_range3_2 = 0.618 * M3.Price_range
                # pred4_price_range4 = 0.236 * abs(M3.End_price - M1.Start_price)
                # pred4_price_range4_1 = 0.382 * abs(M3.End_price - M1.Start_price)
                # pred4_price_range4_2 = 0.5 * abs(M3.End_price - M1.Start_price)
                # pred4_price_range4_3 = 0.618 * abs(M3.End_price - M1.Start_price)

                pred4_price_range2.append([ratio * M2.Price_range for ratio in [1.0, 1.62]])
                pred4_price_range3.append([ratio * M3.Price_range for ratio in [0.382, 0.5, 0.618]])
                pred4_price_range4.append(
                    [ratio * abs(M3.End_price - M1.Start_price) for ratio in [0.236, 0.382, 0.5, 0.618]])

                # pred_y2.append([M3.End_price - M3.Direction * ratio * M2.Price_range for ratio in [1.0, 1.62]])
                # pred_y3.append([M3.End_price - M3.Direction * ratio * M3.Price_range for ratio in [0.382, 0.5, 0.618]])
                # pred_y4.append([M3.End_price - M3.Direction * ratio * abs(M3.End_price - M1.Start_price) for ratio in [0.236, 0.382, 0.5, 0.618]])
                # pred_y2.append([M3.End_price - M3.Direction * ratio * M2.Price_range for ratio in [0.62, 1.00]])
                # pred_y3.append([M3.End_price - M3.Direction * ratio * M3.Price_range for ratio in [0.236, 0.5]])
                # pred_y4.append([M3.End_price - M3.Direction * ratio * abs(M3.End_price - M1.Start_price) for ratio in [0.382]])

                pred_x1.append(x1)
                pred_x2.append(x2)
                start_candle_index.append(start_x)
                start_price.append(start_y)
                hmw_index.append(index)
                # pred_y.append(pred4_end_price)
                if pred4_price_range / M1.Price_range < 0.618 and pred4_price_range / M3.Price_range < (
                        M2.Price_range / M1.Price_range) \
                        and M3.Price_range >= pred4_price_range:
                    pred4_end_price1 = y1 - (pred4_price_range * M3.Direction)
                    pred_y1.append([pred4_end_price1])
                else:
                    pred_y1.append(["none"])

                pred_y_temp = []
                for i in range(2):
                    if pred4_price_range2[ii][i] / M1.Price_range < 0.618 and pred4_price_range2[ii][
                        i] / M3.Price_range < (M2.Price_range / M1.Price_range) \
                            and M3.Price_range >= pred4_price_range2[ii][i]:
                        pred4_end_price2 = M3.End_price - M3.Direction * pred4_price_range2[ii][i]
                        pred_y_temp.append(pred4_end_price2)
                    else:
                        pred_y_temp.append("none")
                pred_y2.append(pred_y_temp)

                pred_y_temp = []
                for i in range(3):
                    if pred4_price_range3[ii][i] / M1.Price_range < 0.618 and pred4_price_range3[ii][
                        i] / M3.Price_range < (M2.Price_range / M1.Price_range) \
                            and M3.Price_range >= pred4_price_range3[ii][i]:
                        pred4_end_price3 = M3.End_price - M3.Direction * pred4_price_range3[ii][i]
                        pred_y_temp.append(pred4_end_price3)
                    else:
                        pred_y_temp.append("none")
                pred_y3.append(pred_y_temp)

                pred_y_temp = []
                for i in range(4):
                    if pred4_price_range4[ii][i] / M1.Price_range < 0.618 and pred4_price_range4[ii][
                        i] / M3.Price_range < (M2.Price_range / M1.Price_range) \
                            and M3.Price_range >= pred4_price_range4[ii][i]:
                        pred4_end_price4 = M3.End_price - M3.Direction * pred4_price_range4[ii][i]
                        pred_y_temp.append(pred4_end_price4)
                    else:
                        pred_y_temp.append("none")
                pred_y4.append(pred_y_temp)

                # if pred4_price_range / M1.Price_range < 0.618:
                #     pred_y1.append(pred4_end_price)
                #     pred_x1.append(x1)
                #     pred_x2.append(x2)
                #     start_candle_index.append(start_x)
                #     start_price.append(start_y)
                #     hmw_index.append(index)
        preds.append(pred_y1)
        preds.append(pred_y2)
        preds.append(pred_y3)
        preds.append(pred_y4)
        # return hmw_index, pred_x1, pred_x2, pred_y1, pred_y2, pred_y3, pred_y4
        return hmw_index, pred_x1, pred_x2, preds

    def Impulse_In_prediction_zone_label_M5_truncated(self, hyper_monowaves, step):

        pred_y = []
        pred_x1 = []
        pred_x2 = []
        start_candle_index = []
        start_price = []
        hmw_index = []
        validation = []

        for index in range(len(hyper_monowaves) - 4):

            M1 = hyper_monowaves[index]
            M2 = hyper_monowaves[index + 1]
            M3 = hyper_monowaves[index + 2]
            M4 = hyper_monowaves[index + 2]

            if (check_subitem_in_list(M1.Structure_list_label, ':5') and check_subitem_in_list(M2.Structure_list_label,
                                                                                               ':F3') and
                    (check_subitem_in_list(M3.Structure_list_label, ':5') or check_subitem_in_list(
                        M3.Structure_list_label, ':s5')) and
                    check_subitem_in_list(M3.Structure_list_label, ':F3')):
                start_x = M1.Start_candle_index
                start_y = M1.Start_price
                x1 = M4.End_candle_index
                y1 = M4.End_price
                x2 = x1 + int(step / 2)

                if (M1.Price_range < M3.Price_range and
                        M4.Price_range > M2.Price_range and
                        0.318 <= M4.Price_range / M3.Price_range <= (0.618 + 0.02)):
                    pred5_end_price = M3.End_price
                    pred_y.append(pred5_end_price)
                    pred_x1.append(x1)
                    pred_x2.append(x2)
                    start_candle_index.append(start_x)
                    start_price.append(start_y)
                    hmw_index.append(index)

        return hmw_index, pred_x1, pred_x2, pred_y


def Impulse_In_prediction_zone_label_M5(self, hyper_monowaves, step):
    pred_y1 = []
    pred_y2 = []
    pred_y3 = []
    pred_y4 = []
    preds = []
    pred_x1 = []
    pred_x2 = []
    pred5_price_range1 = []
    pred5_price_range2 = []
    pred5_price_range3 = []
    pred5_price_range4 = []
    start_candle_index = []
    start_price = []
    hmw_index = []
    validation = []
    ii = -1

    for index in range(len(hyper_monowaves) - 3):
        if index == 101:
            y = 1

        M1 = hyper_monowaves[index]
        M2 = hyper_monowaves[index + 1]
        M3 = hyper_monowaves[index + 2]
        M4 = hyper_monowaves[index + 3]

        if (check_subitem_in_list(M1.Structure_list_label, ':5') and check_subitem_in_list(M2.Structure_list_label,
                                                                                           ':F3') and
                (check_subitem_in_list(M3.Structure_list_label, ':5') or check_subitem_in_list(M3.Structure_list_label,
                                                                                               ':s5')) and
                check_subitem_in_list(M3.Structure_list_label, ':F3')):

            start_x = M1.Start_candle_index
            start_y = M1.Start_price
            x1 = M4.End_candle_index
            y1 = M4.End_price
            x2 = x1 + int(step / 2)
            ii += 1

            # pred4_price_range2 = M2.Price_range
            # pred4_price_range2_1 = 1.62 * M2.Price_range
            # pred4_price_range3 = 0.382 * M3.Price_range
            # pred5_price_range3_1 = 0.5 * M3.Price_range
            # pred5_price_range3_2 = 0.618 * M3.Price_range
            # pred4_price_range4 = 0.236 * abs(M3.End_price - M1.Start_price)
            # pred5_price_range4_1 = 0.382 * abs(M3.End_price - M1.Start_price)
            # pred5_price_range4_2 = 0.5 * abs(M3.End_price - M1.Start_price)
            # pred5_price_range4_3 = 0.618 * abs(M3.End_price - M1.Start_price)

            pred5_price_range1.append([ratio * M1.Price_range for ratio in [1.0, 1.62]])
            pred5_price_range2.append([ratio * abs(M3.End_price - M1.Start_price) for ratio in [0.382, 0.618, 1.0]])
            pred5_price_range3.append([ratio * M4.Price_range for ratio in [1.27, 1.62]])
            pred5_price_range4.append([ratio * M2.Price_range for ratio in [2.62, 4.24]])
            # pred_y2.append([M3.End_price - M3.Direction * ratio * M2.Price_range for ratio in [1.0, 1.62]])
            # pred_y3.append([M3.End_price - M3.Direction * ratio * M3.Price_range for ratio in [0.382, 0.5, 0.618]])
            # pred_y4.append([M3.End_price - M3.Direction * ratio * abs(M3.End_price - M1.Start_price) for ratio in [0.236, 0.382, 0.5, 0.618]])
            # pred_y2.append([M3.End_price - M3.Direction * ratio * M2.Price_range for ratio in [0.62, 1.00]])
            # pred_y3.append([M3.End_price - M3.Direction * ratio * M3.Price_range for ratio in [0.236, 0.5]])
            # pred_y4.append([M3.End_price - M3.Direction * ratio * abs(M3.End_price - M1.Start_price) for ratio in [0.382]])

            pred_x1.append(x1)
            pred_x2.append(x2)
            start_candle_index.append(start_x)
            start_price.append(start_y)
            hmw_index.append(index)
            # pred_y.append(pred4_end_price)
            if pred5_price_range1 / M1.Price_range < 0.618 and pred5_price_range1 / M3.Price_range < (
                    M2.Price_range / M1.Price_range) \
                    and M3.Price_range >= pred5_price_range1:
                pred4_end_price1 = y1 - (pred5_price_range1 * M3.Direction)
                pred_y1.append([pred4_end_price1])
            else:
                pred_y1.append(["none"])

            pred_y_temp = []
            for i in range(2):
                if pred5_price_range2[ii][i] / M1.Price_range < 0.618 and pred5_price_range2[ii][i] / M3.Price_range < (
                        M2.Price_range / M1.Price_range) \
                        and M3.Price_range >= pred5_price_range2[ii][i]:
                    pred4_end_price2 = M3.End_price - M3.Direction * pred5_price_range2[ii][i]
                    pred_y_temp.append(pred4_end_price2)
                else:
                    pred_y_temp.append("none")
            pred_y2.append(pred_y_temp)

            pred_y_temp = []
            for i in range(3):
                if pred5_price_range3[ii][i] / M1.Price_range < 0.618 and pred5_price_range3[ii][i] / M3.Price_range < (
                        M2.Price_range / M1.Price_range) \
                        and M3.Price_range >= pred5_price_range3[ii][i]:
                    pred4_end_price3 = M3.End_price - M3.Direction * pred5_price_range3[ii][i]
                    pred_y_temp.append(pred4_end_price3)
                else:
                    pred_y_temp.append("none")
            pred_y3.append(pred_y_temp)

            pred_y_temp = []
            for i in range(4):
                if pred5_price_range4[ii][i] / M1.Price_range < 0.618 and pred5_price_range4[ii][i] / M3.Price_range < (
                        M2.Price_range / M1.Price_range) \
                        and M3.Price_range >= pred5_price_range4[ii][i]:
                    pred4_end_price4 = M3.End_price - M3.Direction * pred5_price_range4[ii][i]
                    pred_y_temp.append(pred4_end_price4)
                else:
                    pred_y_temp.append("none")
            pred_y4.append(pred_y_temp)

            # if pred5_price_range / M1.Price_range < 0.618:
            #     pred_y1.append(pred4_end_price)
            #     pred_x1.append(x1)
            #     pred_x2.append(x2)
            #     start_candle_index.append(start_x)
            #     start_price.append(start_y)
            #     hmw_index.append(index)
    preds.append(pred_y1)
    preds.append(pred_y2)
    preds.append(pred_y3)
    preds.append(pred_y4)
    # return hmw_index, pred_x1, pred_x2, pred_y1, pred_y2, pred_y3, pred_y4
    return hmw_index, pred_x1, pred_x2, preds

# pred_list.append([W4.End_price + W3.Direction * ratio * W1.Price_range for ratio in [1.0, 1.62]])
# pred_list.append([W4.End_price + W3.Direction * ratio * abs(W3.End_price - W1.Start_price) for ratio in [0.382, 0.618, 1.0]])
# pred_list.append([W4.End_price + W3.Direction * ratio * W4.Price_range for ratio in [1.27, 1.62]])
# pred_list.append([W2.End_price + W3.Direction * ratio * W2.Price_range for ratio in [2.62, 4.24]])
