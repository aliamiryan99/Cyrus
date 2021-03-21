def RefinementSI(window, winInc, winDec):
    # %% -------- find Top and ciel value of each candle
    winSize = len(window)
    topCandle = [0] * winSize
    bottomCandle = [0] * winSize

    for i in range(0, winSize):
        # store the top/bottom value of all candles
        if window[i]['open'] > window[i]['close']:
            topCandle[i] = window[i]['open']
            bottomCandle[i] = window[i]['close']
        else:
            topCandle[i] = window[i]['close']
            bottomCandle[i] = window[i]['open']

    # %% ---------  find up/down trend and wait for its reversion
    # winInc = 5
    # winDec = 5

    # -- check the decreasing trend reversion
    cnt = 0
    for j in range(0, winDec):
        if (topCandle[winSize - j - 2] <= topCandle[winSize - j - 3]) and (window[winSize - j - 2]['open'] > window[winSize - j - 2]['close']):
            cnt += 1
    if (cnt == winDec) and window[winSize - 1]['high'] > window[winSize-3]['high']:
        return 1, window[winSize-3]['high']

    # -- check the increasing trend reversion
    cnt = 0
    for j in range(0, winInc):
        if (bottomCandle[winSize - j - 2] >= bottomCandle[winSize - j - 3]) and (window[winSize - j - 2]['open'] < window[winSize - j - 2]['close']):
            cnt += 1
    if (cnt == winInc) and window[winSize - 1]['low'] < window[winSize-3]['low']:
        return -1, window[winSize-3]['low']

    return 0, 0

