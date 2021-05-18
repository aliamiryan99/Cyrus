from AlgorithmTools.LocalExtermums import *
from AlgorithmTools.HeikinCandle import HeikinConverter
from AlgorithmPackages.Divergence.DivergencePkg import divergence_calculation
from ta.momentum import *
from pandas import Series

from Indicators.KDJ import KDJ
from Indicators.RSI import RSI
from Indicators.Stochastic import Stochastic
from Visualization.Tools import *
from Visualization.BaseChart import *


class DivergenceVisualizer:

    def __init__(self, data, heikin_data_level, indicator_name, extremum_window, asymmetric_extremum_window, asymmetric_alpha):
        self.data = data
        self.hikin_data_level = heikin_data_level
        self.indicator_name = indicator_name

        for i in range(self.hikin_data_level):
            heikin_converter = HeikinConverter(self.data[0])
            self.data = heikin_converter.convert_many(self.data[1:])

        self.open = np.array([d['Open'] for d in self.data])
        self.high = np.array([d['High'] for d in self.data])
        self.low = np.array([d['Low'] for d in self.data])
        self.close = np.array([d['Close'] for d in self.data])

        self.a = np.c_[self.open, self.close].max(1)
        self.b = np.c_[self.open, self.close].min(1)

        self.local_min_price_left, self.local_max_price_left = get_local_extermums(self.data, extremum_window, 1)
        self.local_min_price_right, self.local_max_price_right = \
            get_local_extermums_asymetric(self.data, asymmetric_extremum_window, asymmetric_alpha, 1)

        self.indicator, self.indicator_np = None, None
        self.indicators = []
        self.indicators_list = []
        if indicator_name == 'rsi':
            rsi_ind = RSI(data, 14)
            self.indicators.append(rsi_ind.values)
        elif indicator_name == 'stochastic':
            stochastic_k = Stochastic(data, 14, 3, 3, 'K')
            stochastic_d = Stochastic(data, 14, 3, 3, 'D')
            self.indicators.append(stochastic_k.values)
            self.indicators.append(stochastic_d.values)
        elif indicator_name == 'kdj':
            kdj = KDJ(data, 13, 3)
            k_value, d_value, j_value = kdj.get_values()
            self.indicators += [k_value, d_value, j_value]

        self.min_indicator, self.max_indicator = get_min_max_indicator(self.indicators)
        self.indicators_list.append({'df': pd.DataFrame(self.min_indicator).rename(columns={0: 'value'}), 'color': "#a36232", 'width': 2})
        self.indicators_list.append({'df': pd.DataFrame(self.max_indicator).rename(columns={0: 'value'}), 'color': "#1263a9", 'width': 2})

        self.local_min_indicator_left, self.local_max_indicator_left = get_indicator_local_extermums(self.max_indicator, self.min_indicator, extremum_window)
        self.local_min_indicator_right, self.local_max_indicator_right = get_indicator_local_extermums_asymetric(self.max_indicator, self.min_indicator, asymmetric_extremum_window, asymmetric_alpha)

        real_time = False
        hidden_divergence_check_window = 15
        upper_line_tr = 0.90
        body_avg = np.mean(self.a - self.b)
        pip_difference = body_avg * .2
        # --- bullish divergence
        trend_direction = 1
        down_direction = 0
        [self.idx1, self.val1] = divergence_calculation(self.b, self.low, self.min_indicator, self.local_min_price_left,
                                              self.local_min_price_right, self.local_min_indicator_left,
                                              self.local_min_indicator_right, hidden_divergence_check_window,
                                              down_direction, trend_direction, pip_difference, upper_line_tr, real_time)

        trend_direction = 1
        down_direction = 1
        [self.idx2, self.val2] = divergence_calculation(self.b, self.low, self.min_indicator, self.local_min_price_left,
                                              self.local_min_price_right, self.local_min_indicator_left,
                                              self.local_min_indicator_right, hidden_divergence_check_window,
                                              down_direction, trend_direction, pip_difference, upper_line_tr, real_time)

        # --- bearish divergence
        trend_direction = 0
        down_direction = 0
        [self.idx3, self.val3] = divergence_calculation(self.a, self.high, self.max_indicator, self.local_max_price_left,
                                              self.local_max_price_right, self.local_max_indicator_left,
                                              self.local_max_indicator_right, hidden_divergence_check_window,
                                              down_direction, trend_direction, pip_difference, upper_line_tr, real_time)

        trend_direction = 0
        down_direction = 1
        [self.idx4, self.val4] = divergence_calculation(self.a, self.high, self.max_indicator, self.local_max_price_left,
                                              self.local_max_price_right, self.local_max_indicator_left,
                                              self.local_max_indicator_right, hidden_divergence_check_window,
                                              down_direction, trend_direction, pip_difference, upper_line_tr, real_time)

    def draw(self, fig, height):
        data_df = pd.DataFrame(self.data)
        min_indicator = self.indicators_list[0]['df']
        max_indicator = self.indicators_list[1]['df']
        indicator_fig = get_secondary_fig(self.indicator_name, fig, height, data_df, self.indicators_list, min_indicator, max_indicator)

        fig.circle(self.local_max_price_left, data_df.High[self.local_max_price_left], size=8, color="red")
        fig.circle(self.local_min_price_left, data_df.Low[self.local_min_price_left], size=8, color="blue")

        fig.circle(self.local_max_price_right, data_df.High[self.local_max_price_right], size=4, color="red")
        fig.circle(self.local_min_price_right, data_df.Low[self.local_min_price_right], size=4, color="blue")

        indicator_fig.circle(self.local_max_indicator_left, max_indicator.value[self.local_max_indicator_left], size=8, color="red")
        indicator_fig.circle(self.local_min_indicator_left, min_indicator.value[self.local_min_indicator_left], size=8, color="blue")

        indicator_fig.circle(self.local_max_indicator_right, max_indicator.value[self.local_max_indicator_right], size=4, color="red")
        indicator_fig.circle(self.local_min_indicator_right, min_indicator.value[self.local_min_indicator_right], size=4, color="blue")

        for i in range(len(self.idx1)):
            row = self.idx1[i]
            fig.line(x=[row[0][0], row[0][1]], y=[self.low[row[0][0]], self.low[row[0][1]]], line_color='blue', line_width=1)
            indicator_fig.line(x=[row[1][0], row[1][1]], y=[self.min_indicator[row[1][0]], self.min_indicator[row[1][1]]], line_color='blue', line_width=1)

        for i in range(len(self.idx2)):
            row = self.idx2[i]
            fig.line(x=[row[0][0], row[0][1]], y=[self.low[row[0][0]], self.low[row[0][1]]], line_color='blue', line_width=1)
            indicator_fig.line(x=[row[1][0], row[1][1]], y=[self.min_indicator[row[1][0]], self.min_indicator[row[1][1]]], line_color='blue', line_width=1)

        for i in range(len(self.idx3)):
            row = self.idx3[i]
            fig.line(x=[row[0][0], row[0][1]], y=[self.high[row[0][0]], self.high[row[0][1]]], line_color='red', line_width=1)
            indicator_fig.line(x=[row[1][0], row[1][1]], y=[self.max_indicator[row[1][0]], self.max_indicator[row[1][1]]], line_color='red', line_width=1)

        for i in range(len(self.idx4)):
            row = self.idx4[i]
            fig.line(x=[row[0][0], row[0][1]], y=[self.high[row[0][0]], self.high[row[0][1]]], line_color='red', line_width=1)
            indicator_fig.line(x=[row[1][0], row[1][1]], y=[self.max_indicator[row[1][0]], self.max_indicator[row[1][1]]], line_color='red', line_width=1)

        show(column(fig, indicator_fig, sizing_mode='stretch_both'))





