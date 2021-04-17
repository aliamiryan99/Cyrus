
def pattern_detect(window, window_size):
    # %% -------- find Top and ciel value of each candle
    winSize = len(window)
    topCandle = [0] * winSize
    bottomCandle = [0] * winSize

    for i in range(0, winSize):
        # store the top/bottom value of all candles
        if window[i]['Open'] > window[i]['Close']:
            topCandle[i] = window[i]['Open']
            bottomCandle[i] = window[i]['Close']
        else:
            topCandle[i] = window[i]['Close']
            bottomCandle[i] = window[i]['Open']

    # -- check the decreasing trend reversion
    cnt = 0
    for j in range(0, window_size):
        if (topCandle[- j - 1] <= topCandle[- j - 2]) or (window[- j - 1]['Open'] > window[- j - 1]['Close']):
            cnt += 1
    if cnt == window_size:
        return 1

    # -- check the increasing trend reversion
    cnt = 0
    for j in range(0, window_size):
        if (bottomCandle[- j - 1] >= bottomCandle[- j - 2]) or (window[- j - 1]['Open'] < window[- j - 1]['Close']):
            cnt += 1
    if cnt == window_size:
        return -1

    return 0

