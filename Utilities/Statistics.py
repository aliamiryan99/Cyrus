
from AlgorithmFactory.AlgorithmTools.CandleTools import *


def get_bullish_bearish_ratio(data, signal_indexes, window):
    result = []
    open, high, low, close = get_ohlc(data)
    for i in range(len(signal_indexes)):
        if signal_indexes[i] < len(data) - window:
            result.append({})
            result[-1]['BullishRatio'] = (high[signal_indexes[i]+1:signal_indexes[i]+window+1].max() / close[signal_indexes[i]] - 1) * 100
            result[-1]['BearishRatio'] = (low[signal_indexes[i]+1:signal_indexes[i]+window+1].min() / close[signal_indexes[i]] - 1) * 100
            result[-1]['FirstIncome'] = "Bull" if high[signal_indexes[i]+1:signal_indexes[i]+window+1].argmax() <= low[signal_indexes[i]+1:signal_indexes[i]+window+1].argmin() else "Bear"
    return result


def get_min_max_mean(input_list):
    from statistics import mean
    return min(input_list), max(input_list), mean(input_list)
