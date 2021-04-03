
from Simulation.Config import Config as S_Config
from MetaTrader.Config import Config as MT_Config


def sequence_find(symbol, window, win_inc, win_dec, shadow_threshold, body_threshold):

    Config = S_Config
    if symbol in MT_Config.symbols_pip.keys():
        Config = MT_Config
    shadow_threshold *= (10 ** -Config.symbols_pip[symbol])
    body_threshold *= (10 ** -Config.symbols_pip[symbol])

    cnt = 0
    if window[-win_inc-1]['Close'] < window[-win_inc-1]['Open']:
        for j in range(0, win_inc):
            if window[- j - 1]['Close'] > window[-j - 1]['Open']:
                cnt += 1
        if cnt == win_inc:
            return 1

    cnt = 0
    if window[-win_dec - 1]['Close'] > window[-win_dec - 1]['Open']:
        for j in range(0, win_dec):
            if window[- j - 1]['Close'] < window[-j - 1]['Open']:
                cnt += 1
        if cnt == win_dec:  #
            return -1

    return 0

