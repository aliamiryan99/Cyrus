from Visualization.Visualizer import Visualizer
from AlgorithmFactory.AlgorithmTools.LocalExtermums import *
from AlgorithmFactory.AlgorithmTools.HeikinCandle import HeikinConverter

from Indicators.KDJ import KDJ
from Indicators.RSI import RSI
from Indicators.MA import MovingAverage
from Indicators.Stochastic import Stochastic
from Indicators.MACD import MACD
from Indicators.AMA import AMA
from Indicators.Ichimoku import Ichimoku

from Visualization.Tools import *
from Visualization.BaseChart import *


class IndicatorVisualizer(Visualizer):

    def __init__(self, data, indicator_names, heikin_data_level, extremum_enable, extremum_window, extremum_mode,
                 ma_enable, ma_list, ichimoku_enable, tenkan, kijun, senkou_span_projection):
        self.data = data
        self.hikin_data_level = heikin_data_level
        self.indicator_names = indicator_names
        self.extremum_enable = extremum_enable
        self.ma_enable = ma_enable
        self.ma_list = ma_list
        self.ichimoku_enable = ichimoku_enable
        self.tenkan = tenkan
        self.kijun = kijun

        for i in range(self.hikin_data_level):
            heikin_converter = HeikinConverter(self.data[0])
            self.data = heikin_converter.convert_many(self.data[1:])

        self.local_min_price, self.local_max_price = get_local_extermums(self.data, extremum_window, extremum_mode)

        self.indicators_list = []
        self.min_indicators, self.max_indicators = [], []
        self.local_min_indicator_list, self.local_max_indicator_list = [], []

        price = [d['Close'] for d in data]

        for indicator_name in indicator_names:
            indicators = []
            if indicator_name == 'RSI':
                rsi_ind = RSI(price, 14)
                self.indicators_list.append([{'df': pd.DataFrame(rsi_ind.values).rename(columns={0: 'value'}),
                                             'color': "#3362b2", 'width': 2}])
                indicators.append(rsi_ind.values)
            elif indicator_name == 'stochastic':
                stochastic_k = Stochastic(price, 14, 3, 3, 'K')
                stochastic_d = Stochastic(price, 14, 3, 3, 'D')
                indicators.append(stochastic_k.values)
                indicators.append(stochastic_d.values)
                self.indicators_list.append([{'df': pd.DataFrame(stochastic_k.values).rename(columns={0: 'value'}),
                                             'color': "#3362b2", 'width': 2},
                                             {'df': pd.DataFrame(stochastic_d.values).rename(columns={0: 'value'}),
                                             'color': "#a36232", 'width': 2}])
            elif indicator_name == 'KDJ':
                kdj = KDJ(data, 13, 3)
                k_value, d_value, j_value = kdj.get_values()
                indicators += [k_value, d_value, j_value]
                self.indicators_list.append([{'df': pd.DataFrame(k_value).rename(columns={0: 'value'}),
                                              'color': "#3362b2", 'width': 2},
                                             {'df': pd.DataFrame(d_value).rename(columns={0: 'value'}),
                                              'color': "#a36232", 'width': 2},
                                             {'df': pd.DataFrame(j_value).rename(columns={0: 'value'}),
                                              'color': "#33c232", 'width': 2}])
            elif indicator_name == 'MACD':
                macd_indicator = MACD(price, 26, 12)
                macd_value, signal_value = macd_indicator.macd_values, macd_indicator.signal_values
                indicators += [macd_value, signal_value]
                self.indicators_list.append([{'df': pd.DataFrame(macd_value).rename(columns={0: 'value'}),
                                              'color': "#3362b2", 'width': 2},
                                             {'df': pd.DataFrame(signal_value).rename(columns={0: 'value'}),
                                              'color': "#a36232", 'width': 2}])
            elif indicator_name == 'AMA':
                indicator = AMA(price, 14, 6).get_values()
                indicators.append(indicator)
                self.indicators_list.append([{'df': pd.DataFrame(indicator).rename(columns={0: 'value'}),
                                              'color': '#3362b2', 'width': 2}])

            min_indicator, max_indicator = get_min_max_indicator(indicators)
            self.min_indicators.append(pd.DataFrame(min_indicator).rename(columns={0: 'value'}))
            self.max_indicators.append(pd.DataFrame(max_indicator).rename(columns={0: 'value'}))
            local_min_indicator, local_max_indicator = \
                get_indicator_local_extermums(max_indicator, min_indicator, extremum_window)
            self.local_min_indicator_list.append(local_min_indicator)
            self.local_max_indicator_list.append(local_max_indicator)

        self.ma_indicators = []
        if self.ma_enable:
            for ma in ma_list:
                self.ma_indicators.append(MovingAverage(data, ma['ma_type'], ma['price_type'], ma['window']))
        if self.ichimoku_enable:
            ichimoku = Ichimoku(data, tenkan, kijun, senkou_span_projection=senkou_span_projection)
            self.ichimoku_result = ichimoku.result


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

        if self.ma_enable:
            for i in range(len(self.ma_list)):
                ma = self.ma_list[i]
                ma_indicator = self.ma_indicators[i].values
                fig.line(x=list(np.arange(len(self.data))), y=ma_indicator, color=ma['color'], width=ma['width'])

        if self.ichimoku_enable:
            fig.line(x=list(np.arange(len(self.ichimoku_result['TenkanSen']))), y=self.ichimoku_result['TenkanSen'],
                     color="#ca3a64", width=1)
            fig.line(x=list(np.arange(len(self.ichimoku_result['KijunSen']))), y=self.ichimoku_result['KijunSen'],
                     color="#453af4", width=1)
            fig.line(x=list(np.arange(len(self.ichimoku_result['ChikouSpan']))), y=self.ichimoku_result['ChikouSpan'],
                     color="#3afa64", width=1)
            fig.line(x=list(np.arange(len(self.ichimoku_result['SenkouSpanA']))), y=self.ichimoku_result['SenkouSpanA'],
                     color="#fafa64", width=4)
            fig.line(x=list(np.arange(len(self.ichimoku_result['SenkouSpanB']))), y=self.ichimoku_result['SenkouSpanB'],
                     color="#3afaf4", width=4)
            # fig.line(x=list(np.arange(len(self.ichimoku_result['TenKijun']))), y=self.ichimoku_result['TenKijun'],
            #          color="#ca3af4", width=1)

        figs = [fig]
        figs += indicator_fig_list
        show(column(figs, sizing_mode='stretch_both'))



