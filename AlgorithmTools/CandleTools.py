import numpy as np


def get_bottom_top(data):
    top_candle = []
    bottom_candle = []

    for i in range(0, len(data)):
        # store the top/bottom value of all candles
        if data[i]['Open'] > data[i]['Close']:
            top_candle.append(data[i]['Open'])
            bottom_candle.append(data[i]['Close'])
        else:
            top_candle.append(data[i]['Close'])
            bottom_candle.append(data[i]['Open'])
    bottom_candle, top_candle = np.array(bottom_candle), np.array(top_candle)
    return bottom_candle, top_candle


def get_body_total_length(data):
    body_length = []
    total_length = []
    for candle in data:
        body_length.append(abs(candle['Close'] - candle['Open']))
        total_length.append(abs(candle['High'] - candle['Low']))
    return np.array(body_length), np.array(total_length)


def get_ohlc(data):
    open = np.array([d['Open'] for d in data])
    high = np.array([d['High'] for d in data])
    low = np.array([d['Low'] for d in data])
    close = np.array([d['Close'] for d in data])
    return open, high, low, close


def get_body_mean(data, window):
    body_mean = 0
    for i in range(1, window+1):
        body_mean += abs(data[-i]['Open'] - data[-1]['Close']) / window
    return body_mean


def update_top_bottom(top, bottom, candle):
    top, bottom = top[1:], bottom[1:]
    top = np.append(top, max(candle['Open'], candle['Close']))
    bottom = np.append(bottom, min(candle['Open'], candle['Close']))
    return top, bottom


def update_ohlc(open, high, low, close, candle):
    open, high, low, clsoe = open[1:], high[1:], low[1:], close[1:]
    open = np.append(open, candle['Open'])
    high = np.append(high, candle['High'])
    low = np.append(low, candle['Low'])
    close = np.append(close, candle['Close'])
    return open, high, low, close
