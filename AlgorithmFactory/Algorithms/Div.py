from AlgorithmFactory.AlgorithmPackages.Divergence import DivergencePkg
from AlgorithmFactory.AlgorithmTools import LocalExtermums
from AlgorithmFactory.AlgorithmTools import HeikinConverter
from AlgorithmFactory.AlgorithmTools.LocalExtermums import *
from AlgorithmFactory.AlgorithmTools.CandleTools import *
from AlgorithmFactory.AlgorithmTools.IndicatorTools import *

from AlgorithmFactory.AlgorithmPackages.Divergence import DivergenceOptimizer

import copy


class Divergence:

    def __init__(self, symbol, data_history, params_list, indicator_params, heikin_level, big_win, small_win,
                 hidden_divergence_check_window, upper_line_tr, alpha, extremum_mode, open_mode, optimize_enable,
                 look_forward, score_tr):
        # Data
        self.data = data_history

        # Extract Data
        self.open, self.high, self.low, self.close = get_ohlc(data_history)
        self.a, self.b = get_bottom_top(data_history)
        body_avg = np.mean(self.a - self.b)

        # Set Parameters
        self.symbol = symbol
        self.indicator_param = indicator_params
        self.pip_difference = body_avg * .2
        self.big_win = big_win
        self.small_win = small_win
        self.hidden_divergence_check_window = hidden_divergence_check_window
        self.upper_line_tr = upper_line_tr
        self.alpha = alpha
        self.extremum_mode = extremum_mode
        self.open_mode = open_mode
        self.params_list = params_list
        self.heikin_level = heikin_level
        self.optimize_enable = optimize_enable
        self.look_forward = look_forward
        self.score_tr = score_tr

        # Get Heikin Data
        self.heikin_data = copy.deepcopy(self.data)
        self.converters = []
        for i in range(heikin_level):
            self.converters.append(HeikinConverter(self.heikin_data[0]))
            self.heikin_data = self.converters[i].convert_many(self.heikin_data[1:])

        # Extract Heiking Data
        self.open_hk, self.high_hk, self.low_hk, self.close_hk = get_ohlc(self.heikin_data)

        # Extract Indicator
        self.price = [row['Close'] for row in self.heikin_data]
        self.min_indicator, self.max_indicator = get_indicator(indicator_params, self.price)

        self.local_min_price_left, self.local_max_price_left = LocalExtermums.get_local_extermums(data_history,
                                                                                                  self.big_win,
                                                                                                  self.extremum_mode)
        self.local_min_price_right, self.local_max_price_right = LocalExtermums.get_local_extermums_asymetric(
            data_history, self.small_win, self.alpha, self.extremum_mode)

        self.local_min_indicator_left, self.local_max_indicator_left = LocalExtermums.get_indicator_local_extermums(
            self.max_indicator, self.min_indicator, self.big_win)
        self.local_min_indicator_right, self.local_max_indicator_right = LocalExtermums.get_indicator_local_extermums_asymetric(
            self.max_indicator, self.min_indicator, self.small_win, self.alpha)

        self.buy_trigger = False
        self.sell_trigger = False
        self.buy_limit_price = 0
        self.sell_limit_price = 0
        self.candle_buy_submitted = False
        self.candle_sell_submitted = False

    def on_tick(self):
        if self.open_mode == 2:
            if self.buy_trigger and not self.candle_buy_submitted:
                if self.data[-1]['High'] > self.buy_limit_price:
                    self.candle_buy_submitted = True
                    return 1, self.buy_limit_price
            if self.sell_trigger and not self.candle_sell_submitted:
                if self.data[-1]['Low'] < self.sell_limit_price:
                    self.candle_sell_submitted = True
                    return -1, self.sell_limit_price
        return 0, 0

    def on_data(self, candle, cash):
        self.candle_buy_submitted = False
        self.candle_sell_submitted = False
        self.buy_trigger = False
        self.sell_trigger = False
        self.update_history()
        self.update_heikin_data()
        self.update_indicator()
        self.update_local_extremums()
        signal = self.divergence_predict(self.a, self.b, self.low, self.high, self.max_indicator,
                                         self.min_indicator,
                                         self.local_min_price_left, self.local_min_price_right,
                                         self.local_max_price_left, self.local_max_price_right,
                                         self.local_min_indicator_left, self.local_min_indicator_right,
                                         self.local_max_indicator_left, self.local_max_indicator_right,
                                         self.hidden_divergence_check_window,
                                         self.pip_difference, self.upper_line_tr, self.data, self.heikin_level,
                                         self.big_win,
                                         self.small_win,
                                         self.alpha, self.params_list, self.look_forward, self.score_tr, self.big_win,
                                         self.small_win, self.alpha, self.price,
                                         self.optimize_enable)
        if signal == 1:
            self.buy_trigger = True
            self.buy_limit_price = self.data[-1]['High']
        elif signal == -1:
            self.sell_trigger = True
            self.sell_limit_price = self.data[-1]['Low']
        self.data.pop(0)
        self.data.append(candle)

        if self.open_mode == 1:
            return signal, self.data[-1]['Close']

        return 0, 0

    def update_history(self):
        self.a = self.a[1:]
        self.a = np.append(self.a, [max(self.data[-1]['Open'], self.data[-1]['Close'])])
        self.b = self.b[1:]
        self.b = np.append(self.b, [min(self.data[-1]['Open'], self.data[-1]['Close'])])
        self.open = self.open[1:]
        self.open = np.append(self.open, [self.data[-1]['Open']])
        self.high = self.high[1:]
        self.high = np.append(self.high, [self.data[-1]['High']])
        self.low = self.low[1:]
        self.low = np.append(self.low, [self.data[-1]['Low']])
        self.close = self.close[1:]
        self.close = np.append(self.close, [self.data[-1]['Close']])

    def update_heikin_data(self):
        new_heikin_data = self.data[-1]
        for i in range(self.heikin_level):
            new_heikin_data = self.converters[i].on_data(new_heikin_data)
        self.heikin_data.pop(0)
        self.heikin_data.append(new_heikin_data)

    def update_indicator(self):
        self.price = [row['Close'] for row in self.heikin_data]
        self.min_indicator, self.max_indicator = get_indicator(self.indicator_param, self.price)

    def update_local_extremums(self):
        self.local_min_price_left = update_local_extremum(self.local_min_price_left)
        self.local_max_price_left = update_local_extremum(self.local_max_price_left)
        self.local_min_price_right = update_local_extremum(self.local_min_price_right)
        self.local_max_price_right = update_local_extremum(self.local_max_price_right)
        self.local_min_indicator_left = update_local_extremum(self.local_min_indicator_left)
        self.local_max_indicator_left = update_local_extremum(self.local_max_indicator_left)
        self.local_min_indicator_right = update_local_extremum(self.local_min_indicator_right)
        self.local_max_indicator_right = update_local_extremum(self.local_max_indicator_right)

        window_size = max(self.big_win * 4, self.small_win * 4)
        new_local_min_price_left, new_local_max_price_left = LocalExtermums.get_local_extermums(
            self.data[-window_size:], self.big_win, self.extremum_mode)
        new_local_min_price_right, new_local_max_price_right = LocalExtermums.get_local_extermums_asymetric(
            self.data[-window_size:], self.small_win, self.alpha, self.extremum_mode)

        new_local_min_indicator_left, new_local_max_indicator_left = LocalExtermums.get_indicator_local_extermums(
            self.max_indicator[-window_size:], self.min_indicator[-window_size:], self.big_win)
        new_local_min_indicator_right, new_local_max_indicator_right = LocalExtermums.get_indicator_local_extermums_asymetric(
            self.max_indicator[-window_size:], self.min_indicator[-window_size:], self.small_win, self.alpha)

        self.local_min_price_left = update_new_local_extremum(self.local_min_price_left, new_local_min_price_left,
                                                              len(self.data) + 1, window_size)
        self.local_max_price_left = update_new_local_extremum(self.local_max_price_left, new_local_max_price_left,
                                                              len(self.data) + 1, window_size)
        self.local_min_price_right = update_new_local_extremum(self.local_min_price_right, new_local_min_price_right,
                                                               len(self.data) + 1, window_size)
        self.local_max_price_right = update_new_local_extremum(self.local_max_price_right, new_local_max_price_right,
                                                               len(self.data) + 1, window_size)
        self.local_min_indicator_left = update_new_local_extremum(self.local_min_indicator_left,
                                                                  new_local_min_indicator_left,
                                                                  len(self.min_indicator) + 1, window_size)
        self.local_max_indicator_left = update_new_local_extremum(self.local_max_indicator_left,
                                                                  new_local_max_indicator_left,
                                                                  len(self.max_indicator) + 1, window_size)
        self.local_min_indicator_right = update_new_local_extremum(self.local_min_indicator_right,
                                                                   new_local_min_indicator_right,
                                                                   len(self.min_indicator) + 1, window_size)
        self.local_max_indicator_right = update_new_local_extremum(self.local_max_indicator_right,
                                                                   new_local_max_indicator_right,
                                                                   len(self.max_indicator) + 1, window_size)

    def get_optimize_indicator(self, data, heikin_data_level, extremum_window, asymmetric_extremum_window,
                               asymmetric_alpha,
                               hidden_divergence_check_window, upper_line_tr, trend_direction, down_direction,
                               params_list,
                               look_forward, score_tr, price, big_win, small_win, alpha, min_indicator, max_indicator,
                               local_min_indicator_left, local_max_indicator_left, local_min_indicator_right,
                               local_max_indicator_right):
        optimizer = DivergenceOptimizer(data, heikin_data_level, extremum_window, asymmetric_extremum_window,
                                        asymmetric_alpha,
                                        hidden_divergence_check_window, upper_line_tr, trend_direction,
                                        down_direction)
        scores, best, detail_scores = optimizer.find_optimum_param(params_list, look_forward, score_tr)

        if best != -1:
            indicator_params = params_list[best]
            min_indicator, max_indicator = get_indicator(indicator_params, price)

            local_min_indicator_left, local_max_indicator_left = LocalExtermums.get_indicator_local_extermums(
                max_indicator, min_indicator, big_win)
            local_min_indicator_right, local_max_indicator_right = LocalExtermums.get_indicator_local_extermums_asymetric(
                max_indicator, min_indicator, small_win, alpha)

        return min_indicator, max_indicator, local_min_indicator_left, local_max_indicator_left, local_min_indicator_right, local_max_indicator_right, best

    def divergence_predict(self, a, b, low, high, max_indicator, min_indicator, local_min_price_left,
                           local_min_price_right,
                           local_max_price_left, local_max_price_right,
                           local_min_indicator_left, local_min_indicator_right, local_max_indicator_left,
                           local_max_indicator_right, hidden_divergence_check_window,
                           pip_difference, upper_line_tr, data, heikin_data_level, extremum_window,
                           asymmetric_extremum_window,
                           asymmetric_alpha, params_list, look_forward, score_tr, big_win, small_win, alpha, price,
                           optimize_enable):
        real_time = True

        # --- bullish divergence
        trend_direction = 1
        down_direction = 0

        if optimize_enable:
            min_indicator, max_indicator, local_min_indicator_left, local_max_indicator_left, local_min_indicator_right, \
            local_max_indicator_right, best1 = self.get_optimize_indicator(data, heikin_data_level, extremum_window,
                                                                          asymmetric_extremum_window, asymmetric_alpha,
                                                                          hidden_divergence_check_window, upper_line_tr,
                                                                          trend_direction, down_direction, params_list,
                                                                          look_forward, score_tr, price, big_win,
                                                                          small_win,
                                                                          alpha, min_indicator, max_indicator,
                                                                          local_min_indicator_left,
                                                                          local_max_indicator_left,
                                                                          local_min_indicator_right,
                                                                          local_max_indicator_right)
            if best1 != -1:
                [idx1, val1] = DivergencePkg.divergence_calculation(b, low, min_indicator, local_min_price_left,
                                                                    local_min_price_right,
                                                                    local_min_indicator_left,
                                                                    local_min_indicator_right, hidden_divergence_check_window,
                                                                    down_direction,
                                                                    trend_direction,
                                                                    pip_difference, upper_line_tr, real_time)
            else:
                idx1 = []
        else:
            [idx1, val1] = DivergencePkg.divergence_calculation(b, low, min_indicator, local_min_price_left,
                                                                local_min_price_right,
                                                                local_min_indicator_left,
                                                                local_min_indicator_right,
                                                                hidden_divergence_check_window,
                                                                down_direction,
                                                                trend_direction,
                                                                pip_difference, upper_line_tr, real_time)

        trend_direction = 1
        down_direction = 1
        if optimize_enable:
            min_indicator, max_indicator, local_min_indicator_left, local_max_indicator_left, local_min_indicator_right, \
            local_max_indicator_right, best2 = self.get_optimize_indicator(data, heikin_data_level, extremum_window,
                                                                          asymmetric_extremum_window, asymmetric_alpha,
                                                                          hidden_divergence_check_window, upper_line_tr,
                                                                          trend_direction, down_direction, params_list,
                                                                          look_forward, score_tr, price, big_win,
                                                                          small_win,
                                                                          alpha, min_indicator, max_indicator,
                                                                          local_min_indicator_left,
                                                                          local_max_indicator_left,
                                                                          local_min_indicator_right,
                                                                          local_max_indicator_right)
            if best2 != -1:
                [idx2, val2] = DivergencePkg.divergence_calculation(b, low, min_indicator, local_min_price_left,
                                                                    local_min_price_right,
                                                                    local_min_indicator_left,
                                                                    local_min_indicator_right,
                                                                    hidden_divergence_check_window,
                                                                    down_direction,
                                                                    trend_direction,
                                                                    pip_difference, upper_line_tr, real_time)
            else:
                idx2 = []
        else:
            [idx2, val2] = DivergencePkg.divergence_calculation(b, low, min_indicator, local_min_price_left,
                                                                local_min_price_right,
                                                                local_min_indicator_left,
                                                                local_min_indicator_right,
                                                                hidden_divergence_check_window,
                                                                down_direction,
                                                                trend_direction,
                                                                pip_difference, upper_line_tr, real_time)

        # --- bearish divergence
        trend_direction = 0
        down_direction = 0
        if optimize_enable:
            min_indicator, max_indicator, local_min_indicator_left, local_max_indicator_left, local_min_indicator_right, \
            local_max_indicator_right, best3 = self.get_optimize_indicator(data, heikin_data_level, extremum_window,
                                                                          asymmetric_extremum_window, asymmetric_alpha,
                                                                          hidden_divergence_check_window, upper_line_tr,
                                                                          trend_direction, down_direction, params_list,
                                                                          look_forward, score_tr, price, big_win,
                                                                          small_win,
                                                                          alpha, min_indicator, max_indicator,
                                                                          local_min_indicator_left,
                                                                          local_max_indicator_left,
                                                                          local_min_indicator_right,
                                                                          local_max_indicator_right)
            if best3 != -1:
                [idx3, val3] = DivergencePkg.divergence_calculation(b, low, min_indicator, local_min_price_left,
                                                                    local_min_price_right,
                                                                    local_min_indicator_left,
                                                                    local_min_indicator_right,
                                                                    hidden_divergence_check_window,
                                                                    down_direction,
                                                                    trend_direction,
                                                                    pip_difference, upper_line_tr, real_time)
            else:
                idx3 = []
        else:
            [idx3, val3] = DivergencePkg.divergence_calculation(b, low, min_indicator, local_min_price_left,
                                                                local_min_price_right,
                                                                local_min_indicator_left,
                                                                local_min_indicator_right,
                                                                hidden_divergence_check_window,
                                                                down_direction,
                                                                trend_direction,
                                                                pip_difference, upper_line_tr, real_time)

        trend_direction = 0
        down_direction = 1
        if optimize_enable:
            min_indicator, max_indicator, local_min_indicator_left, local_max_indicator_left, local_min_indicator_right, \
            local_max_indicator_right, best4 = self.get_optimize_indicator(data, heikin_data_level, extremum_window,
                                                                          asymmetric_extremum_window, asymmetric_alpha,
                                                                          hidden_divergence_check_window, upper_line_tr,
                                                                          trend_direction, down_direction, params_list,
                                                                          look_forward, score_tr, price, big_win,
                                                                          small_win,
                                                                          alpha, min_indicator, max_indicator,
                                                                          local_min_indicator_left,
                                                                          local_max_indicator_left,
                                                                          local_min_indicator_right,
                                                                          local_max_indicator_right)
            if best4 != -1:
                [idx4, val4] = DivergencePkg.divergence_calculation(b, low, min_indicator, local_min_price_left,
                                                                    local_min_price_right,
                                                                    local_min_indicator_left,
                                                                    local_min_indicator_right,
                                                                    hidden_divergence_check_window,
                                                                    down_direction,
                                                                    trend_direction,
                                                                    pip_difference, upper_line_tr, real_time)
            else:
                idx4 = []
        else:
            [idx4, val4] = DivergencePkg.divergence_calculation(b, low, min_indicator, local_min_price_left,
                                                                local_min_price_right,
                                                                local_min_indicator_left,
                                                                local_min_indicator_right,
                                                                hidden_divergence_check_window,
                                                                down_direction,
                                                                trend_direction,
                                                                pip_difference, upper_line_tr, real_time)

        if len(idx1) != 0:
            if idx1[-1][0][1] >= len(a) - 2 or idx1[-1][1][1] >= len(a) - 2:
                return 1
        if len(idx2) != 0:
            if idx2[-1][0][1] >= len(a) - 2 or idx2[-1][1][1] >= len(a) - 2:
                return 1
        if len(idx3) != 0:
            if idx3[-1][0][1] >= len(a) - 2 or idx3[-1][1][1] >= len(a) - 2:
                return -1
        if len(idx4) != 0:
            if idx4[-1][0][1] >= len(a) - 2 or idx4[-1][1][1] >= len(a) - 2:
                return -1
        return 0
