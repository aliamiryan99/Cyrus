
from AlgorithmFactory.AlgorithmTools.LocalExtermums import *
from AlgorithmFactory.AlgorithmTools.CandleTools import *
import numpy as np


def get_parallel_channels(data, extremum_start_window, extremum_end_window, extremum_window_step, extremum_mode, check_window, alpha):
    open, high, low, close = get_ohlc(data)
    bottom, top = get_bottom_top(data)

    price_up, price_down = high, low
    if extremum_mode == 2:
        price_up, price_down = bottom, top

    up_channels, down_channels = [], []
    for window in range(extremum_start_window, extremum_end_window+1, extremum_window_step):
        local_min, local_max = get_local_extermums(data, window, extremum_mode)
        min_pointer, max_pointer = check_window-1, check_window-1
        while min_pointer < len(local_min) and max_pointer < len(local_max):
            channel = check_channels(price_up, price_down, local_min, local_max, min_pointer, max_pointer, check_window, alpha, window)
            # Save Channels
            if channel is not None:
                if channel['UpLine']['line'][0] > 0:
                    up_channels.append(channel)
                else:
                    down_channels.append(channel)
            # Next
            if local_min[min_pointer] < local_max[max_pointer]:
                min_pointer += 1
            else:
                max_pointer += 1
    return up_channels, down_channels


def check_channels(price_up, price_down, local_min, local_max, local_min_pointer, local_max_pointer, check_window, alpha, window):
    for max_i in local_max[local_max_pointer-check_window+1:local_max_pointer]:
        up_line = np.polyfit([max_i, local_max[local_max_pointer]], [price_up[max_i], price_up[local_max[local_max_pointer]]], 1)
        for min_i in local_min[local_min_pointer-check_window+1:local_min_pointer]:
            down_line = np.polyfit([min_i, local_min[local_min_pointer]], [price_down[min_i], price_down[local_min[local_min_pointer]]], 1)
            if is_parallel(up_line[0], down_line[0], alpha):
                if betweenness(up_line, down_line, price_up, price_down, min(min_i, max_i), max(local_max[local_max_pointer], local_min[local_min_pointer]) + window):
                    up_line = {'x': [max_i, local_max[local_max_pointer]], 'y': [price_up[max_i], price_up[local_max[local_max_pointer]]], 'line': up_line}
                    down_line = {'x': [min_i, local_min[local_min_pointer]], 'y': [price_down[min_i], price_down[local_min[local_min_pointer]]], 'line': down_line}
                    return {'UpLine': up_line, 'DownLine': down_line, 'Window': window}
    return None


def is_parallel(up_slope, down_slope, alpha):
    return abs((up_slope - down_slope)/(up_slope + down_slope)) < alpha


def betweenness(up_line, down_line, price_up, price_down, start, end):
    for i in range(start, end+1):
        if np.polyval(up_line, i) < price_up[i]:
            return False
        if np.polyval(down_line, i) > price_down[i]:
            return False
    return True
