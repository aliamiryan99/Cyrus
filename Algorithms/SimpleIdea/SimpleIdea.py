from Simulation.Config import Config as S_Config
from MetaTrader.Config import Config as MT_Config

def simpleIdea(symbol, data, winInc, winDec, shadow_threshold, body_threshold, mode, mean_window):     # mode 1 : Simlpe , mode 2 : average condition , mode 3 : impulse condition
    win_size = len(data)

    Config = S_Config
    if symbol not in S_Config.symbols_pip.keys():
        Config = MT_Config
    shadow_threshold *= (10 ** -Config.symbols_pip[symbol])
    body_threshold *= (10 ** -Config.symbols_pip[symbol])
    # -- check the decreasing trend reversion

    if mode == 2:
        body_mean = 0
        for i in range(mean_window):
            body_mean += abs(data[-i-1]['Close'] - data[-i-1]['Open']) / mean_window
        if abs(data[-1]['Close'] - data[-1]['Open']) < body_mean or abs(data[-2]['Close'] - data[-2]['Open']) < body_mean:
            return 0

    cnt = 0
    for j in range(0, winDec):
        if max(data[- j - 2]['Open'], data[- j - 2]['Close']) <= max(data[- j - 3]['Open'], data[- j - 3]['Close']) or (data[- j - 2]['Open'] > data[- j - 2]['Close'] + body_threshold):
            cnt += 1
    if (cnt == winDec) and (data[-1]['Open'] + body_threshold < data[-1]['Close']) and max(data[-2]['Open'], data[-2]['Close']) <= max(data[-1]['Open'], data[-1]['Close']):        #   it can be replaced by  bottomCandle[-2] < bottomCandle[-1]:
        return 1

    # -- check the increasing trend reversion
    cnt = 0
    for j in range(0, winInc):
        if min(data[- j - 2]['Open'], data[- j - 2]['Close']) >= min(data[- j - 3]['Open'], data[- j - 3]['Close']) or (data[- j - 2]['Open'] + body_threshold < data[- j - 2]['Close']):
            cnt += 1
    if (cnt == winInc) and (data[-1]['Open'] > data[-1]['Close'] + body_threshold) and min(data[-2]['Open'], data[-2]['Close']) >= min(data[-1]['Open'], data[-1]['Close']):          #   it can be replaced by  topCnadle[-2] > topCnadle[-1]:
        return -1

    return 0

