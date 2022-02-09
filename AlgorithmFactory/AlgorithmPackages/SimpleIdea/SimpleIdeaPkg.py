
from Shared.Variables import Variables


def simple_idea(symbol, data, win_inc, win_dec, shadow_threshold, body_threshold, mode, mean_window):     # mode 1 : Simlpe , mode 2 : average condition , mode 3 : impulse condition

    shadow_threshold *= (10 ** -Variables.config.symbols_pip[symbol])
    body_threshold *= (10 ** -Variables.config.symbols_pip[symbol])
    # -- check the decreasing trend reversion

    if mode == 2:
        body_mean = 0
        for i in range(mean_window):
            body_mean += abs(data[-i-1]['Close'] - data[-i-1]['Open']) / mean_window
        if abs(data[-1]['Close'] - data[-1]['Open']) < body_mean or abs(data[-2]['Close'] - data[-2]['Open']) < body_mean:
            return 0

    cnt = 0
    for j in range(0, win_dec):
        if max(data[- j - 2]['Open'], data[- j - 2]['Close']) <= max(data[- j - 3]['Open'], data[- j - 3]['Close']) or (data[- j - 2]['Open'] > data[- j - 2]['Close'] + body_threshold):
            cnt += 1
    if (cnt == win_dec) and (data[-1]['Open'] + body_threshold < data[-1]['Close']) and max(data[-2]['Open'], data[-2]['Close']) <= max(data[-1]['Open'], data[-1]['Close']):        #   it can be replaced by  bottomCandle[-2] < bottomCandle[-1]:
        return 1

    # -- check the increasing trend reversion
    cnt = 0
    for j in range(0, win_inc):
        if min(data[- j - 2]['Open'], data[- j - 2]['Close']) >= min(data[- j - 3]['Open'], data[- j - 3]['Close']) or (data[- j - 2]['Open'] + body_threshold < data[- j - 2]['Close']):
            cnt += 1
    if (cnt == win_inc) and (data[-1]['Open'] > data[-1]['Close'] + body_threshold) and min(data[-2]['Open'], data[-2]['Close']) >= min(data[-1]['Open'], data[-1]['Close']):          #   it can be replaced by  topCnadle[-2] > topCnadle[-1]:
        return -1

    return 0


def get_detected_simple_idea(data, symbol, window, shadow_threshold, body_threshold, mode, mean_window):
    detected_list = []
    for i in range(window+5, len(data)):
        result = simple_idea(symbol, data[i-window-4:i], window, window, shadow_threshold, body_threshold, mode, mean_window)
        if result != 0:
            detected_list.append({'Index': i-1, 'Time': data[i-1]['Time'], 'Price':data[i-1]['Low'], 'Direction': result})
    return detected_list
