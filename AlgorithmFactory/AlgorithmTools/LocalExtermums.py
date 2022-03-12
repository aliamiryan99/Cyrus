from AlgorithmFactory.AlgorithmTools.CandleTools import *


def get_local_extermums(data, window, mode):         # mode 1: High Low , mode 2 : Top Bottom

    open, high, low, close = get_ohlc(data)
    bottom, top = get_bottom_top(data)

    price_up, price_down = high, low
    if mode == 2:
        price_up, price_down = top, bottom

    local_min = [0] * len(data)
    local_max = [0] * len(data)

    for i in range(window, len(open) - window):
        if price_up[i] >= price_up[i - window:i + window+1].max() and local_max[i-1] == 0:
            local_max[i] = i
        if price_down[i] <= price_down[i - window:i + window+1].min() and local_min[i-1] == 0:
            local_min[i] = i

    local_max = np.array(list(filter(lambda num: num != 0, local_max)))
    local_min = np.array(list(filter(lambda num: num != 0, local_min)))

    return local_min, local_max


def filter_extremums(data, window, mode, local_min, local_max, atr_tr):
    open, high, low, close = get_ohlc(data)
    bottom, top = get_bottom_top(data)

    price_up, price_down = high, low
    if mode == 2:
        price_up, price_down = top, bottom

    atr = get_body_mean(data, len(data))

    new_local_min = []
    for i in range(len(local_min)):
        if calculate_area_diff(price_down, window, local_min[i]) >= atr_tr * atr:
            new_local_min.append(local_min[i])
    new_local_max = []
    for i in range(len(local_max)):
        if calculate_area_diff(price_up, window, local_max[i]) >= atr_tr * atr:
            new_local_max.append(local_max[i])

    return new_local_min, new_local_max


def calculate_area_diff(price, window, index):
    diff_sum = 0
    for i in range(max(0, index-2 * window), min(len(price)-1, index+2*window)):
        diff_sum += abs(price[i] - price[index])
    return abs(diff_sum/(2*window))


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


def get_local_extermums_asymetric(data, window_left, window_right, mode):

    open, high, low, close = get_ohlc(data)

    bottom_candle, top_candle = get_bottom_top(data)

    top_candle = np.array(top_candle)
    bottom_candle = np.array(bottom_candle)

    price_up = high
    price_down = low
    if mode == 2:
        price_up = top_candle
        price_down = bottom_candle

    local_min = [0] * len(data)
    local_max = [0] * len(data)

    right_window = max(window_right, 0)
    for i in range(window_left, len(open) - right_window):
        if price_up[i] > price_up[i - window_left:i].max() and price_up[i] >= price_up[i:i + right_window+1].max():
            local_max[i] = i
        if price_down[i] < price_down[i - window_left:i].min() and price_down[i] <= price_down[i:i + right_window+1].min():
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


def remove_continuous_extremum(local_min, local_max):
    i, j = 0, 0
    flag = 0
    new_local_min, new_local_max = [], []
    while True:
        if j != len(local_min) and (i == len(local_max) or local_min[j] < local_max[i]):
            if flag != 1:
                new_local_min.append(local_min[j])
            flag = 1
            j += 1
        else:
            if i == len(local_max):
                break
            if flag != -1:
                new_local_max.append(local_max[i])
            flag = -1
            i += 1
    return new_local_min, new_local_max


def get_last_local_extermum(data, window):
    localMin, localMax = get_local_extermums(data, window, 1)
    return localMin[-1], localMax[-1]


def get_local_extremum_area(data, local_min, local_max, time_range, price_range):
    local_max_area = []
    for i in range(len(local_max)):
        for j in range(max(0, local_max[i] - time_range), min(local_max[i] + time_range, len(data))):
            if data[local_max[i]]['High'] - data[j]['High'] < price_range:
                local_max_area.append(j)
    local_max_area.sort()
    local_max_area = list(dict.fromkeys(local_max_area))        # Remove Duplicates
    local_min_area = []
    for i in range(len(local_min)):
        for j in range(max(0, local_min[i] - time_range), min(local_min[i] + time_range, len(data))):
            if data[j]['Low'] - data[local_min[i]]['Low'] < price_range:
                local_min_area.append(j)
    local_min_area.sort()
    local_min_area = list(dict.fromkeys(local_min_area))        # Remove Duplicates
    return local_min_area, local_max_area


def update_local_extremum(local_extremum):
    if len(local_extremum) != 0:
        while len(local_extremum) != 0 and local_extremum[0] <= 0:
            local_extremum = local_extremum[1:]
        for i in range(len(local_extremum)):
            local_extremum[i] -= 1
    else:
        print("Warning : Extremum List Is Empty")
    return local_extremum


def update_new_local_extremum(pre_local_extremum, new_local_extremum, total_window, local_window):
    for i in range(len(new_local_extremum)):
        new_local = new_local_extremum[i] + (total_window - local_window)
        if not new_local in pre_local_extremum:
            pre_local_extremum = np.append(pre_local_extremum, [new_local])
    return pre_local_extremum


def update_local_extremum_list(data_window, local_min, local_max, extremum_window, extremum_mode):
    local_min = update_local_extremum(local_min)
    local_max = update_local_extremum(local_max)

    window_size = extremum_window*4
    new_local_min, new_local_max = get_local_extermums(data_window[-window_size:], extremum_window, extremum_mode)

    local_min = update_new_local_extremum(local_min, new_local_min, len(data_window), window_size)
    local_max = update_new_local_extremum(local_max, new_local_max, len(data_window), window_size)
    return local_min, local_max


def find_next_extremum(extremums, index):
    start, end = 0, len(extremums)-1
    while start < end-1:
        middle = (start + end) // 2
        if extremums[middle] < index:
            start = middle
        else:
            end = middle
    return end