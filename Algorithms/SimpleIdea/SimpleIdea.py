from Simulation.Config import Config as S_Config
from MetaTrader.Config import Config as MT_Config

def simpleIdea(symbol, window, winInc, winDec, shadow_threshold, body_threshold):
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
    Config = S_Config
    if symbol not in S_Config.symbols_pip.keys():
        Config = MT_Config
    shadow_threshold *= (10 ** -Config.symbols_pip[symbol])
    body_threshold *= (10 ** -Config.symbols_pip[symbol])
    # -- check the decreasing trend reversion
    cnt = 0
    for j in range(0, winDec):
        if (topCandle[winSize - j - 2] <= topCandle[winSize - j - 3]) or (window[winSize - j - 2]['Open'] > window[winSize - j - 2]['Close'] + body_threshold):
            cnt += 1
    if (cnt == winDec) and (window[-1]['Open'] + body_threshold < window[-1]['Close']) and topCandle[-2] <= topCandle[-1]:        #   it can be replaced by  bottomCandle[-2] < bottomCandle[-1]:
        return 1

    # -- check the increasing trend reversion
    cnt = 0
    for j in range(0, winInc):
        if (bottomCandle[winSize - j - 2] >= bottomCandle[winSize - j - 3]) or (window[winSize - j - 2]['Open'] + body_threshold  < window[winSize - j - 2]['Close']):
            cnt += 1
    if (cnt == winInc) and (window[-1]['Open'] > window[-1]['Close'] + body_threshold) and bottomCandle[-2] >= bottomCandle[-1]:          #   it can be replaced by  topCnadle[-2] > topCnadle[-1]:
        return -1

    return 0

