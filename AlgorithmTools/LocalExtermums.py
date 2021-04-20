import numpy as np


def get_local_extermums(data, window, mode):         # mode 1: High Low , mode 2 : Top Bottom
    Open = np.array([d['Open'] for d in data])
    High = np.array([d['High'] for d in data])
    Low = np.array([d['Low'] for d in data])

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

    top_candle = np.array(top_candle)
    bottom_candle = np.array(bottom_candle)

    price_up = High
    price_down = Low
    if mode == 2:
        price_up = top_candle
        price_down = bottom_candle

    local_min = [0] * len(data)
    local_max = [0] * len(data)

    for i in range(window, len(Open) - window):
        if price_up[i] >= price_up[i - window:i + window+1].max() and local_max[i-1] == 0:
            local_max[i] = i
        if price_down[i] <= price_down[i - window:i + window+1].min() and local_min[i-1] == 0:
            local_min[i] = i

    local_max = np.array(list(filter(lambda num: num != 0, local_max)))
    local_min = np.array(list(filter(lambda num: num != 0, local_min)))

    return local_min, local_max


def get_indicator_local_extermums(max_data, min_data, window):
    max_data = np.array(max_data)
    min_data = np.array(min_data)

    local_max = [0] * len(max_data)
    local_min = [0] * len(min_data)

    for i in range(window, len(min_data) - window):
        if min_data[i] <= min_data[i - window:i + window+1].min():
            local_min[i] = i
        if max_data[i] >= max_data[i - window:i + window+1].max():
            local_max[i] = i

    local_max = np.array(list(filter(lambda num: num != 0, local_max)))
    local_min = np.array(list(filter(lambda num: num != 0, local_min)))

    return local_min, local_max


def get_local_extermums_asymetric(data, window, alpha, mode):
    Open = np.array([d['Open'] for d in data])
    High = np.array([d['High'] for d in data])
    Low = np.array([d['Low'] for d in data])

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

    top_candle = np.array(top_candle)
    bottom_candle = np.array(bottom_candle)

    price_up = High
    price_down = Low
    if mode == 2:
        price_up = top_candle
        price_down = bottom_candle

    local_min = [0] * len(data)
    local_max = [0] * len(data)

    up_window = max(round(window/alpha), 0)
    for i in range(window, len(Open) - up_window):
        if price_up[i] >= price_up[i - window:i + up_window+1].max():
            local_max[i] = i
        if price_down[i] <= price_down[i - window:i + up_window+1].min():
            local_min[i] = i

    local_max = np.array(list(filter(lambda num: num != 0, local_max)))
    local_min = np.array(list(filter(lambda num: num != 0, local_min)))

    return local_min, local_max


def get_indicator_local_extermums_asymetric(max_data, min_data, window, alpha):
    max_data = np.array(max_data)
    min_data = np.array(min_data)

    local_max = [0] * len(max_data)
    local_min = [0] * len(min_data)

    up_window = max(round(window/alpha), 0)
    for i in range(window, len(min_data) - up_window):
        if max_data[i] >= max_data[i - window:i + up_window+1].max():
            local_max[i] = i
        if min_data[i] <= min_data[i - window:i + up_window+1].min():
            local_min[i] = i

    local_max = np.array(list(filter(lambda num: num != 0, local_max)))
    local_min = np.array(list(filter(lambda num: num != 0, local_min)))

    return local_min, local_max


def get_last_local_extermum(data, window):
    localMin, localMax = get_local_extermums(data, window, 1)
    return localMin[-1], localMax[-1]


def update_local_extremum(local_extremum):
    while local_extremum[0] <= 0:
        local_extremum = local_extremum[1:]
    for i in range(len(local_extremum)):
        local_extremum[i] -= 1
    return local_extremum


def update_new_local_extremum(pre_local_extremum, new_local_extremum, total_window, local_window):
    for i in range(len(new_local_extremum)):
        new_local = new_local_extremum[i] + (total_window - local_window - 1)
        if not new_local in pre_local_extremum:
            pre_local_extremum = np.append(pre_local_extremum, [new_local])
    return pre_local_extremum

