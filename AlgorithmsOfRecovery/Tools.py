

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
    return volume


def calc_tp(open_positions, price, mode, tp_alpha, fix_tp):
    tp = 0
    if mode == 1:
        tp = fix_tp
    elif mode == 2:
        tp = fix_tp * (len(open_positions) + 1)
    elif mode == 3:
        tp = abs(open_positions[-1]['OpenPrice'] * tp_alpha +
                 price * (1 - tp_alpha) - price)
    return tp
