import copy
import numpy as np

from AlgorithmFactory.AlgorithmTools.Elliott.utility import *
from AlgorithmFactory.AlgorithmTools.Elliott.mw_utils import *


class PolyWave:
    def __init__(self, monoWaveList):

        self.monowavesList = monoWaveList

        self.cols = ['PWstartIndex', 'PWendIndex', 'countWave', 'EW_structure',
                     'Validation', 'ExtensionWaveIndex', 'FiboRelatedWaves', 'PostConfirmation', 'EW_type']
        self.types = [np.int, np.int, np.int, np.object, np.bool, np.int, np.bool, np.bool, np.object]
        self.default = {'PWstartIndex': 0, 'PWendIndex': 0, 'countWave': 0, 'EW_structure': [],
                        'Validation': True, 'ExtensionWaveIndex': 0, 'FiboRelatedWaves': False,
                        'PostConfirmation': False, 'EW_type': []}
        # self.polywave_list = pd.DataFrame(columns=cols)
        self.polywaveList = df_empty(self.cols, self.types)

    def build_polywave(self, pairs: list):
        for i in range(0, len(pairs)):
            start = pairs[i][0]
            end = pairs[i][1]
            count = end - start + 1
            vals = {'PWstartIndex': start, 'PWendIndex': end, 'countWave': count}
            default_vals = copy.deepcopy({**self.default, **vals})
            self.polywaveList = self.polywaveList.append(default_vals, ignore_index=True)

    def save(self, path=".\\outputs\\", fname="polywaves"):
        """Save Polywaves to CSV file"""
        start_candle_idx = []
        end_candle_idx = []
        start_price = []
        end_price = []

        for i in range(len(self.polywaveList)):
            start_i = self.polywaveList.loc[i].PWstartIndex
            end_i = self.polywaveList.loc[i].PWendIndex
            start_candle_idx.append(self.monowavesList[start_i].Start_candle_index)
            end_candle_idx.append(self.monowavesList[end_i].End_candle_index)
            start_price.append(self.monowavesList[start_i].Start_price)
            end_price.append(self.monowavesList[end_i].End_price)

        self.polywaveList["Start_candle_index"] = start_candle_idx
        self.polywaveList["End_candle_index"] = end_candle_idx
        self.polywaveList["Start_price"] = start_price
        self.polywaveList["End_price"] = end_price

        self.polywaveList.to_csv(path + fname + ".csv", index=False, encoding='utf-8', sep=';')

    def visualize_valid_polywave(self):
        """copy valid polywaves having EW_Type"""
        start_candle_idx = []
        end_candle_idx = []
        start_price = []
        end_price = []
        ew_type = []

        pred_x1 = []
        pred_x2 = []
        pred_y1 = []
        pred_y2 = []
        pred_y3 = []

        for i in range(len(self.polywaveList)):
            if self.polywaveList.loc[i].EW_type != []:
                start_i = self.polywaveList.loc[i].PWstartIndex
                end_i = self.polywaveList.loc[i].PWendIndex
                start_candle_idx.append(self.monowavesList[start_i].Start_candle_index)
                end_candle_idx.append(self.monowavesList[end_i].End_candle_index)
                start_price.append(self.monowavesList[start_i].Start_price)
                end_price.append(self.monowavesList[end_i].End_price)
                ew_type.append(self.polywaveList.loc[i].EW_type)

                if check_subitem_in_list(self.polywaveList.loc[i, 'EW_type'], 'Impulse'):
                    res = self.impulsions_prediction(i)
                    pred_x1.append(res[0])
                    pred_x2.append(res[1])
                    pred_y1.append(res[2])
                    pred_y2.append(res[3])
                    pred_y3.append(res[4])

                elif check_subitem_in_list(self.polywaveList.loc[i, 'EW_type'], 'Flat') or check_subitem_in_list(
                        self.polywaveList.loc[i, 'EW_type'], 'Zigzag'):
                    res = self.flat_zigzag_prediction(i)
                    pred_x1.append(res[0])
                    pred_x2.append(res[1])
                    pred_y1.append(res[2])
                    pred_y2.append(res[3])
                    pred_y3.append(res[4])

        return start_candle_idx, end_candle_idx, start_price, end_price, ew_type, pred_x1, pred_x2, pred_y1, pred_y2, pred_y3

    def candidate_patterns(self):
        n = len(self.polywaveList)
        for i in range(n):
            idx = self.polywaveList.loc[i].PWstartIndex

            M0 = self.monowavesList[idx]
            M1 = self.monowavesList[idx + 1]
            M2 = self.monowavesList[idx + 2]

            if self.polywaveList.loc[i].countWave == 5:

                M3 = self.monowavesList[idx + 3]
                M4 = self.monowavesList[idx + 4]

                if not self.balance_similarity(M0, M1, M2, M3, M4):
                    self.polywaveList.loc[i, 'Validation'] = False

                if (check_subitem_in_list(M0.Structure_list_label, ':5') and check_subitem_in_list(
                        M1.Structure_list_label, ':F3') and
                        (check_subitem_in_list(M2.Structure_list_label, ':5') or check_subitem_in_list(
                            M2.Structure_list_label, ':s5')) and
                        check_subitem_in_list(M3.Structure_list_label, ':F3') and check_subitem_in_list(
                            M4.Structure_list_label, ':L5')):
                    self.polywaveList.loc[i, 'EW_type'].append('Impulse')

                if (check_subitem_in_list(M0.Structure_list_label, ':F3') and check_subitem_in_list(
                        M1.Structure_list_label, ':c3') and
                        check_subitem_in_list(M2.Structure_list_label, ':c3') and (
                                check_subitem_in_list(M3.Structure_list_label, '3') and
                                not check_subitem_in_list(M3.Structure_list_label, 'x.c3')) and (
                                check_subitem_in_list(M4.Structure_list_label, '3') and
                                not check_subitem_in_list(M4.Structure_list_label, 'x.c3'))):

                    self.polywaveList.loc[i, 'EW_type'].append('Triangle')

                    if check_subitem_in_list(M4.Structure_list_label, ':L3'):
                        start = self.polywaveList.loc[i].PWstartIndex
                        end = self.polywaveList.loc[i].PWendIndex
                        count = end - start + 1
                        valid = self.polywaveList.loc[i].Validation
                        vals = {'PWstartIndex': start, 'PWendIndex': end, 'countWave': count, 'EW_type': ['Terminal'],
                                'Validation': valid}
                        default_vals = copy.deepcopy({**self.default, **vals})
                        self.polywaveList = self.polywaveList.append(default_vals, ignore_index=True)

            if self.polywaveList.loc[i].countWave == 3:

                if not self.balance_similarity(M0, M1, M2):
                    self.polywaveList.loc[i, 'Validation'] = False
                # (":?5") -> ? should be something -> end of zigzag could be :s5 or :L5 and not :5
                if (check_subitem_in_list(M0.Structure_list_label, ':5') and check_subitem_in_list(
                        M1.Structure_list_label, ':F3') and
                        (check_subitem_in_list(M2.Structure_list_label, ':s5') or check_subitem_in_list(
                            M2.Structure_list_label, ':L5'))):
                    self.polywaveList.loc[i, 'EW_type'].append('Zigzag')
                    self.zigzag_detour(i)

                if (check_subitem_in_list(M0.Structure_list_label, ':F3') and check_subitem_in_list(
                        M1.Structure_list_label, ':c3') and
                        check_subitem_in_list(M2.Structure_list_label, '5')):
                    self.polywaveList.loc[i, 'EW_type'].append('Flat')

    def balance_similarity(self, M0, M1, M2, M3=None, M4=None):

        if M3 is None and M4 is None:
            if ((compare_ratio_waves(M0.Price_range, M1.Price_range, 1 / 3) or compare_ratio_waves(M0.Duration,
                                                                                                   M1.Duration, 1 / 3))
                    and (compare_ratio_waves(M1.Price_range, M2.Price_range, 1 / 3) or compare_ratio_waves(M1.Duration,
                                                                                                           M2.Duration,
                                                                                                           1 / 3))):
                return True

        if M3 is not None and M4 is not None:
            if ((compare_ratio_waves(M0.Price_range, M1.Price_range, 1 / 3) or compare_ratio_waves(M0.Duration,
                                                                                                   M1.Duration, 1 / 3))
                    and (compare_ratio_waves(M1.Price_range, M2.Price_range, 1 / 3) or compare_ratio_waves(M1.Duration,
                                                                                                           M2.Duration,
                                                                                                           1 / 3))
                    and (compare_ratio_waves(M2.Price_range, M3.Price_range, 1 / 3) or compare_ratio_waves(M2.Duration,
                                                                                                           M3.Duration,
                                                                                                           1 / 3))
                    and (compare_ratio_waves(M3.Price_range, M4.Price_range, 1 / 3) or compare_ratio_waves(M3.Duration,
                                                                                                           M4.Duration,
                                                                                                           1 / 3))):
                return True

        return False

    def zigzag_detour(self, index):

        start = self.polywaveList.loc[index].PWstartIndex - 2

        M_2 = self.monowavesList[start] if (start >= 0) else None
        M_1 = self.monowavesList[start + 1] if (start + 1 >= 0) else None

        M0 = self.monowavesList[start + 2]
        M1 = self.monowavesList[start + 3]
        M2 = self.monowavesList[start + 4]

        if M_2 is not None and check_subitem_in_list(M2.Structure_list_label,
                                                     ':L5'):  # End of Impulse can not be s5 and must be L5
            if check_subitem_in_list(M_2.Structure_list_label, ':5') and check_subitem_in_list(M_1.Structure_list_label,
                                                                                               ':F3'):

                valid = True
                if not self.balance_similarity(M_2, M_1, M0, M1, M2):
                    valid = False

                end = self.polywaveList.loc[index].PWendIndex
                count = end - start + 1
                vals = {'PWstartIndex': start, 'PWendIndex': end, 'countWave': count, 'EW_type': ['Impulse'],
                        'Validation': valid}
                default_vals = copy.deepcopy({**self.default, **vals})
                self.polywaveList = self.polywaveList.append(default_vals, ignore_index=True)

    def analyzing_rules(self):
        valid_pairs = []
        for i in range(len(self.polywaveList)):
            if len(self.polywaveList.loc[i, 'EW_type']) == 0:
                self.polywaveList.loc[i, 'Validation'] = False

            if (check_subitem_in_list(self.polywaveList.loc[i, 'EW_type'], 'Impulse') or
                    check_subitem_in_list(self.polywaveList.loc[i, 'EW_type'], 'Terminal')):
                self.impulsion_essential_construction_rule(i)  # change the validation value
                self.impulsion_extension_rule(i)  # change the validation value
                self.impulsion_alternation_rule(i)  # change the validation value
                self.impulsion_equality_rule(i)  # change the validation value
                self.impulsion_overlap_rule(i)  # change the validation value
                self.impulsion_fibo_rel_rule(i)  # change the fib-rel value
                self.impulsions_post_confirmation(i)  # change the post_confirmation value

            if check_subitem_in_list(self.polywaveList.loc[i, 'EW_type'], 'Triangle'):
                self.Triangle(i)  # change the validation value
                self.triangle_fibo_rel_rule(i)  # change the fib-rel value
                self.contracting_triangle_post_confirmation(i)  # change the post_confirmation value
            if check_subitem_in_list(self.polywaveList.loc[i, 'EW_type'], 'Flat'):
                self.Flat(i)  # change the validation value
                self.flat_fibo_rel_rule(i)  # change the fib-rel value
                self.flat_zigzag_post_confirmation(i)  # change the post_confirmation value
            if check_subitem_in_list(self.polywaveList.loc[i, 'EW_type'], 'Zigzag'):
                self.Zigzag(i)  # change the validation value
                self.zigzag_fibo_rel_rule(i)  # change the fib-rel value
                self.flat_zigzag_post_confirmation(i)  # change the post_confirmation value

            if self.polywaveList.loc[
                i, 'Validation']:  # and self.polywaveList.loc[i,'FiboRelatedWaves'] and self.polywaveList.loc[i,'PostConfirmation']:
                valid_pairs.append((self.polywaveList.loc[i].PWstartIndex, self.polywaveList.loc[i].PWendIndex))

        return valid_pairs

    def impulsion_essential_construction_rule(self, index):
        stIndex = self.polywaveList.loc[index].PWstartIndex

        M1 = self.monowavesList[stIndex]
        M2 = self.monowavesList[stIndex + 1]
        M3 = self.monowavesList[stIndex + 2]
        M4 = self.monowavesList[stIndex + 3]
        M5 = self.monowavesList[stIndex + 4]

        if M1.Price_range <= M2.Price_range or M2.Price_range >= M3.Price_range or M3.Price_range <= M4.Price_range:
            self.polywaveList.loc[index, 'Validation'] = False

        elif M3.Price_range < M1.Price_range and M3.Price_range < M5.Price_range:
            self.polywaveList.loc[index, 'Validation'] = False

        elif M5.Price_range < (1 - fib_ratio) * M4.Price_range:
            self.polywaveList.loc[index, 'Validation'] = False

        elif M5.Price_range < M4.Price_range:
            self.polywaveList.loc[index, 'EW_structure'].append('5th wave Failure')

    def impulsion_extension_rule(self, index):
        stIndex = self.polywaveList.loc[index].PWstartIndex

        M1 = self.monowavesList[stIndex]
        M3 = self.monowavesList[stIndex + 2]
        M5 = self.monowavesList[stIndex + 4]

        HMPriceList = [M1.Price_range, M3.Price_range, M5.Price_range]

        twoLargestIndex = sorted(range(len(HMPriceList)), key=lambda sub: HMPriceList[sub])[-2:]

        largestWavePrice = HMPriceList[twoLargestIndex[1]]
        secLargestWavePrice = HMPriceList[twoLargestIndex[0]]

        # if index: 0 -> Wave: 1, index: 1 -> Wave: 3, index: 2 -> Wave: 5
        self.polywaveList.loc[index, 'ExtensionWaveIndex'] = twoLargestIndex[1] * 2 + 1

        if largestWavePrice >= 1.618 * secLargestWavePrice:
            return

        # if The First wave is the Longest wave
        if self.polywaveList.loc[index].ExtensionWaveIndex == 1:
            if 0.618 * M1.Price_range + M1.End_price > M3.End_price:
                return

        # if The third wave is the Longest wave
        if self.polywaveList.loc[index].ExtensionWaveIndex == 3:
            if 1.618 * M1.Price_range > M3.Price_range:
                return

        self.polywaveList.loc[index, 'Validation'] = False

    def impulsion_alternation_rule(self, index):
        # TODO: Condition of "Intricacy" and "Construction" must be implemented

        stIndex = self.polywaveList.loc[index].PWstartIndex

        M1 = self.monowavesList[stIndex]
        M2 = self.monowavesList[stIndex + 1]
        M3 = self.monowavesList[stIndex + 2]
        M4 = self.monowavesList[stIndex + 3]

        if compare_ratio_waves(M2.Price_range, M4.Price_range, fib_ratio, True) or compare_ratio_waves(M2.Duration,
                                                                                                       M4.Duration,
                                                                                                       fib_ratio, True):
            return

        W2_RetracedRatio = M2.Price_range / M1.Price_range
        W4_RetracedRatio = M4.Price_range / M3.Price_range

        if compare_ratio_waves(W2_RetracedRatio, W4_RetracedRatio, fib_ratio, True):
            return

        self.polywaveList.loc[index, 'Validation'] = False

    def impulsion_equality_rule(self, index):
        stIndex = self.polywaveList.loc[index].PWstartIndex

        M1 = self.monowavesList[stIndex]
        M3 = self.monowavesList[stIndex + 2]
        M5 = self.monowavesList[stIndex + 4]

        if self.polywaveList.loc[index].ExtensionWaveIndex == 1:
            if (waves_are_fib_related(M3.Price_range, M5.Price_range, 1) or waves_are_fib_related(M3.Duration,
                                                                                                  M5.Duration, 1) or
                    waves_are_fib_related(M3.Price_range, M5.Price_range) or waves_are_fib_related(M3.Duration,
                                                                                                   M5.Duration)):
                return

        elif self.polywaveList.loc[index].ExtensionWaveIndex == 3:
            if (waves_are_fib_related(M1.Price_range, M5.Price_range, 1) or waves_are_fib_related(M1.Duration,
                                                                                                  M5.Duration, 1) or
                    waves_are_fib_related(M1.Price_range, M5.Price_range) or waves_are_fib_related(M1.Duration,
                                                                                                   M5.Duration)):
                return

        elif self.polywaveList.loc[index].ExtensionWaveIndex == 5:
            if (waves_are_fib_related(M1.Price_range, M3.Price_range, 1) or waves_are_fib_related(M1.Duration,
                                                                                                  M3.Duration, 1) or
                    waves_are_fib_related(M1.Price_range, M3.Price_range) or waves_are_fib_related(M1.Duration,
                                                                                                   M3.Duration)):
                return

        self.polywaveList.loc[index, 'Validation'] = False

    def impulsion_overlap_rule(self, index):
        stIndex = self.polywaveList.loc[index].PWstartIndex

        M2 = self.monowavesList[stIndex + 1]
        M4 = self.monowavesList[stIndex + 3]

        if ((check_subitem_in_list(self.polywaveList.loc[index, 'EW_type'], 'Impulse') and not wave_overlap(M2, M4))
                or (check_subitem_in_list(self.polywaveList.loc[index, 'EW_type'], 'Terminal') and wave_overlap(M2,
                                                                                                                M4))):
            return

        self.polywaveList.loc[index, 'Validation'] = False

    def impulsion_fibo_rel_rule(self, index):
        stIndex = self.polywaveList.loc[index].PWstartIndex

        M1 = self.monowavesList[stIndex]
        M3 = self.monowavesList[stIndex + 2]
        M4 = self.monowavesList[stIndex + 3]
        M5 = self.monowavesList[stIndex + 4]

        if self.polywaveList.loc[index].ExtensionWaveIndex == 1:
            if ((waves_are_fib_related(M3.Price_range, M1.Price_range, fib_ratio, True) and
                 waves_are_fib_related(M5.Price_range, M3.Price_range, 1 - fib_ratio, True)) or
                    (waves_are_fib_related(M3.Price_range, M1.Price_range, 1 - fib_ratio, True)) and
                    waves_are_fib_related(M5.Price_range, M3.Price_range, fib_ratio, True)):
                self.polywaveList.loc[index, 'FiboRelatedWaves'] = True

        elif self.polywaveList.loc[index].ExtensionWaveIndex == 3:
            if (M3.Price_range >= (1 + fib_ratio) * M1.Price_range and (
                    waves_are_fib_related(M1.Price_range, M5.Price_range, 1) or
                    waves_are_fib_related(M1.Price_range, M5.Price_range, fib_ratio))):
                self.polywaveList.loc[index, 'FiboRelatedWaves'] = True

        elif self.polywaveList.loc[index].ExtensionWaveIndex == 5:
            price_M1_to_M4 = abs(M4.End_price - M1.Start_price)
            if (M1.Price_range < M3.Price_range and waves_are_fib_related(M1.Price_range, M3.Price_range, fib_ratio) and
                    M5.Price_range > (1 + fib_ratio) * price_M1_to_M4):
                self.polywaveList.loc[index, 'FiboRelatedWaves'] = True

    def Flat(self, index):
        stIndex = self.polywaveList.loc[index].PWstartIndex

        Ma = self.monowavesList[stIndex]
        Mb = self.monowavesList[stIndex + 1]
        Mc = self.monowavesList[stIndex + 2]

        if Ma.Price_range * fib_ratio > Mb.Price_range:
            self.polywaveList.loc[index, 'Validation'] = False
            return
        if Ma.Price_range * 1.618 > Mc.Price_range:
            self.polywaveList.loc[index, 'Validation'] = False
            return

        if 1.01 * Ma.Price_range <= Mb.Price_range <= 1.236 * Ma.Price_range:
            if Mc.Price_range >= Mb.Price_range and Mc.Price_range < (1 + fib_ratio) * Ma.Price_range:
                self.polywaveList.loc[index, 'EW_structure'].append('Strong B-Wave: Irregular')
                return

            if Mc.Price_range > 1.618 * Ma.Price_range:
                self.polywaveList.loc[index, 'EW_structure'].append('Strong B-Wave: Elongated')
                return

        if 1.236 * Ma.Price_range <= Mb.Price_range < 1.38 * Ma.Price_range:
            if Mc.Price_range > Mb.Price_range:
                self.polywaveList.loc[index, 'EW_structure'].append('Strong B-Wave: Irregular')
                return
            if wave_end_inside_channel(Ma, Mc) and Mc.Price_range < Mb.Price_range:
                self.polywaveList.loc[index, 'EW_structure'].append('Strong B-Wave: Irregular Failure')
                return
            if not wave_end_inside_channel(Ma, Mc):
                self.polywaveList.loc[index, 'EW_structure'].append('Strong B-Wave: Running Correction')
                return

        if Mb.Price_range >= 1.38 * Ma.Price_range:  # (the c-wave of a Triangle might retrace all of wave-b, but not the c-wave of a Flat)
            self.polywaveList.loc[index, 'Validation'] = False
            return

        if 0.81 * Ma.Price_range <= Mb.Price_range <= Ma.Price_range:
            if Mc.Price_range < Mb.Price_range:
                self.polywaveList.loc[index, 'EW_structure'].append('Normal B-Wave: C-Failure')
                return
            if Mb.Price_range <= Mc.Price_range <= 1.38 * Mb.Price_range:
                self.polywaveList.loc[index, 'EW_structure'].append('Normal B-Wave: Common')
                return
            if Mc.Price_range > 1.38 * Mb.Price_range:
                self.polywaveList.loc[index, 'EW_structure'].append('Normal B-Wave: Elongated')
                return

        if 0.618 * Ma.Price_range <= Mb.Price_range <= 0.8 * Ma.Price_range:
            if Mc.Price_range < Mb.Price_range:
                self.polywaveList.loc[index, 'EW_structure'].append('Weak B-Wave: Double-Failure')
                return
            if Mb.Price_range <= Mc.Price_range <= 1.38 * Mb.Price_range:
                self.polywaveList.loc[index, 'EW_structure'].append('Weak B-Wave: B-Failure')
                return
            if Mc.Price_range > 1.38 * Mb.Price_range:
                self.polywaveList.loc[index, 'EW_structure'].append('Weak B-Wave: Elongated')
                return

    def Zigzag(self, index):
        stIndex = self.polywaveList.loc[index].PWstartIndex

        Ma = self.monowavesList[stIndex]
        Mb = self.monowavesList[stIndex + 1]
        Mc = self.monowavesList[stIndex + 2]

        # TODO: Ma should be retrace less than 0.618 previous Impulse wave of one larger degree
        # TODO: checking max and min for polywaves' domain
        if 0.01 < Mb.Price_range / Ma.Price_range and wave_beyond(Ma,
                                                                  Mc) and Mb.Price_range / Ma.Price_range < fib_ratio:
            if fib_ratio < Mc.Price_range / Ma.Price_range:
                if (Mc.Direction == 1 and Mc.End_price < Ma.End_price + 1.618 * Ma.Price_range) or (
                        Mc.Direction == -1 and Mc.End_price > Ma.End_price + 1.618 * Ma.Price_range):
                    self.polywaveList.loc[index, 'EW_structure'].append('Normal')
                    return
            if 0.38 < Mc.Price_range / Ma.Price_range < 0.618:
                self.polywaveList.loc[index, 'EW_structure'].append('Truncated')
                # TODO: In this case, Market must retrace at least 81% of entire Zigzag
                return
            if (Mc.Direction == 1 and Mc.End_price > Ma.End_price + 1.618 * Ma.Price_range) or (
                    Mc.Direction == -1 and Mc.End_price < Ma.End_price + 1.618 * Ma.Price_range):
                self.polywaveList.loc[index, 'EW_structure'].append('Elongated')
                # TODO: After an Elongated Zigzag, the market should retrace more than 61.8% of the c-wave
                return
        else:
            self.polywaveList.loc[index, 'Validation'] = False

    def Triangle(self, index):
        stIndex = self.polywaveList.loc[index].PWstartIndex

        Ma = self.monowavesList[stIndex]
        Mb = self.monowavesList[stIndex + 1]
        Mc = self.monowavesList[stIndex + 2]
        Md = self.monowavesList[stIndex + 3]
        Me = self.monowavesList[stIndex + 4]

        hmw = [Ma, Mb, Mc, Md, Me]
        hmw_price_range = [Ma.Price_range, Mb.Price_range, Mc.Price_range, Md.Price_range, Me.Price_range]

        # 5. The length of wave-b must fall between 38.2-261.8% of wave-a
        if 0.382 * Ma.Price_range < Mb.Price_range < 2.618 * Ma.Price_range:
            # 6. Of the five segments in a Triangle, four retrace a previous segment. Of those four, three segments must retrace at least 50% of the previous wave
            cond_list_contracting = []
            cond_list_expanding = []
            for i in range(4):
                cond_list_contracting.append(hmw_price_range[i + 1] > 0.5 * hmw_price_range[i])
                cond_list_expanding.append(hmw_price_range[i + 1] < 0.5 * hmw_price_range[i])

            if sum(cond_list_contracting) < 3 and sum(cond_list_expanding) < 3:
                return

            # 8. the B-D trendline should not be broken by any part of wave C or E in the Triangle
            if beyond_trendline(Mb, Md, Mc) or beyond_trendline(Mb, Md,
                                                                Me):  # TODO or beyond_trendline(Ma, Mc, Mb) or beyond_trendline(Ma, Mc, Md):
                self.polywaveList.loc[index, 'Validation'] = False
                return

            thrust = self.monowavesList[stIndex + 5] if (stIndex + 5) < len(self.monowavesList) else None

            if thrust is None:
                return

            widest_segment_price = max(hmw_price_range)
            widest_segment_index = np.argmax(hmw_price_range)

            # Contracting Triangles:
            # 1. "thrust" must be at least 75% of the widest segment of the Triangle and will not exceed 125% of the widest segment
            if 0.75 * widest_segment_price <= thrust.Price_range <= 1.25 * widest_segment_price:
                if thrust.Direction == -1:
                    exit_price_triangle = min(Mb.End_price, Md.End_price)
                else:
                    exit_price_triangle = max(Mb.End_price, Md.End_price)

                # 2. thrust must exceed the highest or lowest price achieved during the formation of the triangle
                if thrust.Direction * (thrust.End_price - exit_price_triangle) > 0:

                    # 3. The e-wave must be the smallest wave in the Triangle
                    if sum(cond_list_contracting) >= 3 and np.argmin(hmw_price_range) == 4:  # e-wave is smallest wave
                        self.polywaveList.loc[index, 'EW_structure'].append('Contracting')

                        apex_time_index, apex_price = self.apex(Ma, Mb, Mc, Md)

                        time_duration = Me.End_candle_index - Ma.Start_candle_index

                        # Limiting Triangle: the termination of wave-e should occur from 20-40% before the apex point of the Triangle
                        if Me.End_candle_index + 0.2 * time_duration <= apex_time_index <= Me.End_candle_index + 0.4 * time_duration:
                            self.polywaveList.loc[index, 'EW_structure'].append('Limiting')

                            # TODO: 1. The trendlines of the Triangle must travel in opposite price directions

                            # 2.The Apex point must fall within a range 61.8% of the longest segment of the Triangle, centered in the middle of the longest segment
                            centered_widest_segment_price = (hmw[widest_segment_index].End_price + hmw[
                                widest_segment_index].Start_price) / 2

                            if (centered_widest_segment_price - widest_segment_price * 0.382) <= apex_price <= (
                                    centered_widest_segment_price + widest_segment_price * 0.382):
                                # 3. Wave-d must be smaller than wave-c and 4. Wave-e must be smaller than wave-d
                                if Md.Price_range < Mc.Price_range and Mc.Price_range < Me.Price_range:
                                    self.polywaveList.loc[index, 'EW_structure'].append('Horizental')
                                    return

                            # 1. Wave-b should not be more than 261.8% of wave-a
                            if Mb.Price_range <= 2.618 * Ma.Price_range:

                                # 2. Waves c, d and e must all be smaller than the previous wave
                                if Mc.Price_range < Mb.Price_range and Md.Price_range < Mc.Price_range and Me.Price_range < Md.Price_range:
                                    self.polywaveList.loc[index, 'EW_structure'].append('Irregular')
                                    return

                            # 1.Wave-b is longer than wave-a, 2.Wave-c is smaller than wave-b, 3.Wave-d is larger than wave-c, 4.Wave-e is smaller than wave-d
                            if (Mb.Price_range > Ma.Price_range and Mb.Price_range > Mc.Price_range and
                                    Md.Price_range > Mc.Price_range and Md.Price_range > Me.Price_range):
                                # TODO: 5. Both trendlines will slope upward or downward.

                                # 6. thrust will be much larger than the widest leg of the Triangle, sometimes as much as 261.8%, but no more
                                if widest_segment_price < thrust.Price_range <= 2.618 * widest_segment_price:
                                    self.polywaveList.loc[index, 'EW_structure'].append('Running')
                                    return

                        elif (Me.End_candle_index + 0.2 * time_duration >= apex_time_index or
                              Me.End_candle_index + 0.4 * time_duration <= apex_time_index):

                            # TODO: In a Non-Limiting Triangle, a post-thrust correction into the apex's time zone of the converging trendlines
                            # TODO: Post-Triangular Thrust in Non-Limiting Triangle
                            self.polywaveList.loc[index, 'EW_structure'].append('Non-Limiting')
                            return

            # Expanding Triangles:
            # 1. The a-wave or the b-wave will always be the smallest segment of the Triangle.
            if np.argmin(hmw_price_range) == 0 or np.argmin(hmw_price_range) == 1:
                # 2. Wave-e will almost always be the largest wave of the pattern.
                if np.argmax(hmw_price_range) == 4:
                    # TODO: 3. Expanding Triangles cannot occur as b-waves in Zigzags or b, c or d-waves of a larger Triangle.
                    # TODO: 4. The e-wave will usually be the most time consuming and complex segment of the Triangle

                    # 5. The e-wave will almost always break beyond the trendline drawn across the top of wave-a and wave-c.
                    # 6. The b-d trendline should function the same as it would in any Contracting Triangle -> it's checked before
                    # TODO: maybe need to write a new function to check only end of e-wave breaks a-c trendline
                    if beyond_trendline(Ma, Mc, Me):
                        # 7. The "thrust" out of an Expanding Triangle should be less than the widest wave of the Triangle (which, in this case, is wave-e) unless it concludes a powerful, larger Correction.
                        # if thrust.Price_range < Me.Price_range:

                        # 8. Backward from wave-e, three of the previous waves must be at least 50% of the wave to the right.
                        if sum(cond_list_expanding) >= 3:
                            self.polywaveList.loc[index, 'EW_structure'].append('Expanding')

                            # Limiting Expanding Triangles:
                            # TODO: 1. A b-wave Expanding, Limiting Triangle appears to be possible only in an Irregular Failure or C-Failure Flat pattern.
                            # 2. The "thrust" out of the Triangle is minimal, retracing approximately 61.8% of the Triangle from highest to lowest point.
                            if waves_are_fib_related(thrust.Price_range, widest_segment_price, 0.618, True):
                                self.polywaveList.loc[index, 'EW_structure'].append('Limiting')

                                # 1. Wave-a must be the smallest wave in the pattern.
                                if np.argmin(hmw_price_range) == 0:
                                    # 2. Wave-b, c, d, and e must each exceed the previous segment's termination point
                                    if (Mb.Price_range > Ma.Price_range and Mc.Price_range > Mb.Price_range and
                                            Md.Price_range > Mc.Price_range and Me.Price_range > Md.Price_range):
                                        # 3. The e-wave will probably break beyond the trendline drawn across wave-a & c. -> it's checked before
                                        self.polywaveList.loc[index, 'EW_structure'].append('Horizontal')
                                        return

                                # 1. Either wave-b is smaller than wave-a and all the rest of the waves are larger than the previous, or wave-d is smaller than wave-c and all the other waves are larger than the previous.
                                if ((Mb.Price_range < Ma.Price_range and Mc.Price_range > Mb.Price_range and
                                     Md.Price_range > Mc.Price_range and Me.Price_range > Md.Price_range) or
                                        (Mb.Price_range > Ma.Price_range and Mc.Price_range > Mb.Price_range and
                                         Md.Price_range < Mc.Price_range and Me.Price_range > Md.Price_range)):
                                    # TODO: 2. The longer the period of time covered by the pattern, the more likely the channeling of the pattern will be upwardly or downwardly skewed.
                                    self.polywaveList.loc[index, 'EW_structure'].append('Irregular')
                                    return

                                # wave-b being slightly larger than wave-a and wave-d being slightly shorter than wave-c.
                                # Another variation occurs when all waves are larger than the previous except wave-c (which is shorter than wave-b).
                                # TODO: trendlines both go in the same direction, but still diverge
                                if ((Mb.Price_range > Ma.Price_range and Md.Price_range < Mc.Price_range) or
                                        (Mb.Price_range > Ma.Price_range and Mc.Price_range < Mb.Price_range and
                                         Md.Price_range > Mc.Price_range and Me.Price_range > Md.Price_range)):
                                    self.polywaveList.loc[index, 'EW_structure'].append('Running')
                                    return

                            apex_time_index, apex_price = self.apex(Ma, Mb, Mc, Md)
                            time_duration = Me.End_candle_index - Ma.Start_candle_index

                            # Measure the time consumed by the entire Triangle then take 40% of that amount and subtract it from the beginning of wave-a. The apex will occur before the 40% time frame is reached.
                            if Ma.Start_candle_index - 0.4 * time_duration < apex_time_index:
                                self.polywaveList.loc[index, 'EW_structure'].append('Non-Limiting')

    def apex(self, Ma, Mb, Mc, Md):
        """Return apex cordinate of Triangle"""
        x1 = Ma.End_candle_index
        y1 = Ma.End_price
        x2 = Mc.End_candle_index
        y2 = Mc.End_price

        x3 = Mb.End_candle_index
        y3 = Mb.End_price
        x4 = Md.End_candle_index
        y4 = Md.End_price

        return intersection(x1, y1, x2, y2, x3, y3, x4, y4)

    def correction_alternation_rule(self, index):
        # TODO: Condition of "Intricacy" and "Construction" must be implemented
        # no need to implement "Price" Alternation
        # TODO: Use this rule later

        stIndex = self.polywaveList.loc[index].PWstartIndex

        M1 = self.monowavesList[stIndex]
        M2 = self.monowavesList[stIndex + 1]
        M3 = self.monowavesList[stIndex + 2]

        if compare_ratio_waves(M1.Duration, M2.Duration, fib_ratio, True) or compare_ratio_waves(M1.Duration,
                                                                                                 M2.Duration,
                                                                                                 fib_ratio):
            if (waves_are_fib_related(M3.Duration, M1.Duration, 1) or waves_are_fib_related(M3.Duration, M2.Duration,
                                                                                            1) or
                    waves_are_fib_related(M3.Duration, M1.Duration, fib_ratio) or waves_are_fib_related(M3.Duration,
                                                                                                        M2.Duration,
                                                                                                        fib_ratio) or
                    waves_are_fib_related(M3.Duration, M1.Duration + M2.Duration, 1)):
                return

        self.polywaveList.loc[index, 'Validation'] = False

    def flat_fibo_rel_rule(self, index):
        stIndex = self.polywaveList.loc[index].PWstartIndex

        Ma = self.monowavesList[stIndex]
        Mb = self.monowavesList[stIndex + 1]
        Mc = self.monowavesList[stIndex + 2]

        if check_subitem_in_list(self.polywaveList.loc[index, 'EW_structure'], 'Strong B-Wave'):
            #  If the c-wave did relate by a Fibonacci ratio to wave-a, the ratio would be 161.8% or 61.8%.
            if waves_are_fib_related(Ma.Duration, Mc.Duration, fib_ratio):
                self.polywaveList.loc[index, 'FiboRelatedWaves'] = True

        if check_subitem_in_list(self.polywaveList.loc[index, 'EW_structure'], 'Normal B-Wave: C-Failure'):
            #  the c-wave would relate to wave-a by 61.8%. On very rare occasions, wave-c can relate to wave-a by 38.2%
            if waves_are_fib_related(Mc.Duration, Ma.Duration, fib_ratio, True) or waves_are_fib_related(Mc.Duration,
                                                                                                         Ma.Duration,
                                                                                                         1 - fib_ratio,
                                                                                                         True):
                self.polywaveList.loc[index, 'FiboRelatedWaves'] = True

        if check_subitem_in_list(self.polywaveList.loc[index, 'EW_structure'], 'Normal B-Wave: Elongated'):
            # If the c-wave Elongates, it is not likely there will be any relationship between wave-a & c. If there is, it would have to be 161.8% or 261.8%
            if waves_are_fib_related(Ma.Duration, Mc.Duration, fib_ratio) or waves_are_fib_related(Ma.Duration,
                                                                                                   Mc.Duration,
                                                                                                   1 - fib_ratio):
                self.polywaveList.loc[index, 'FiboRelatedWaves'] = True

        if check_subitem_in_list(self.polywaveList.loc[index, 'EW_structure'], 'Weak B-Wave:'):
            # If wave-a and wave-b related, it would be by 61.8%.  Waves-a & c could relate by the same amount.  The c-wave could also be 61.8% of wave-b.
            if (waves_are_fib_related(Ma.Duration, Mb.Duration, fib_ratio) or waves_are_fib_related(Ma.Duration,
                                                                                                    Mc.Duration,
                                                                                                    fib_ratio) or
                    waves_are_fib_related(Mb.Duration, Mc.Duration, fib_ratio)):
                self.polywaveList.loc[index, 'FiboRelatedWaves'] = True

    def zigzag_fibo_rel_rule(self, index):
        stIndex = self.polywaveList.loc[index].PWstartIndex

        Ma = self.monowavesList[stIndex]
        Mb = self.monowavesList[stIndex + 1]
        Mc = self.monowavesList[stIndex + 2]

        if check_subitem_in_list(self.polywaveList.loc[index, 'EW_structure'], 'Normal'):
            # If waves-a & b do relate, it will be by 61.8% or 38.2%
            # Wave-a will be either 61.8%, 100% or 161.8% of wave-c
            if (waves_are_fib_related(Ma.Duration, Mb.Duration, fib_ratio) or waves_are_fib_related(Ma.Duration,
                                                                                                    Mb.Duration,
                                                                                                    1 - fib_ratio) or
                    waves_are_fib_related(Ma.Duration, Mc.Duration, fib_ratio) or waves_are_fib_related(Ma.Duration,
                                                                                                        Mc.Duration,
                                                                                                        1)):
                self.polywaveList.loc[index, 'FiboRelatedWaves'] = True

        if check_subitem_in_list(self.polywaveList.loc[index, 'EW_structure'], 'Elongated'):
            # Usually an Elongated c-wave will have no relation to wave-a; if it does, it will be by 261.8%
            if waves_are_fib_related(Ma.Duration, Mc.Duration, 1 - fib_ratio, True):
                self.polywaveList.loc[index, 'FiboRelatedWaves'] = True

        if check_subitem_in_list(self.polywaveList.loc[index, 'EW_structure'], 'Truncated'):
            # Wave-c would be 38.2% of wave-a.
            if waves_are_fib_related(Mc.Duration, Ma.Duration, 1 - fib_ratio, True):
                self.polywaveList.loc[index, 'FiboRelatedWaves'] = True

    def triangle_fibo_rel_rule(self, index):
        stIndex = self.polywaveList.loc[index].PWstartIndex

        Ma = self.monowavesList[stIndex]
        Mb = self.monowavesList[stIndex + 1]
        Mc = self.monowavesList[stIndex + 2]
        Md = self.monowavesList[stIndex + 3]
        Me = self.monowavesList[stIndex + 4]

        # The most common setup is for waves-a, c, & e to relate by 61.8% or 38.2% and the b & d-waves to relate by 61.8%.
        if (waves_are_fib_related(Mb.Duration, Md.Duration, fib_ratio) and waves_are_fib_related(Ma.Duration,
                                                                                                 Mc.Duration,
                                                                                                 fib_ratio) and
                waves_are_fib_related(Mc.Duration, Me.Duration, 1 - fib_ratio) and waves_are_fib_related(Md.Duration,
                                                                                                         Me.Duration,
                                                                                                         fib_ratio)):
            self.polywaveList.loc[index, 'FiboRelatedWaves'] = True

        if waves_are_fib_related(Mb.Duration, Ma.Duration, fib_ratio, True):
            self.polywaveList.loc[index, 'Validation'] = False

    # Chapter 6: Post-Constructive Rules ot Logic - page 86 pdf

    def impulsions_post_confirmation(self, index):
        stIndex = self.polywaveList.loc[index].PWstartIndex

        M1 = self.monowavesList[stIndex]
        M2 = self.monowavesList[stIndex + 1]
        M3 = self.monowavesList[stIndex + 2]
        M4 = self.monowavesList[stIndex + 3]
        M5 = self.monowavesList[stIndex + 4]

        post_action = self.monowavesList[stIndex + 5] if (stIndex + 5) <= len(self.monowavesList) else None

        if post_action is not None:

            # post-Impulsive market action must break the 2-4 trendline in the same amount of time consumed by the 5th wave or less
            if wave_breaking_trendline_impulse(M2, M4, M5, post_action):
                if self.polywaveList.loc[index].ExtensionWaveIndex == 1:

                    # The retracement to follow 1st Wave Extension must return to the termination of wave-4
                    if post_action.Price_range > M5.Price_range:
                        self.polywaveList.loc[index, 'PostConfirmation'] = True

                elif self.polywaveList.loc[index].ExtensionWaveIndex == 3:

                    # Price action must return to the 4th wave zone of the completed Impulse pattern and will usually end near the termination of wave-4.
                    tmp_price = post_action.Max_price if post_action.Direction > 0 else post_action.Min_price
                    if (M4.End_price - M4.Start_price) * (tmp_price - M4.Start_price) > 0:
                        self.polywaveList.loc[index, 'PostConfirmation'] = True

                elif self.polywaveList.loc[index].ExtensionWaveIndex == 5:
                    # The correction to follow a 5th extension pattern must retrace at least 61.8% of the 5th wave
                    if post_action.Price_range / M5.Price_range > 0.618:
                        self.polywaveList.loc[index, 'PostConfirmation'] = True

                elif check_subitem_in_list(self.polywaveList.loc[index, 'EW_structure'], '5th wave Failure'):
                    # the move to follow should completely retrace the entire Impulse wave.
                    tmp_price = post_action.Max_price if post_action.Direction > 0 else post_action.Min_price
                    if (M1.End_price - M1.Start_price) * (M1.Start_price - tmp_price) > 0:
                        self.polywaveList.loc[index, 'PostConfirmation'] = True
            else:
                # TODO: If it takes more time, the 5th wave is developing into a Terminal or wave-4 is not complete or your Impulse interpretation is wrong
                pass

    def flat_zigzag_post_confirmation(self, index):
        stIndex = self.polywaveList.loc[index].PWstartIndex

        Ma = self.monowavesList[stIndex]
        Mb = self.monowavesList[stIndex + 1]
        Mc = self.monowavesList[stIndex + 2]

        post_action = self.monowavesList[stIndex + 3] if (stIndex + 3) <= len(self.monowavesList) else None

        if post_action is not None:

            # the condition of Wave-b Shorter than Wave-a or Wave-b Longer than Wave-a are not different.
            # if Mb.Price_range < Ma.Price_range:
            # post-Corrective market action must break the "0-B" trendline in the same amount of time (or less) that wave-c took to form
            if wave_breaking_trendline_flat_zigzag_triangle(Ma, Mc, post_action):
                # If Stage 1 confirmation is met, Stage 2 requires wave-c be completely retraced in the same amount of time (or less) that wave-c took to form.
                if wave_is_steeper(post_action.Price_range, post_action.Duration, Mc):
                    self.polywaveList.loc[index, 'PostConfirmation'] = True
            else:
                # TODO: If it takes more time, the c-wave is developing into a Terminal or wave-4 (of wave-c) is not complete or your Corrective interpretation is incorrect
                pass

    def contracting_triangle_post_confirmation(self, index):
        stIndex = self.polywaveList.loc[index].PWstartIndex

        Ma = self.monowavesList[stIndex]
        Mb = self.monowavesList[stIndex + 1]
        Mc = self.monowavesList[stIndex + 2]
        Md = self.monowavesList[stIndex + 3]
        Me = self.monowavesList[stIndex + 4]

        post_action = self.monowavesList[stIndex + 5] if (stIndex + 5) <= len(self.monowavesList) else None

        if post_action is None:
            return

        if check_subitem_in_list(self.polywaveList.loc[index, 'EW_structure'], 'Contracting'):

            # the market must break the B-D trendline in the same amount of time (or less) as that consumed by wave-e.
            if wave_breaking_trendline_flat_zigzag_triangle(Mc, Me, post_action):

                # The "thrust" after wave-e of a Triangle should exceed the highest or lowest price level achieved during the Triangle.
                if ((post_action.Direction == 1 and post_action.End_price > max(Mb.End_price, Md.End_price)) or
                        (post_action.Direction == -1 and post_action.End_price < min(Mb.End_price, Md.End_price))):
                    self.polywaveList.loc[index, 'PostConfirmation'] = True

    def flat_zigzag_prediction(self, index):
        stIndex = self.polywaveList.loc[index].PWstartIndex

        Ma = self.monowavesList[stIndex]
        Mb = self.monowavesList[stIndex + 1]
        Mc = self.monowavesList[stIndex + 2]

        xa = Ma.Start_candle_index
        ya = Ma.Start_price
        xb = Mc.Start_candle_index
        yb = Mc.Start_price

        xc = Mc.End_candle_index
        yc = Mc.End_price

        x = xc + xc - xb

        # post market action must break the "0-B" trendline in the same amount of time (or less) that wave-c took to form
        xr1, yr1 = intersection(xa, ya, xb, yb, x, yc, x, yb)
        xr2, yr2 = intersection(xa, ya, xb, yb, xc, yc, x, yb)
        return int(xc), int(xr1), yr1, yr2, yb

    def impulsions_prediction(self, index):
        stIndex = self.polywaveList.loc[index].PWstartIndex

        M1 = self.monowavesList[stIndex]
        M2 = self.monowavesList[stIndex + 1]
        M3 = self.monowavesList[stIndex + 2]
        M4 = self.monowavesList[stIndex + 3]
        M5 = self.monowavesList[stIndex + 4]

        # post-Impulsive market action must break the 2-4 trendline in the same amount of time consumed by the 5th wave or less
        x2 = M2.End_candle_index
        y2 = M2.End_price
        x4 = M4.End_candle_index
        y4 = M4.End_price

        x5 = M5.End_candle_index
        y5 = M5.End_price
        x6 = x5 + x5 - x4

        xr1, yr1 = intersection(x2, y2, x4, y4, x6, y5, x6, y4)
        xr2, yr2 = intersection(x2, y2, x4, y4, x5, y5, x6, y4)
        return int(x5), int(xr1), yr1, yr2, y4
