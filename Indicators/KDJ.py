import pandas as pd
import numpy as np
from Simulation.Utility import *


def kdj(array_high, array_low, array_close, k_periods, d_periods):
    # converting from UNIX timestamp to normal
    y = 0
    # k_periods are 14 array start from 0 index
    array_highest = []
    for x in range(0, array_high.size - k_periods):
        z = array_high[y]
        for j in range(0, k_periods):
            if z < array_high[y + 1]:
                z = array_high[y + 1]
            y = y + 1
        # creating list highest of k periods
        array_highest.append(z)
        y = y - (k_periods - 1)
    y = 0
    array_lowest = []
    for x in range(0, array_low.size - k_periods):
        z = array_low[y]
        for j in range(0, k_periods):
            if z > array_low[y + 1]:
                z = array_low[y + 1]
            y = y + 1
        # creating list lowest of k periods
        array_lowest.append(z)
        y = y - (k_periods - 1)

    # KDJ (K line, D line, J line)
    k_value = []
    for x in range(k_periods, array_close.size):
        k = ((array_close[x] - array_lowest[x - k_periods]) * 100 / (array_highest[x - k_periods] - array_lowest[x - k_periods]))
        k_value.append(k)
    y = 0
    # d_periods for calculate d values
    d_value = [None, None]
    for x in range(0, len(k_value) - d_periods + 1):
        sum = 0
        for j in range(0, d_periods):
            sum = k_value[y] + sum
            y = y + 1
        mean = sum / d_periods
        # d values for %d line
        d_value.append(mean)
        y = y - (d_periods - 1)

    j_value = [None, None]
    for x in range(0, len(d_value) - d_periods + 1):
        j = (d_value[x + 2] * 3) - (k_value[x + 2] * 2)
        # j values for %j line
        j_value.append(j)

    k_value = k_value[2:]
    d_value = d_value[2:]
    j_value = j_value[2:]

    return k_value, d_value, j_value


