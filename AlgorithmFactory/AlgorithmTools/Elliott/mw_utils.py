import pandas as pd
import numpy as np
import copy
from AlgorithmFactory.AlgorithmTools.Elliott.utility import intersection

fib_ratio = 0.618033989
fib_ratio_precision = fib_ratio * 0.05

STATES_NUM = 3

_ew_region_rules = None

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


def compare_ratio_waves(pd1, pd2, ratio=fib_ratio, lesser=False, ordered=False):
    """Returns True if the value of pd1 and pd2 are compared by the ratio, where pd is price or duration"""
    flag = False
    if ordered:
        first = pd1
        second = pd2
    else:
        first = min(pd1, pd2)
        second = max(pd1, pd2)
    ratio_precision = ratio * 0.05
    if (second != 0):
        if lesser:
            flag = (first / second) <= (ratio + ratio_precision)
        else:
            flag = (ratio - ratio_precision) <= (first / second)
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
    return (p1 * W2.Duration) / ((W2.Price_range+0.01) * d1)


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



"""
Args:
    df_nodes1 <DataFrame>: candles in timeframe which has the big legs
    df_nodes2 <DataFrame>: candles in timeframe which has the smaller legs
    mw1_handler <DataFrame>: monowaves which have the big legs
    mw2_handler <DataFrame>: monowaves which have the smaller legs
    labels <List<str>>: the labels to be checked
    timestamp_tolerance <int>: checks this many of seconds before and after the candles (start and end) for smaller legs
    candle_tolerance <int>: checks this many of candles before and after the candles (start and end) for smaller legs
    
Returns:
    list: has tuples containing candles and monowaves that satisfy conditions
    list :
        As long as len(mw1_handler). Each element corresponds to one label in `labels`.
        Boolean values if the leg in mw1_handler satisfies the conditions corresponding to the label.
    
#TODO:
    label should become a list of labels and the return value would change accordingly
"""
def matching_monowaves(df_nodes1, df_nodes2, mw1_handler, mw2_handler, labels:list = [':F3',], timestamp_tolerance=1000,
                       candle_tolerance=None, label_validity_threshold=0.0):
    from ast import literal_eval
    if timestamp_tolerance is not None and candle_tolerance is not None:
        print(f"Switching to candle_tolerance (={candle_tolerance})")
        timestamp_tolerance = None

    _df_nodes1 = df_nodes1
    _df_nodes2 = df_nodes2

    if not _df_nodes1.index.dtype in (np.int64, np.uint64, int):
        _df_nodes1 = _df_nodes1.reset_index()
    if not _df_nodes2.index.dtype in (np.int64, np.uint64, int):
        _df_nodes2 = _df_nodes2.reset_index()

    if timestamp_tolerance is not None:
        _df_nodes1['timestamp_Time'] = _df_nodes1.apply(lambda x: pd.Timestamp(x['Time'], ).timestamp(), axis=1)
        _df_nodes2['timestamp_Time'] = _df_nodes2.apply(lambda x: pd.Timestamp(x['Time'], ).timestamp(), axis=1)

    results = []
    indices = []
    for i in range(len(mw1_handler)):
        mw = mw1_handler.iloc[i]
        if isinstance(mw.Structure_list_label, str):
            structure_list_label = set(literal_eval(mw.Structure_list_label))
        else:
            structure_list_label= mw.Structure_list_label
        cond1 = None
        cond2 = None

        candidates = []
        for label in labels:
            candidates.append(0.0)
            if label in structure_list_label:
                candles1 = _df_nodes1.iloc[mw.Start_candle_index:mw.End_candle_index]

                if cond1 is None or cond2 is None:
                    if timestamp_tolerance is not None:
                        cond1 = _df_nodes2['timestamp_Time'] >= (candles1.iloc[0]['timestamp_Time'] - timestamp_tolerance)
                        cond2 = _df_nodes2['timestamp_Time'] <= (_df_nodes1.iloc[candles1.index.values[-1] + 1][
                                                                       'timestamp_Time'] - 10 + timestamp_tolerance)
                    else:
                        cond1 = _df_nodes2.index.values >= (candles1.index.values[0] - candle_tolerance)
                        cond2 = _df_nodes2.index.values <= (candles1.index.values[-1] + candle_tolerance)

                candles2 = _df_nodes2[(cond2) & (cond1)]
                if candles2.empty or candles1.empty:
                    continue
                cond3 = mw2_handler['Start_candle_index'] > (candles2.index.values[0] - 1)
                cond4 = mw2_handler['End_candle_index'] < (candles2.index.values[-1] + 1)
                mw2_result = mw2_handler.loc[(cond3) & (cond4)]

                if not mw2_result.empty:
                    validity = matching_conditions.get(label)(mw, mw2_result)
                    if validity > label_validity_threshold:

                        candidates[-1] = validity

                        results.append(
                            (candles1, candles2,
                            mw.to_frame().transpose() if len(mw.shape) == 1 else mw,
                            mw2_result.to_frame().transpose() if len(mw2_result.shape) == 1 else mw2_result,
                            label, validity)
                        )

        indices.append(candidates)
    # todo: should get rid of `results` in production. it is just for the sake of making things easier
    return results, indices

# def F3(mw1, mw2):
#     return mw2.shape[0] == 3# or mw2.shape[0] == 4
#
# def L5(mw1, mw2):
#     return mw2.shape[0] == 4
#
# def L3(mw1, mw2):
#     return mw2.shape[0] == 3
#
# def five(mw1, mw2):
#     return mw2.shape[0] == 5
#
# def S5(mw1, mw2):
#     return mw2.shape[0] == 5

matching_conditions = {
    '(:F3)': lambda mw1, mw2: max(0.0, 1 - ((mw2.shape[0]-3)/STATES_NUM)) if mw2.shape[0] >= 3 else 0.0,
    '(:L5)': lambda mw1, mw2: max(0.0, 1 - ((mw2.shape[0]-5)/STATES_NUM)) if mw2.shape[0] >= 5 else 0.0,
    '(:5)' : lambda mw1, mw2: max(0.0, 1 - ((mw2.shape[0]-5)/STATES_NUM)) if mw2.shape[0] >= 5 else 0.0,
    '(:L3)': lambda mw1, mw2: max(0.0, 1 - ((mw2.shape[0]-3)/STATES_NUM)) if mw2.shape[0] >= 3 else 0.0,
    '(:s5)': lambda mw1, mw2: max(0.0, 1 - ((mw2.shape[0]-5)/STATES_NUM)) if mw2.shape[0] >= 5 else 0.0,
    '[:F3]': lambda mw1, mw2: max(0.0, 1 - ((mw2.shape[0]-3)/STATES_NUM)) if mw2.shape[0] >= 3 else 0.0,
    '[:L5]': lambda mw1, mw2: max(0.0, 1 - ((mw2.shape[0]-5)/STATES_NUM)) if mw2.shape[0] >= 5 else 0.0,
    '[:5]' : lambda mw1, mw2: max(0.0, 1 - ((mw2.shape[0]-5)/STATES_NUM)) if mw2.shape[0] >= 5 else 0.0,
    '[:L3]': lambda mw1, mw2: max(0.0, 1 - ((mw2.shape[0]-3)/STATES_NUM)) if mw2.shape[0] >= 3 else 0.0,
    '[:s5]': lambda mw1, mw2: max(0.0, 1 - ((mw2.shape[0]-5)/STATES_NUM)) if mw2.shape[0] >= 5 else 0.0,

    ':F3'  : lambda mw1, mw2: max(0.0, 1 - ((mw2.shape[0]-3)/STATES_NUM)) if mw2.shape[0] >= 3 else 0.0,
    ':L3'  : lambda mw1, mw2: max(0.0, 1 - ((mw2.shape[0]-3)/STATES_NUM)) if mw2.shape[0] >= 3 else 0.0,
    ':L5'  : lambda mw1, mw2: max(0.0, 1 - ((mw2.shape[0]-5)/STATES_NUM)) if mw2.shape[0] >= 5 else 0.0,
    ':s5'  : lambda mw1, mw2: max(0.0, 1 - ((mw2.shape[0]-5)/STATES_NUM)) if mw2.shape[0] >= 5 else 0.0,
    ':5'   : lambda mw1, mw2: max(0.0, 1 - ((mw2.shape[0]-5)/STATES_NUM)) if mw2.shape[0] >= 5 else 0.0,

    # ':L5': lambda mw1, mw2: mw2.shape[0] == 5,
    # ':5' : lambda mw1, mw2: mw2.shape[0] == 5,
    # ':L3': lambda mw1, mw2: mw2.shape[0] == 3,
    # ':s5': lambda mw1, mw2: mw2.shape[0] == 5,
}


def chart_monowaves(data, match_list, chart_tool,):
    # print(f"check_lower_neo\t\t{len(self.monowave_list)}\t\t{i}")
    print(f"Match List:\t\t{len(match_list)}\n")
    # The Darker, more prominent Blueviolet > Fuschia > plum
    ranges = [(0.3, 0.4, '221,160,221'), (0.6, 0.7, '255,0,255'), (0.9, 1.1, '138,43,226')]
    for spectrums in ranges:

        candidates = [idx for idx in range(len(match_list)) if
                      match_list[idx][5] >= spectrums[0] and match_list[idx][5] <= spectrums[1]]
        color = spectrums[2]
        width = 4
        # for il in range(len(match_list)):
        for il in candidates:
            names = []
            start_times = []
            end_times = []
            start_prices = []
            end_prices = []

            for idx, item in match_list[il][3].iterrows():
                names.append(f"lower_neo_leg_{il}_{idx}")
                # names = [f"lower_neo_leg_{il}_{idx}" for idx, item in match_list[il][3].iterrows()]
                start_times.append(data[item['Start_candle_index']]['Time'])
                end_times.append(data[item['End_candle_index']]['Time'])
                start_prices.append(item['Start_price'])
                end_prices.append(item['End_price'])
                # start_times = [item['Start_time'] for idx, item in match_list[il][3].iterrows()]

                # end_times = [item['End_time'] for idx, item in match_list[il][3].iterrows()]
                # start_prices = [item['Start_price'] for idx, item in match_list[il][3].iterrows()]
                # end_prices = [item['End_price'] for idx, item in match_list[il][3].iterrows()]

            chart_tool.trend_line(names, start_times, start_prices, end_times, end_prices, color=color,
                                       width=width, style=chart_tool.EnumStyle.DashDotDot)


def balance_similarity(M0, M1, M2, M3=None, M4=None, small_middle=False, lesser=False):
    _lesser = lesser
    # _ratio = 1/3
    _ratio = 2 / 5
    _ordered = small_middle
    if M3 is None and M4 is None:
        return (
            (
                compare_ratio_waves(M1.Price_range, M0.Price_range, _ratio, _lesser, _ordered) #or
                # compare_ratio_waves(M0.Duration, M1.Duration, _ratio, _lesser,)
            ) and (
                compare_ratio_waves(M1.Price_range, M2.Price_range, _ratio, _lesser, _ordered) #or
                # compare_ratio_waves(M1.Duration, M2.Duration, _ratio, _lesser,)
            )
        )


def get_ew_region_rules_list(monowaves, condition_hashing_index):
    global _ew_region_rules
    if _ew_region_rules is not None: return _ew_region_rules[condition_hashing_index]
    # _not_implemented = lambda hmw, idx: print(f"Not Implemented")
    _not_implemented = None
    # Why 80? according to our naive hash calculation, the hash value doesn't exceed this number (if it did, \
    # recalculate it or something
    _ew_region_rules = [_not_implemented for i in range(80)]
    # Num Retracement Rule: 1
    _ew_region_rules[1 * 10 + (ord('a') - ord('a'))] = lambda hmw, index: monowaves.EW_R1a(hmw, index)
    _ew_region_rules[1 * 10 + (ord('b') - ord('a'))] = lambda hmw, index: monowaves.EW_R1b(hmw, index)
    _ew_region_rules[1 * 10 + (ord('c') - ord('a'))] = lambda hmw, index: monowaves.EW_R1c(hmw, index)
    _ew_region_rules[1 * 10 + (ord('d') - ord('a'))] = lambda hmw, index: monowaves.EW_R1d(hmw, index)
    # Num Retracement Rule: 2
    _ew_region_rules[2 * 10 + (ord('a') - ord('a'))] = lambda hmw, index: monowaves.EW_R2a(hmw, index)
    _ew_region_rules[2 * 10 + (ord('b') - ord('a'))] = lambda hmw, index: monowaves.EW_R2b(hmw, index)
    _ew_region_rules[2 * 10 + (ord('c') - ord('a'))] = lambda hmw, index: monowaves.EW_R2c(hmw, index)
    _ew_region_rules[2 * 10 + (ord('d') - ord('a'))] = lambda hmw, index: monowaves.EW_R2d(hmw, index)
    _ew_region_rules[2 * 10 + (ord('e') - ord('a'))] = lambda hmw, index: monowaves.EW_R2e(hmw, index)
    # Num Retracement Rule: 3
    _ew_region_rules[3 * 10 + (ord('a') - ord('a'))] = lambda hmw, index: monowaves.EW_R3a(hmw, index)
    _ew_region_rules[3 * 10 + (ord('b') - ord('a'))] = lambda hmw, index: monowaves.EW_R3b(hmw, index)
    _ew_region_rules[3 * 10 + (ord('c') - ord('a'))] = lambda hmw, index: monowaves.EW_R3c(hmw, index)
    _ew_region_rules[3 * 10 + (ord('d') - ord('a'))] = lambda hmw, index: monowaves.EW_R3d(hmw, index)
    _ew_region_rules[3 * 10 + (ord('e') - ord('a'))] = lambda hmw, index: monowaves.EW_R3e(hmw, index)
    _ew_region_rules[3 * 10 + (ord('f') - ord('a'))] = lambda hmw, index: monowaves.EW_R3f(hmw, index)
    # Num Retracement Rule: 4
    _ew_region_rules[4 * 10 + (ord('a') - ord('a'))] = lambda hmw, index: monowaves.EW_R4a(hmw, index)
    _ew_region_rules[4 * 10 + (ord('b') - ord('a'))] = lambda hmw, index: monowaves.EW_R4b(hmw, index)
    _ew_region_rules[4 * 10 + (ord('c') - ord('a'))] = lambda hmw, index: monowaves.EW_R4c(hmw, index)
    _ew_region_rules[4 * 10 + (ord('d') - ord('a'))] = lambda hmw, index: monowaves.EW_R4d(hmw, index)
    _ew_region_rules[4 * 10 + (ord('e') - ord('a'))] = lambda hmw, index: monowaves.EW_R4e(hmw, index)
    # Num Retracement Rule: 5
    _ew_region_rules[5 * 10 + (ord('a') - ord('a'))] = lambda hmw, index: monowaves.EW_R5a(hmw, index)
    _ew_region_rules[5 * 10 + (ord('b') - ord('a'))] = lambda hmw, index: monowaves.EW_R5b(hmw, index)
    _ew_region_rules[5 * 10 + (ord('c') - ord('a'))] = lambda hmw, index: monowaves.EW_R5c(hmw, index)
    _ew_region_rules[5 * 10 + (ord('d') - ord('a'))] = lambda hmw, index: monowaves.EW_R5d(hmw, index)
    # Num Retracement Rule: 6
    _ew_region_rules[6 * 10 + (ord('a') - ord('a'))] = lambda hmw, index: monowaves.EW_R6a(hmw, index)
    _ew_region_rules[6 * 10 + (ord('b') - ord('a'))] = lambda hmw, index: monowaves.EW_R6b(hmw, index)
    _ew_region_rules[6 * 10 + (ord('c') - ord('a'))] = lambda hmw, index: monowaves.EW_R6c(hmw, index)
    _ew_region_rules[6 * 10 + (ord('d') - ord('a'))] = lambda hmw, index: monowaves.EW_R6d(hmw, index)
    # Num Retracement Rule: 7
    _ew_region_rules[7 * 10 + (ord('a') - ord('a'))] = lambda hmw, index: monowaves.EW_R7a(hmw, index)
    _ew_region_rules[7 * 10 + (ord('b') - ord('a'))] = lambda hmw, index: monowaves.EW_R7b(hmw, index)
    _ew_region_rules[7 * 10 + (ord('c') - ord('a'))] = lambda hmw, index: monowaves.EW_R7c(hmw, index)
    _ew_region_rules[7 * 10 + (ord('d') - ord('a'))] = lambda hmw, index: monowaves.EW_R7d(hmw, index)

    return _ew_region_rules[condition_hashing_index]
