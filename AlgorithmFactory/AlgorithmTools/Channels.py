
from AlgorithmFactory.AlgorithmTools.LocalExtermums import *
from AlgorithmFactory.AlgorithmTools.CandleTools import *
import numpy as np


def get_channels(data, extremum_start_window, extremum_end_window, extremum_window_step, extremum_mode, check_window, alpha):
    open, high, low, close = get_ohlc(data)
    bottom, top = get_bottom_top(data)

    price_up, price_down = high, low
    if extremum_mode == 2:
        price_up, price_down = bottom, top

    up_channels, down_channels = [], []
    for window in range(extremum_start_window, extremum_end_window, extremum_window_step):
        local_min, local_max = get_local_extermums(data, window, extremum_mode)
        min_pointer, max_pointer = check_window-1, check_window-1
        while min_pointer < len(local_min) and max_pointer < len(local_max):
            up_channel = check_up_channel(price_up, price_down, local_min, local_max, min_pointer, max_pointer, check_window, alpha, window)
            down_channel = check_down_channel(price_up, price_down, local_min, local_max, min_pointer, max_pointer, check_window, alpha, window)
            # Save Channels
            if up_channel is not None:
                up_channels.append(up_channel)
            if down_channel is not None:
                down_channels.append(down_channel)
            # Next
            if local_min[min_pointer] < local_max[max_pointer]:
                min_pointer += 1
            else:
                max_pointer += 1
    return up_channels, down_channels


def check_up_channel(price_up, price_down, local_min, local_max, local_min_pointer, local_max_pointer, check_window, alpha, window):
    if check_ascending(price_up, local_max[local_max_pointer-check_window+1:local_max_pointer+1]):
        if check_ascending(price_down, local_min[local_min_pointer-check_window+1:local_min_pointer+1]):
            up_line, up_slop = get_up_convex_line(price_up, local_max[local_max_pointer-check_window+1:local_max_pointer+1])
            down_line, down_slop = get_down_convex_line(price_down, local_min[local_min_pointer-check_window+1:local_min_pointer+1])
            if down_line is 0 or up_line is 0:
                return None
            if abs((up_slop - down_slop)/(up_slop + down_slop)) < alpha:
                return {'UpLine': up_line, 'DownLine': down_line, 'Window': window}
    return None


def check_down_channel(price_up, price_down, local_min, local_max, local_min_pointer, local_max_pointer, check_window, alpha, window):
    if check_descending(price_up, local_max[local_max_pointer-check_window+1:local_max_pointer+1]):
        if check_descending(price_down, local_min[local_min_pointer-check_window+1:local_min_pointer+1]):
            up_line, up_slop = get_up_convex_line(price_up, local_max[local_max_pointer-check_window+1:local_max_pointer+1])
            down_line, down_slop = get_down_convex_line(price_down, local_min[local_min_pointer-check_window+1:local_min_pointer+1])
            if down_line is 0 or up_line is 0:
                return None
            if abs((up_slop - down_slop)/(up_slop + down_slop)) < alpha:
                return {'UpLine': up_line, 'DownLine': down_line, 'Window': window}
    return None


def check_ascending(price, indexes):
    for i in range(len(indexes)-1):
        if price[indexes[i]] > price[indexes[i+1]]:
            return False
    return True


def check_descending(price, indexes):
    for i in range(len(indexes)-1):
        if price[indexes[i]] < price[indexes[i+1]]:
            return False
    return True


def get_up_convex_line(price, indexes):
    for i in range(len(indexes)-2, -1, -1):
        line = np.polyfit([indexes[i], indexes[-1]], [price[indexes[i]], price[indexes[-1]]], 1)
        is_convex = True
        for j in range(len(indexes)-1):
            index = indexes[j]
            if price[index] > np.polyval(line, index) and i != j:
                is_convex = False
        if is_convex:
            return {'x': [indexes[i], indexes[-1]], 'y': [price[indexes[i]], price[indexes[-1]]], 'line': line}, line[0]
    return 0, 0


def get_down_convex_line(price, indexes):
    for i in range(len(indexes) - 2, -1, -1):
        line = np.polyfit([indexes[i], indexes[-1]], [price[indexes[i]], price[indexes[-1]]], 1)
        is_convex = True
        for j in range(len(indexes) - 1):
            index = indexes[j]
            if price[index] < np.polyval(line, index) and i != j:
                is_convex = False
        if is_convex:
            return {'x': [indexes[i], indexes[-1]], 'y': [price[indexes[i]], price[indexes[-1]]], 'line': line}, line[0]
    return 0, 0

