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

from AlgorithmFactory.AlgorithmTools.CandleTools import *


class RsiPattern(Visualizer):

    def __init__(self, data, indicator_params):

        self.data = data
        self.indicator_name = indicator_params['Name']

        self.indicator_values = []
        self.line70 = []
        self.line50 = []
        self.line30 = []
        self.open = []
        self.close = []
        self.high = []
        self.low = []

        # ----------------- || main body of indicator || -----------------
        for i in range(len(self.data)):
            self.open.append(self.data[i]['Open'])
            self.close.append(self.data[i]['Close'])
            self.high.append(self.data[i]['High'])
            self.low.append(self.data[i]['Low'])

        self.open, self.high, self.low, self.close = get_ohlc(data)
        middle = get_middle(data)

        src = middle

        # Extract Indicator
        rsi, _ = self.get_indicator(indicator_params, src)

        self.indicators_list = []
        self.indicators_list.append(
            {'df': pd.DataFrame(rsi).rename(columns={0: 'value'}), 'color': "#a36232", 'width': 2})

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
                                            if (sections[p] == 'middleMinus' or sections[p] == 'middlePlus') and rsi[p] \
                                                    > rsi[k] and (((k - j) / (l - k)) >= tr_kj_lk) and min(
                                                rsi[l + 1:p + 1]) > \
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
                    if sections[j] == 'overbought' and max(rsi[i:j]) < rsi[j] and min(rsi[i + 1:j + 1]) > rsi[i]:
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

        for i in range(len(self.buy_idx_value) - 1):
            self.buy_idx_value[i] = (newMax - newMin) / (Max - Min) * (self.buy_idx_value[i] - Max) + newMax

        for i in range(len(self.sell_idx_value) - 1):
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

    def draw(self, fig, height):
        data_df = pd.DataFrame(self.data)
        fig = get_base_fig(data_df, ChartConfig.symbol)

        min_indicator = self.indicators_list[0]['df']
        max_indicator = self.indicators_list[0]['df']
        indicator_fig = get_secondary_fig(self.indicator_name, fig, height, data_df, self.indicators_list,
                                          min_indicator, max_indicator)

        buys = [buy_item[4] for buy_item in self.buy_idx]
        sells = [sell_item[4] for sell_item in self.sell_idx]

        fig.circle(sells, self.close[sells], size=8,color="red")
        fig.circle(buys, self.close[buys], size=8, color="blue")

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
