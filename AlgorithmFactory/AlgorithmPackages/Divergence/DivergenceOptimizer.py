from AlgorithmFactory.AlgorithmTools.LocalExtermums import *
from AlgorithmFactory.AlgorithmTools import HeikinConverter
from AlgorithmFactory.AlgorithmPackages.Divergence import divergence_calculation

from AlgorithmFactory.AlgorithmTools.IndicatorTools import *
from AlgorithmFactory.AlgorithmTools.CandleTools import *


class DivergenceOptimizer:

    def __init__(self, data, heikin_data_level, extremum_window, asymmetric_extremum_window,
                 asymmetric_alpha, hidden_divergence_check_window, upper_line_tr, trend_direction, down_direction):

        self.heiking_data_level = heikin_data_level
        self.extremum_window = extremum_window
        self.asymmetric_extremum_window = asymmetric_extremum_window
        self.asymmetric_alpha = asymmetric_alpha
        self.hidden_divergence_check_window = hidden_divergence_check_window
        self.upper_line_tr = upper_line_tr
        self.trend_direction = trend_direction
        self.down_direction = down_direction

        # Make Heikin Data
        for i in range(heikin_data_level):
            heikin_converter = HeikinConverter(data[0])
            data = heikin_converter.convert_many(data[1:])

        # Extract Data
        self.open, self.high, self.low, self.close = get_ohlc(data)
        self.b, self.a = get_bottom_top(data)
        self.middle = get_middle_hl(data)

        # Extract Local Extremum
        self.local_min_price_left, self.local_max_price_left = get_local_extermums(data, extremum_window, 1)
        self.local_min_price_right, self.local_max_price_right = \
            get_local_extermums_asymetric(data, asymmetric_extremum_window, asymmetric_alpha, 1)

        self.real_time = False
        # Extract Pip Difference
        self.body_avg = np.mean(self.a - self.b)
        self.pip_difference = self.body_avg * .2

    def calculate_score(self, idx_list, base_look_forward, score_tr, p):
        scores = []
        for idx in idx_list:
            if idx + base_look_forward <= len(self.close):
                look_forward = idx + base_look_forward
            else:
                scores.append(0)
                continue

            # evaluation of score 1 and 2

            max_idx = np.argmax(self.high[idx + 1:look_forward + 1]) + idx + 1
            max_price = self.high[max_idx]
            min_idx = np.argmin(self.low[idx + 1:look_forward + 1]) + idx + 1
            min_price = self.low[min_idx]

            in_range_min_price = min(self.low[idx + 1:max_idx + 2])
            in_range_max_price = max(self.high[idx + 1:min_idx + 2])

            if in_range_max_price < self.close[idx]:
                in_range_max_price = self.close[idx]
            if in_range_min_price > self.close[idx]:
                in_range_min_price = self.close[idx]

            a = max_price - self.close[idx]
            b = self.close[idx] - in_range_min_price

            score_max = (a - b) / (a + b)

            a = in_range_max_price - self.close[idx]
            b = self.close[idx] - min_price

            score_min = (a - b) / (a + b)

            score1 = (max_price - self.close[idx]) * score_max / (max_price - min_price)
            score2 = (self.close[idx] - min_price) * score_min / (max_price - min_price)

            # --- sloppe approach score method
            slope = np.diff(self.middle[idx: look_forward])
            slope = slope / (max(slope))

            n = slope.size
            coeff = self.polynomial_coff(n) * slope
            score3 = np.mean(coeff)

            # --- drawdown vs profit
            neg = np.min(self.low[idx: look_forward]) - self.close[idx]
            pos = np.max(self.high[idx: look_forward]) - self.close[idx]

            if abs(neg) > abs(pos) * 2:
                score4 = -0.5
            elif abs(neg) > abs(pos) * 1.5:
                score4 = -0.25
            elif 2 * abs(neg) < abs(pos):
                score4 = 0.5
            elif 1.5 * abs(neg) < abs(pos):
                score4 = 0.25
            else:
                score4 = 0

            # summations of scores
            total_score = score1 + score2 + score3 + score4
            scores.append(total_score)

        end_indexes, scores = self.remove_neighbors(idx_list, scores, 2)
        scores = [score for score in scores if score is not None]

        bad_scores = 0
        for i in range(len(scores)):
            if self.trend_direction == 1:
                if scores[i] < score_tr:
                    bad_scores += 1
            elif self.trend_direction == 0:
                if scores[i] > -score_tr:
                    bad_scores += 1
        if len(scores) == 0:
            return 0, scores
        if bad_scores/len(scores) > (1-p):
            return 0, scores

        a = np.array(self.polynomial_coff(len(scores))[::-1])
        scores_p = np.array(scores) * a
        sum_scores = sum(scores_p)
        return sum_scores, scores

    def get_indexes(self, indicator_params):
        # Make Indicator
        min_indicator, max_indicator = get_indicator(indicator_params, self.close)

        # Extract Indicator Extremum
        local_min_indicator_left, local_max_indicator_left = \
            get_indicator_local_extermums(max_indicator, min_indicator, self.extremum_window)
        local_min_indicator_right, local_max_indicator_right = \
            get_indicator_local_extermums_asymetric(max_indicator, min_indicator, self.asymmetric_extremum_window,
                                                    self.asymmetric_alpha)

        if self.trend_direction == 1:
            [idx, val] = divergence_calculation(self.b, self.low,
                                                min_indicator,
                                                self.local_min_price_left,
                                                self.local_min_price_right, local_min_indicator_left,
                                                local_min_indicator_right, self.hidden_divergence_check_window,
                                                self.down_direction, self.trend_direction, self.pip_difference,
                                                self.upper_line_tr,
                                                self.real_time)
        else:
            [idx, val] = divergence_calculation(self.a, self.high,
                                                max_indicator,
                                                self.local_max_price_left, self.local_max_price_right,
                                                local_max_indicator_left, local_max_indicator_right,
                                                self.hidden_divergence_check_window, self.down_direction,
                                                self.trend_direction,
                                                self.pip_difference, self.upper_line_tr, self.real_time)

        end_indexes = []
        for i in range(len(idx)):
            end_indexes.append(idx[i][0][1])
        end_indexes = np.array(end_indexes)
        sort_idx = np.argsort(end_indexes)
        end_indexes = list(end_indexes[sort_idx])
        return end_indexes

    def find_optimum_param(self, params_list, look_forward, threshold):
        period_scores = []
        all_scores = []
        for indicator_params in params_list:
            end_indexes = self.get_indexes(indicator_params)
            period_score, scores = self.calculate_score(end_indexes, look_forward, 0.4, 0.7)
            period_scores.append(period_score)
            all_scores.append(scores)
        period_scores = np.array(period_scores)
        period_scores = np.round(period_scores, 6)
        sorted_idx = np.argsort(period_scores)[::-1]
        sorted_period_scores = period_scores[sorted_idx]

        best_score_idx = -1
        window = 1
        for i in range(len(sorted_period_scores)):
            found_best = True

            for j in range(max(0, sorted_idx[i]-window), min(len(period_scores), sorted_idx[i]+window+1)):
                if self.trend_direction == 1:
                    if period_scores[j] < threshold:
                        found_best = False
                else:
                    if period_scores[j] > -threshold:
                        found_best = False
            if found_best:
                best_score_idx = sorted_idx[i]
                break
            if self.trend_direction == 1:
                if sorted_period_scores[i] < threshold:
                    break
            else:
                if sorted_period_scores[i] > -threshold:
                    break

        return period_scores, best_score_idx, all_scores[best_score_idx]

    @staticmethod
    def polynomial_coff(num):
        x = np.arange(1, num + 1)
        return 1 / x ** 0.3

    @staticmethod
    def remove_neighbors(indx, scores, window):
        diffs = np.diff(np.array(indx))

        j = 0
        s = 0
        k = 0
        for i in range(len(diffs)):
            s += diffs[i]
            k += 1
            if s <= window:
                scores[j] = (scores[j] * k + scores[i + 1]) / (k + 1)
                indx[j] = (float(indx[j] * k + indx[i + 1])) / (k + 1)
                scores[i + 1] = None
                indx[i + 1] = -1
            else:
                s = 0
                k = 0
                j = i + 1
        for i in range(len(indx)):
            indx[i] = int(round(indx[i]))

        return indx, scores

