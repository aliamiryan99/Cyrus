import pandas as pd
import numpy as np
import copy
from AlgorithmFactory.AlgorithmTools.Elliott import intersection

fib_ratio = 0.618033989
fib_ratio_precision = fib_ratio * 0.05


def waves_are_fib_related(pd1, pd2, fib_r=fib_ratio, order=False):
    """Returns True if the value of pd1 and pd2 are related by fib_ratios, where pd is price or duration"""
    flag = False
    first = pd1
    second = pd2
    if (order == False):
        first = min(pd1, pd2)
        second = max(pd1, pd2)
    if (second != 0):
        flag = (fib_r - fib_ratio_precision) < (first / second) < (fib_r + fib_ratio_precision)
    return flag


def compare_ratio_waves(pd1, pd2, ratio=fib_ratio, lesser=False):
    """Returns True if the value of pd1 and pd2 are compared by the ratio, where pd is price or duration"""
    flag = False
    first = min(pd1, pd2)
    second = max(pd1, pd2)
    ratio_precision = ratio * 0.05
    if (second != 0):
        if (lesser == False):
            flag = (ratio - ratio_precision) <= (first / second)
        else:
            flag = (first / second) <= (ratio + ratio_precision)
    return flag


def wave_overlap(W1, W2):
    """Returns True if the wave1 and wave 2 price range are overlapped """
    max1 = max(W1.Start_price, W1.End_price)
    min1 = min(W1.Start_price, W1.End_price)
    max2 = max(W2.Start_price, W2.End_price)
    min2 = min(W2.Start_price, W2.End_price)
    return max1 >= min2 and max2 >= min1


def wave_end_inside_channel(W1, W2):
    """Returns True if the end of wave 2 is inside of the wave 1's channel (W1 and W2 are in the same direction)"""
    return (W2.End_price - W2.Start_price) * (W2.End_price - W1.Start_price) > 0


def hmw_save(hmw: list, filepath=".\\outputs\\", fname="hmw"):
    """Save HyperMonowaves to CSV file"""
    df_hmw = pd.DataFrame(hmw)
    df_hmw.to_csv(filepath + fname + ".csv", index=False, encoding='utf-8', sep=';')


def wave_beyond(W1, W2):
    """Returns True if the end of wave 2 exceeds the end of wave 1 (W1 and W2 are in the same direction)"""
    return (W2.End_price - W2.Start_price) * (W2.End_price - W1.End_price) > 0


def point_WRT_line(x1, y1, x2, y2, x3, y3):
    """Returns 1,0,-1 depends on the position of point (x3,y3) with respect to the line of (x1,y1)->(x2,y2) : 1 if the point over the line"""
    slope = (y2 - y1) / (x2 - x1)
    intercept = y2 - slope * x2

    y_line = slope * x3 + intercept
    if format(y_line, '.10f') < format(y3, '.10f'):
        return 1
    elif format(y_line, '.10f') > format(y3, '.10f'):
        return -1
    return 0


def beyond_trendline(M1, M2, M3):
    """Returns True if the Max or Min of M3 break the line from end of M1 to the end of M2"""
    x1 = M1.End_candle_index
    y1 = M1.End_price
    x2 = M2.End_candle_index
    y2 = M2.End_price

    if M1.Direction == 1:
        x3 = M3.Max_candle_index
        y3 = M3.Max_price
        return point_WRT_line(x1, y1, x2, y2, x3, y3) > 0  # return true when the point M3.max is over line (M1e, M2e)

    else:
        x3 = M3.Min_candle_index
        y3 = M3.Min_price
        return point_WRT_line(x1, y1, x2, y2, x3, y3) < 0  # return true when the point M3.min is below line (M1e, M2e)


def wave_breaking_trendline_impulse(M2, M4, M5, post_action):
    """Returns True if post_action breaks a trendline drawn across the end of M2 and M4 in a period equal to or less than that taken by M5"""

    x2 = M2.End_candle_index
    y2 = M2.End_price
    x4 = M4.End_candle_index
    y4 = M4.End_price

    x5 = M5.End_candle_index
    y5 = M5.End_price
    x6 = post_action.End_candle_index
    y6 = post_action.End_price

    xr, _ = intersection(x2, y2, x4, y4, x5, y5, x6, y6)
    if xr is None: return False
    progress = np.minimum(x5 - x4, x6 - x5)
    return x5 <= xr <= x5 + progress


def wave_breaking_trendline_flat_zigzag_triangle(Ma, Mc, post_action):
    """Returns True if post_action breaks a trendline drawn across the start of Ma and Mc in a period equal to or less than that taken by Mc"""

    xa = Ma.Start_candle_index
    ya = Ma.Start_price
    xb = Mc.Start_candle_index
    yb = Mc.Start_price

    xc = Mc.End_candle_index
    yc = Mc.End_price
    x = post_action.End_candle_index
    y = post_action.End_price

    xr, _ = intersection(xa, ya, xb, yb, xc, yc, x, y)
    if xr is None: return False
    progress = np.minimum(xc - xb, x - xc)
    return xc <= xr <= xc + progress


def waves_relative_slope(p1, d1, W2):
    """Returns the slop proportion of wave 1(p1, d1) to wave 2(W2)"""
    return (p1 * W2.Duration) / (W2.Price_range * d1)


def wave_is_steeper(p1, d1, W2, retraced_ratio=1):
    """Returns True if wave 1(p1,d1) is steeper and have a larger Price_range (W1 and W2 are in the same direction)"""
    return waves_relative_slope(p1, d1, W2) > 1 and p1 >= (W2.Price_range * retraced_ratio)


def merge(MW_list: list):
    """ merge list of monowaves into one """
    if len(MW_list) == 1:
        return MW_list[0]

    Ms = MW_list[0]
    Me = MW_list[-1]
    res = Ms.copy()
    # assert(Me.Direction == Ms.Direction)
    res.MW_end_index = Me.MW_end_index
    res.End_price = Me.End_price
    res.End_candle_index = Me.End_candle_index

    res.MW_start_index = Ms.MW_start_index
    res.Start_price = Ms.Start_price
    res.Start_candle_index = Ms.Start_candle_index

    res.Price_range = abs(Me.End_price - Ms.Start_price)
    res.Duration = Me.End_candle_index - Ms.Start_candle_index
    res.Direction = Ms.Direction

    res.Num_sub_monowave = sum([M.Num_sub_monowave for M in MW_list])

    res.Min_price = min([M.Min_price for M in MW_list])
    res.Max_price = max([M.Max_price for M in MW_list])

    res.Min_candle_index = MW_list[np.argmin([M.Min_price for M in MW_list])].Min_candle_index
    res.Max_candle_index = MW_list[np.argmax([M.Max_price for M in MW_list])].Max_candle_index
    res.Price_coverage = res.Max_price - res.Min_price

    return res


def compaction(HMW, valid_pairs):
    valid_pairs.sort(key=lambda tup: tup[1])
    HMW_nextLvl = []
    old_index = 0
    HMW2 = copy.deepcopy(HMW)
    for i in range(len(valid_pairs)):
        start_idx = valid_pairs[i][0]
        end_idx = valid_pairs[i][1]

        HMW_nextLvl.extend(HMW2[old_index:start_idx])
        res = merge(HMW2[start_idx:end_idx + 1])
        HMW_nextLvl.append(res)

        old_index = end_idx + 1

    HMW_nextLvl.extend(HMW2[old_index:])

    for i in range(len(HMW_nextLvl)):
        HMW_nextLvl[i].Structure_list_label = []
        HMW_nextLvl[i].EW_structure = []

    return HMW_nextLvl


def count_labels(hmw: list) -> int:
    """Return total number of labels in the list of hmw

    Args:
        hmw (list): list of hypermonowaves

    Returns:
        int: return total number of structural list numbers in all hypermonowaves
    """
    return np.sum([len(m.Structure_list_label) for m in hmw], dtype=int)