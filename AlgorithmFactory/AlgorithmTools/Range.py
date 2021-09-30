
from AlgorithmFactory.AlgorithmTools.CandleTools import *


def detect_range_region(data, range_candle_threshold):

    open, high, low , close = get_ohlc(data)
    bottom, top = get_bottom_top(data)

    in_range_candles = 0
    top_region = high[0]
    bottom_region = low[0]

    results = []

    for i in range(1, len(data)):
        if top[i] < high[i-1] and bottom[i] > low[i-1]:
            in_range_candles += 1
            if high[i] > top_region:
                top_region = high[i]
            if low[i] < bottom_region:
                bottom_region = low[i]
        else:
            if in_range_candles >= range_candle_threshold:
                results.append({'Start': i-in_range_candles-1, 'End': i, 'BottomRegion': bottom_region, 'TopRegion': top_region})
            in_range_candles = 0
            top_region = high[i]
            bottom_region = low[i]

    return results
