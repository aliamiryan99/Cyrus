from Visualization.Visualizer import Visualizer
from AlgorithmFactory.AlgorithmTools.LocalExtermums import *
from AlgorithmFactory.AlgorithmTools.HeikinCandle import HeikinConverter
from AlgorithmFactory.AlgorithmPackages.Divergence.DivergencePkg import divergence_calculation

from Indicators.KDJ import KDJ
from Indicators.RSI import RSI
from Indicators.Stochastic import Stochastic
from Indicators.MACD import MACD
from Indicators.AMA import AMA
from Visualization.Tools import *
from Visualization.BaseChart import *

from AlgorithmFactory.AlgorithmTools.CandleTools import *
from Configuration.Tools.LocalToolsConfig import ChartConfig


class DivergenceVisualizer(Visualizer):

    def __init__(self, data, heikin_data_level, indicator_params, extremum_window, asymmetric_extremum_window,
                 asymmetric_alpha, hidden_divergence_check_window, upper_line_tr):
        # Paramaeters
        self.data = data
        self.hikin_data_level = heikin_data_level
        self.indicator_name = indicator_params['Name']
        # Extract Heikin Data
        for i in range(self.hikin_data_level):
            heikin_converter = HeikinConverter(self.data[0])
            self.data = heikin_converter.convert_many(self.data[1:])

        # Extract Data
        self.open, self.high, self.low, self.close = get_ohlc(self.data)
        self.b, self.a = get_bottom_top(self.data)
        self.middle = get_middle_hl(self.data)

        # Extract Local Extremum
        self.local_min_price_left, self.local_max_price_left = get_local_extermums(self.data, extremum_window, 1)
        self.local_min_price_right, self.local_max_price_right = \
            get_local_extermums_asymetric(self.data, asymmetric_extremum_window, asymmetric_alpha, 1)

        # Extract Indicator
        self.min_indicator, self.max_indicator = self.get_indicator(indicator_params, self.close)

        # Extract Indicator Extremum
        self.local_min_indicator_left, self.local_max_indicator_left = get_indicator_local_extermums(self.max_indicator,
                                                                                                     self.min_indicator,
                                                                                                     extremum_window)
        self.local_min_indicator_right, self.local_max_indicator_right = get_indicator_local_extermums_asymetric(
            self.max_indicator, self.min_indicator, asymmetric_extremum_window, asymmetric_alpha)

        real_time = False
        # Extract Pip Difference
        body_avg = np.mean(self.a - self.b)
        pip_difference = body_avg * 1.5

        # --- bullish divergence
        trend_direction = 1
        down_direction = 0
        [self.idx1, self.val1] = divergence_calculation(self.b, self.low, self.min_indicator,
                                                                self.local_min_price_left,
                                                                self.local_min_price_right,
                                                                self.local_min_indicator_left,
                                                                self.local_min_indicator_right,
                                                                hidden_divergence_check_window,
                                                                down_direction, trend_direction, pip_difference,
                                                                upper_line_tr, real_time)
        trend_direction = 1
        down_direction = 1
        [self.idx2, self.val2] = divergence_calculation(self.b, self.low, self.min_indicator,
                                                                self.local_min_price_left,
                                                                self.local_min_price_right,
                                                                self.local_min_indicator_left,
                                                                self.local_min_indicator_right,
                                                                hidden_divergence_check_window,
                                                                down_direction, trend_direction, pip_difference,
                                                                upper_line_tr, real_time)
        # --- bearish divergence
        trend_direction = 0
        down_direction = 0
        [self.idx3, self.val3] = divergence_calculation(self.a, self.high, self.max_indicator,
                                                                self.local_max_price_left,
                                                                self.local_max_price_right,
                                                                self.local_max_indicator_left,
                                                                self.local_max_indicator_right,
                                                                hidden_divergence_check_window,
                                                                down_direction, trend_direction, pip_difference,
                                                                upper_line_tr, real_time)
        trend_direction = 0
        down_direction = 1
        [self.idx4, self.val4] = divergence_calculation(self.a, self.high, self.max_indicator,
                                                                self.local_max_price_left,
                                                                self.local_max_price_right,
                                                                self.local_max_indicator_left,
                                                                self.local_max_indicator_right,
                                                                hidden_divergence_check_window,
                                                                down_direction, trend_direction, pip_difference,
                                                                upper_line_tr, real_time)
        self.indicators_list = []
        self.indicators_list.append(
            {'df': pd.DataFrame(self.min_indicator).rename(columns={0: 'value'}), 'color': "#a36232", 'width': 2})
        self.indicators_list.append(
            {'df': pd.DataFrame(self.max_indicator).rename(columns={0: 'value'}), 'color': "#1263a9", 'width': 2})

    def draw(self, fig, height):
        data_df = pd.DataFrame(self.data)
        fig = get_base_fig(data_df, ChartConfig.symbol)

        min_indicator = self.indicators_list[0]['df']
        max_indicator = self.indicators_list[1]['df']
        indicator_fig = get_secondary_fig(self.indicator_name, fig, height, data_df, self.indicators_list,
                                          min_indicator, max_indicator)

        fig.circle(self.local_max_price_left, data_df.High[self.local_max_price_left], size=8, color="red")
        fig.circle(self.local_min_price_left, data_df.Low[self.local_min_price_left], size=8, color="blue")

        fig.circle(self.local_max_price_right, data_df.High[self.local_max_price_right], size=4, color="red")
        fig.circle(self.local_min_price_right, data_df.Low[self.local_min_price_right], size=4, color="blue")

        indicator_fig.circle(self.local_max_indicator_left, max_indicator.value[self.local_max_indicator_left], size=8,
                             color="red")
        indicator_fig.circle(self.local_min_indicator_left, min_indicator.value[self.local_min_indicator_left], size=8,
                             color="blue")

        indicator_fig.circle(self.local_max_indicator_right, max_indicator.value[self.local_max_indicator_right],
                             size=4, color="red")
        indicator_fig.circle(self.local_min_indicator_right, min_indicator.value[self.local_min_indicator_right],
                             size=4, color="blue")

        for i in range(len(self.idx1)):
            row = self.idx1[i]
            fig.line(x=[row[0][0], row[0][1]], y=[self.low[row[0][0]], self.low[row[0][1]]], line_color='blue',
                     line_width=1)
            indicator_fig.line(x=[row[1][0], row[1][1]],
                               y=[self.min_indicator[row[1][0]], self.min_indicator[row[1][1]]], line_color='blue',
                               line_width=1)

        for i in range(len(self.idx2)):
            row = self.idx2[i]
            fig.line(x=[row[0][0], row[0][1]], y=[self.low[row[0][0]], self.low[row[0][1]]], line_color='blue',
                     line_width=1)
            indicator_fig.line(x=[row[1][0], row[1][1]],
                               y=[self.min_indicator[row[1][0]], self.min_indicator[row[1][1]]], line_color='blue',
                               line_width=1)

        for i in range(len(self.idx3)):
            row = self.idx3[i]
            fig.line(x=[row[0][0], row[0][1]], y=[self.high[row[0][0]], self.high[row[0][1]]], line_color='red',
                     line_width=1)
            indicator_fig.line(x=[row[1][0], row[1][1]],
                               y=[self.max_indicator[row[1][0]], self.max_indicator[row[1][1]]], line_color='red',
                               line_width=1)

        for i in range(len(self.idx4)):
            row = self.idx4[i]
            fig.line(x=[row[0][0], row[0][1]], y=[self.high[row[0][0]], self.high[row[0][1]]], line_color='red',
                     line_width=1)
            indicator_fig.line(x=[row[1][0], row[1][1]],
                               y=[self.max_indicator[row[1][0]], self.max_indicator[row[1][1]]], line_color='red',
                               line_width=1)

        show(column(fig, indicator_fig, sizing_mode='stretch_both'))

    @staticmethod
    def get_indicator(params, price):
        indicator_name = params['Name']
        indicators = []
        if indicator_name == 'RSI':
            rsi_ind = RSI(price, params['Window'])
            indicators.append(rsi_ind.values)
        elif indicator_name == 'Stochastic':
            stochastic_k = Stochastic(price, params['Window'], params['Smooth1'], params['Smooth2'], 'K')
            stochastic_d = Stochastic(price, params['Window'], params['Smooth1'], params['Smooth2'], 'D')
            indicators.append(stochastic_k.values)
            indicators.append(stochastic_d.values)
        elif indicator_name == 'KDJ':
            kdj = KDJ(price, params['WindowK'], params['WindowD'])
            k_value, d_value, j_value = kdj.get_values()
            indicators += [k_value, d_value, j_value]
        elif indicator_name == 'MACD':
            macd_indicator = MACD(price, params['WindowSlow'], params['WindowFast'])
            macd_value, signal_value = macd_indicator.macd_values, macd_indicator.signal_values
            indicators += [macd_value, signal_value]
        elif indicator_name == 'AMA':
            ama_indicator = AMA(price, params['Window'], params['WindowSF'])
            indicators += [ama_indicator.get_values()]

        min_indicator, max_indicator = get_min_max_indicator(indicators)
        return min_indicator, max_indicator


def polynomial_coff(num):
    x = np.arange(1, num + 1)
    return 1 / x ** 0.3
