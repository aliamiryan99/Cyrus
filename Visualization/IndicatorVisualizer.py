
from AlgorithmTools.LocalExtermums import *
from AlgorithmTools.HeikinCandle import HeikinConverter

from Indicators.KDJ import KDJ
from Indicators.RSI import RSI
from Indicators.Stochastic import Stochastic
from Visualization.Tools import *
from Visualization.BaseChart import *


class IndicatorVisualizer:

    def __init__(self, data, indicator_names, heikin_data_level, extremum_enable, extremum_window, extremum_mode,
                 ma_enable, ma_list):
        self.data = data
        self.hikin_data_level = heikin_data_level
        self.indicator_names = indicator_names
        self.extremum_enable = extremum_enable

        for i in range(self.hikin_data_level):
            heikin_converter = HeikinConverter(self.data[0])
            self.data = heikin_converter.convert_many(self.data[1:])

        self.local_min_price, self.local_max_price = get_local_extermums(self.data, extremum_window, extremum_mode)

        self.indicators_list = []
        self.min_indicators, self.max_indicators = [], []
        self.local_min_indicator_list, self.local_max_indicator_list = [], []

        for indicator_name in indicator_names:
            indicators = []
            if indicator_name == 'rsi':
                rsi_ind = RSI(data, 14)
                self.indicators_list.append([{'df': pd.DataFrame(rsi_ind.values).rename(columns={0: 'value'}),
                                             'color': "#3362b2", 'width': 2}])
                indicators.append(rsi_ind.values)
            elif indicator_name == 'stochastic':
                stochastic_k = Stochastic(data, 14, 3, 3, 'K')
                stochastic_d = Stochastic(data, 14, 3, 3, 'D')
                indicators.append(stochastic_k.values)
                indicators.append(stochastic_d.values)
                self.indicators_list.append([{'df': pd.DataFrame(stochastic_k.values).rename(columns={0: 'value'}),
                                             'color': "#3362b2", 'width': 2},
                                             {'df': pd.DataFrame(stochastic_d.values).rename(columns={0: 'value'}),
                                             'color': "#a36232", 'width': 2}])
            elif indicator_name == 'kdj':
                kdj = KDJ(data, 13, 3)
                k_value, d_value, j_value = kdj.get_values()
                indicators += [k_value, d_value, j_value]
                self.indicators_list.append([{'df': pd.DataFrame(k_value).rename(columns={0: 'value'}),
                                              'color': "#3362b2", 'width': 2},
                                             {'df': pd.DataFrame(d_value).rename(columns={0: 'value'}),
                                              'color': "#a36232", 'width': 2},
                                             {'df': pd.DataFrame(j_value).rename(columns={0: 'value'}),
                                              'color': "#33c232", 'width': 2}])
            min_indicator, max_indicator = get_min_max_indicator(indicators)
            self.min_indicators.append(pd.DataFrame(min_indicator).rename(columns={0: 'value'}))
            self.max_indicators.append(pd.DataFrame(max_indicator).rename(columns={0: 'value'}))
            local_min_indicator, local_max_indicator = \
                get_indicator_local_extermums(max_indicator, min_indicator, extremum_window)
            self.local_min_indicator_list.append(local_min_indicator)
            self.local_max_indicator_list.append(local_max_indicator)


    def draw(self, fig, height):
        data_df = pd.DataFrame(self.data)
        indicator_fig_list = []
        for i in range(len(self.indicator_names)):
            indicator_name = self.indicator_names[i]
            indicator_fig = get_secondary_fig(indicator_name, fig, height, data_df, self.indicators_list[i],
                                              self.min_indicators[i], self.max_indicators[i])
            if self.extremum_enable:
                indicator_fig.circle(self.local_max_indicator_list[i],
                                     self.max_indicators[i].value[self.local_max_indicator_list[i]],
                                     size=8, color="red")
                indicator_fig.circle(self.local_min_indicator_list[i],
                                     self.min_indicators[i].value[self.local_min_indicator_list[i]],
                                     size=8, color="blue")
            indicator_fig_list.append(indicator_fig)

        if self.extremum_enable:
            fig.circle(self.local_max_price, data_df.High[self.local_max_price], size=8, color="red")
            fig.circle(self.local_min_price, data_df.Low[self.local_min_price], size=8, color="blue")

        figs = [fig]
        figs += indicator_fig_list
        show(column(figs, sizing_mode='stretch_both'))





