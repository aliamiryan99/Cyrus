
def refinement_si(window, win_inc, win_dec, pivot):
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

    # %% ---------  find up/down trend and wait for its reversion
    # winInc = 5
    # winDec = 5

    # -- check the decreasing trend reversion
    cnt = 0
    for j in range(0, win_dec):
        if topCandle[-j - 2] <= topCandle[-j - 3] and window[-j - 2]['Close'] < window[-j - 2]['Open']:
            cnt += 1
    if cnt == win_dec and window[-1]['High'] > window[-pivot-1]['High']:
        return 1, window[-pivot-1]['High']

    # -- check the increasing trend reversion
    cnt = 0
    for j in range(0, win_inc):
        if bottomCandle[-j - 2] >= bottomCandle[-j - 3] and window[-j - 2]['Close'] > window[-j - 2]['Open']:
            cnt += 1
    if cnt == win_inc and window[-1]['Low'] < window[-pivot-1]['Low']:
        return -1, window[-pivot-1]['Low']

    return 0, 0

