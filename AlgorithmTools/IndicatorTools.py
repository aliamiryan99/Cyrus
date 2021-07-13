
from Indicators.KDJ import KDJ
from Indicators.RSI import RSI
from Indicators.Stochastic import Stochastic
from Indicators.MACD import MACD
from Indicators.AMA import AMA

import numpy as np


def get_min_max_indicator(indicators):
    values = np.array(indicators)

    min_indicator_value = np.min(values, axis=0)
    max_indicator_value = np.max(values, axis=0)

    return min_indicator_value, max_indicator_value


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
