
from Shared.Variables import Variables

import operator as op
from functools import reduce


def calc_volume(open_positions, mode, volume_alpha, fix_tp, history):
    volume = 0
    if mode == 1:
        volume = open_positions[-1]['Volume'] * volume_alpha
    elif mode == 2:
        volume = open_positions[-1]['Volume'] *\
                 (abs(history[-2]['Open'] - history[-1]['Open']) / fix_tp) * volume_alpha
    elif mode == 3:
        volume = 0
        for position in open_positions:
            volume += position['Volume']
        volume *= volume_alpha
    elif mode == 4:
        volume = open_positions[-1]['Volume'] * (abs(open_positions[-1]['OpenPrice'] - history[-1]['Close']) / fix_tp)
    elif mode == 5:
        volume = open_positions[-1]['Volume'] * (abs(open_positions[-1]['OpenPrice'] - history[-1]['Close']) / fix_tp)\
                 * (len(open_positions) + 1)
    elif mode == 6:
        volume = open_positions[0]['Volume'] * (len(open_positions) + 1)
    elif mode == 7:
        volume = open_positions[0]['Volume'] * ncr(3, len(open_positions))
    return volume


def calc_tp(open_positions, price, volume, mode, tp_alpha, fix_tp):
    tp = 0
    if mode == 1:
        tp = fix_tp
    elif mode == 2:
        tp = fix_tp * (len(open_positions) + 1)
    elif mode == 3:
        tp = abs(open_positions[-1]['OpenPrice'] * tp_alpha +
                 price * (1 - tp_alpha) - price)
    elif mode == 4:
        vp_sum, v_sum = 0, 0
        for i in range(len(open_positions)):
            vp_sum += open_positions[i]['OpenPrice'] * open_positions[i]['Volume']
            v_sum += open_positions[i]['Volume']
        volume = min(volume, Variables.config.max_volume)
        vp_sum += price * volume
        v_sum += volume
        symbol = open_positions[0]['Symbol']
        tp = abs((vp_sum/v_sum) - price) + Variables.config.spreads[symbol] * 2
    return tp


def ncr(n, r):
    r = min(r, n-r)
    numer = reduce(op.mul, range(n, n-r, -1), 1)
    denom = reduce(op.mul, range(1, r+1), 1)
    return numer // denom  # or / in Python 2

