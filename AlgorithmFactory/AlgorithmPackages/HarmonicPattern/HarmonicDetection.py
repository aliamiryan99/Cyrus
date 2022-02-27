import numpy as np

from AlgorithmFactory.AlgorithmTools.LocalExtermums import *
import math
from tqdm import tqdm
import matplotlib.pyplot as plt


# find Harmonic Patterns function
def harmonic_pattern(high, low, middle, local_min, local_min_price, local_max, local_max_price, harmonic_name,
                     trend_direction, is_visual, alpha, beta,
                     fibo_tolerance):
    # define Fib Ratios
    # f_r_norm = np.array([.382, .50, .618, .786, 1, 1.272, 1.618])  # Most Important FibRatio
    # fib_tolerance = 0.01
    # f_r_norm_lower = f_r_norm * (1 - fib_tolerance)
    # f_r_norm_upper = f_r_norm * (1 + fib_tolerance)
    # f_b_table = np.array([f_r_norm_lower, f_r_norm, f_r_norm_upper])
    # f_ri_norm = [.236 2.618 4.236] # uncommon fib Ratio


    x_b_ratio, a_c_ratio, b_d_ratio, x_d_ratio = 0, 0, 0, 0
    if harmonic_name == 'Gartley':
        x_b_ratio = [.618]
        a_c_ratio = [0.382, 0.886]
        b_d_ratio = [1.13, 1.618]
        x_d_ratio = [0.786]
    elif harmonic_name == 'Butterfly':
        x_b_ratio = [.786]
        a_c_ratio = [0.382, 0.886]
        b_d_ratio = [1.618, 2.618]
        x_d_ratio = [1.27, 1.618]
    elif harmonic_name == 'Bat':
        x_b_ratio = [0.382, 0.500]
        a_c_ratio = [0.382, 0.886]
        b_d_ratio = [1.618, 2.618]
        x_d_ratio = [0.886]
    elif harmonic_name == 'Crab':
        x_b_ratio = [0.382, 0.618]
        a_c_ratio = [0.382, 0.886]
        b_d_ratio = [2.240, 3.618]
        x_d_ratio = [1.618]
    elif harmonic_name == 'Shark':
        x_b_ratio = [0.000, 10.00]
        a_c_ratio = [1.130, 1.618]
        b_d_ratio = [1.618, 2.240]
        x_d_ratio = [0.886, 1.130]
    elif harmonic_name == 'Cypher':
        x_b_ratio = [0.382, 0.618]
        a_c_ratio = [1.272, 1.414]
        b_d_ratio = [0.000, 10.00]
        x_d_ratio = [0.786]
    elif harmonic_name == 'FiveZero':
        x_b_ratio = [1.130, 1.618]
        a_c_ratio = [1.618, 2.240]
        b_d_ratio = [0.500]
        x_d_ratio = [0.000, 10.00]
    elif harmonic_name == 'ThreeDrives':
        # % x_b_ratio = [1.130,  1.618]
        # % a_c_ratio = [1.618,  2.240]
        # % b_d_ratio = [1.272]
        # % x_d_ratio = [0.000,  10.00]
        x_b_ratio = [1.272]
        a_c_ratio = [0.618]
        b_d_ratio = [1.272]
        x_d_ratio = [0.000, 10.00]
    elif harmonic_name == 'ABCD':
        x_b_ratio = [0.618, 0.786]
        a_c_ratio = [1.272, 1.618]
        b_d_ratio = [0.000, 10.00]
        x_d_ratio = [0.000, 10.00]

    elif harmonic_name == 'ExpandingFlag':
        x_b_ratio = [1.272, 1.618]
        a_c_ratio = [1.618]
        b_d_ratio = [1.618, 2, 2.240, 2.618, 3.618, 4, 4.618]
        x_d_ratio = [2, 2.618, 3, 3.618, 4, 4.618]

    elif harmonic_name == 'Wedge':
        x_b_ratio = [0.786, 0.886]
        a_c_ratio = [0.618, 0.707]
        b_d_ratio = [0.382, 0.50, 0.618, 0.707, 0.786, ]
        x_d_ratio = [0.382, 0.50, 0.618, 0.707, 0.786, 0.886]
    elif harmonic_name == 'Inverse':
        alpha = 1
        x_b_ratio = [alpha]
        a_c_ratio = [1 / alpha]
        b_d_ratio = [alpha]
        x_d_ratio = [0.000, 10.00]

    valid_fibbo_num = np.array(
        [0.382, 0.50, 0.618, 0.707, 0.786, 0.886, 1, 1.272, 1.130, 1.382, 1.618, 2, 2.618, 3.618])

    results = harmonic_patterns_detector(high, low, middle, local_min, local_min_price, local_max, local_max_price,
                                         harmonic_name, trend_direction,
                                         x_b_ratio, a_c_ratio, b_d_ratio, x_d_ratio, valid_fibbo_num, is_visual, alpha,
                                         beta, fibo_tolerance)

    return results


def harmonic_patterns_detector(high, low, middle, local_min, local_min_price, local_max, local_max_price,
                               harmonic_name, trend_direction, x_b_ratio_target, a_c_ratio_target, b_d_ratio_target,
                               x_d_ratio_target, valid_fibbo_num, is_visual, alpha, beta, fibo_tolerance):
    res = []
    tp_sl_val = []
    is_d_point_based_on_extremum = True
    ac2bd_tr = .15  # threshold of ac wings to bd based on Time and candle num
    xb2bd_tr = ac2bd_tr
    xb2ac_tr = ac2bd_tr

    # in case of Bearish Patterns Just change the High / Low
    direction = [1, -1, 1, -1]

    # change the shift of high low value based on the local extremum of the elliott waves
    # for i in range(0, len(local_max)):
    #     for j in range(0, 50):
    #         idx1 = min([local_max[i] + j, len(high)-1])
    #         idx2 = max([local_max[i] - j, 0])
    #         if high[idx1] == local_max_price[i]:
    #             local_max[i] = idx1
    #             break
    #         elif high[idx2] == local_max_price[i]:
    #             local_max[i] = idx2
    #             break
    #
    # for i in range(0, len(local_min)):
    #     for j in range(0, 50):
    #         idx1 = min([local_min[i] + j, len(low)-1])
    #         idx2 = max([local_min[i] - j, 0])
    #         if low[idx1] == local_min_price[i]:
    #             local_min[i] = idx1
    #             break
    #         elif low[idx2] == local_min_price[i]:
    #             local_min[i] = idx2
    #             break

    # high[np.array(local_max)] = local_max_price
    # low[np.array(local_min)] = local_min_price

    middle = (low + high) / 2  # build

    if trend_direction == 'Bearish':
        high, low = low, high
        local_min, local_max = local_max, local_min

        direction = direction[::-1]  # reverse the variable from rnd to front

    if harmonic_name == 'ExpandingFlag':
        max_candle_diff = 550
    else:
        max_candle_diff = 550
    min_candle_diff = 1

    # fibonacci number Tolerance
    if harmonic_name == 'Inverse':
        tol = 0.035  # default 0.003
    else:
        # tol = 0.005
        tol = fibo_tolerance

    reg_tol = 0.15  # regression Line Tolerance

    # ----  add tolerance to the boundary of fibonacci ratio
    if len(x_b_ratio_target) != 1:
        x_b_ratio_target[0] = x_b_ratio_target[0] * (1 - tol)
        x_b_ratio_target[1] = x_b_ratio_target[1] * (1 + tol)
    else:
        x_b_ratio_target = [x_b_ratio_target[0] * (1 - tol), x_b_ratio_target[0] * (1 + tol)]

    if len(a_c_ratio_target) != 1:
        a_c_ratio_target[0] = a_c_ratio_target[0] * (1 - tol)
        a_c_ratio_target[1] = a_c_ratio_target[1] * (1 + tol)
    else:
        a_c_ratio_target = [a_c_ratio_target[0] * (1 - tol), a_c_ratio_target[0] * (1 + tol)]

    if len(b_d_ratio_target) != 1:
        b_d_ratio_target[0] = b_d_ratio_target[0] * (1 - tol)
        b_d_ratio_target[1] = b_d_ratio_target[1] * (1 + tol)
    else:
        b_d_ratio_target = [b_d_ratio_target[0] * (1 - tol), b_d_ratio_target[0] * (1 + tol)]

    if len(x_d_ratio_target) != 1:
        x_d_ratio_target[0] = x_d_ratio_target[0] * (1 - tol)
        x_d_ratio_target[1] = x_d_ratio_target[1] * (1 + tol)
    else:
        x_d_ratio_target = [x_d_ratio_target[0] * (1 - tol), x_d_ratio_target[0] * (1 + tol)]

    # find complete pattern with X A B C D
    # bearish patterns
    if is_visual:
        p_bar = tqdm(total=len(local_min))

    tmp_a, tmp_b, tmp_c, tmp_d = 0, 0, 0, 0
    #  ---- ||  X point
    for i in range(len(local_min)):
        x = low[local_min[i]]
        if is_visual:
            p_bar.update(1)
        # find for A point
        while local_max[tmp_a] <= local_min[i]:
            tmp_a += 1
            if tmp_a >= len(local_max):
                break
        if tmp_a >= len(local_max):
            break
        tmp_b = i
        for j in range(tmp_a, len(local_max)):

            # find for the B point
            while local_min[tmp_b] <= local_max[j]:
                tmp_b += 1
                if tmp_b >= len(local_min):
                    break
            if tmp_b >= len(local_min):
                break
            tmp_c = j

            # check for the range of the waves
            a = high[local_max[j]]

            # Check regression Boundary of X and A
            # print('leg XA')
            rng = [local_min[i], local_max[j]]
            if (direction[0] == 1 and x > a) or (direction[0] == -1 and a > x) or (
                    rng[-1] - rng[0] < min_candle_diff) or (rng[-1] - rng[0] > max_candle_diff):
                continue
            is_regression_cond = check_in_bound_price(middle, low, high, direction[0], harmonic_name, alpha, beta,
                                                      np.arange(rng[0], rng[-1] + 1), local_min, local_max,trend_direction)

            if is_regression_cond and rng[1] - rng[0] > min_candle_diff:
                for k in range(tmp_b, len(local_min)):
                    # range of AB leg
                    rng = [local_max[j], local_min[k]]

                    b = low[local_min[k]]
                    if (direction[1] == 1 and a > b) or (direction[1] == -1 and b > a):
                        continue

                    # make XB leg ratio
                    xa = a - x
                    ab = a - b

                    x_b_ratio = ab / xa
                    if local_min[k] - local_max[j] > min_candle_diff:
                        cond_len_ab = True
                    else:
                        cond_len_ab = False
                    # print(cond_len_ab)
                    # check the XB wave ratio
                    if ((x_b_ratio_target[0] <= x_b_ratio) and (x_b_ratio_target[-1] >= x_b_ratio)) and \
                            (rng[1] - rng[0] > min_candle_diff) and cond_len_ab:
                        # check the XB ratio be the similar the target fibonacci number
                        if not check_fibo_ratio(valid_fibbo_num, x_b_ratio, tol):
                            continue

                        # check price channel of AB leg
                        # print('leg AB')
                        is_regression_cond = check_in_bound_price(middle, low, high, direction[1], harmonic_name, alpha,
                                                                  beta,
                                                                  np.arange(rng[0], rng[-1] + 1), local_min, local_max,trend_direction)

                        # is_regression_cond = True
                        if not is_regression_cond:
                            continue

                        # ---- || find for the C point
                        while local_max[tmp_c] <= local_min[k]:
                            tmp_c += 1
                            if tmp_c >= len(local_max):
                                break
                        if tmp_c >= len(local_max):
                            break
                        tmp_d = k

                        for p in range(tmp_c, len(local_max)):

                            # check for the range of the Leg
                            if local_max[p] - local_min[i] > max_candle_diff:
                                break

                            # range of BC leg
                            rng = [local_min[k], local_max[p]]

                            c = high[local_max[p]]
                            if (direction[2] == 1 and b > c) or (direction[2] == -1 and c > b):
                                continue

                            # make AC wave ratio
                            bc = (c - b)
                            a_c_ratio = bc / ab
                            # check the AC wave ratio
                            if local_max[p] - local_min[k] > min_candle_diff:
                                cond_len_bc = True
                            else:
                                cond_len_bc = False

                            if (a_c_ratio_target[0] <= a_c_ratio) and (a_c_ratio_target[-1] >= a_c_ratio) and \
                                    cond_len_bc:
                                # check the AC ratio be the similar the target fibonacci number
                                if not check_fibo_ratio(valid_fibbo_num, a_c_ratio, tol):
                                    continue

                                # check price channel of BC leg
                                # print('leg BC')
                                is_regression_cond = check_in_bound_price(middle, low, high, direction[2],
                                                                          harmonic_name, alpha, beta,
                                                                          np.arange(rng[0], rng[-1] + 1), local_min,
                                                                          local_max,trend_direction)
                                # is_regression_cond = True
                                if not is_regression_cond:
                                    continue

                                # if it was a AB=CD pattern d point shouldn't be check
                                if harmonic_name == 'ABCD':
                                    b_d_ratio, x_d_ratio, xb2ac, xb2bd, ac2bd = 0, 0, 0, 0, 0
                                    l = local_min[k] + 1
                                    d = b
                                    res.append(
                                        [local_min[i], local_max[j], local_min[k], local_max[p], l, x, a, b, c, d,
                                         x_b_ratio, a_c_ratio, b_d_ratio, x_d_ratio, xb2ac, xb2bd, ac2bd])
                                    continue

                                # there are two kind of localextremums points
                                # first is the common local extreme and the second is that change their values by
                                # elliot waves
                                if is_d_point_based_on_extremum:
                                    local_min_new = local_min
                                else:
                                    local_min_new = list(range(len(high)))
                                while local_min[tmp_d] <= local_max[p]:
                                    tmp_d += 1
                                    if tmp_d >= len(local_min):
                                        break
                                if tmp_d >= len(local_min):
                                    break

                                for l in range(tmp_d, len(local_min_new)):
                                    # check for the range of the waves
                                    if local_min_new[l] - local_min[i] > max_candle_diff:
                                        break

                                    if is_d_point_based_on_extremum:
                                        d = low[local_min_new[l]]
                                    else:
                                        if trend_direction == 'Bearish':
                                            if low[l] > low[l - 1] and low[l] > low[l - 2] and low[l] > low[l - 3] and \
                                                    low[l] > low[l - 4]:
                                                d = low[l]
                                            else:
                                                pass
                                                # continue
                                        elif trend_direction == 'Bullish':
                                            if low[l] < low[l - 1] and low[l] < low[l - 2] and low[l] < low[l - 3] and \
                                                    low[
                                                        l] < low[l - 4]:
                                                d = low[l]
                                            else:
                                                continue

                                    # build BD wave ratio
                                    cd = (c - d)
                                    b_d_ratio = cd / bc

                                    # build BD wave ratio
                                    xd = (d - x)
                                    x_d_ratio = 1 - (xd / xa)

                                    # range od CD leg
                                    rng = [local_max[p], local_min_new[l]]

                                    # check the AC wave ratio
                                    if ((b_d_ratio_target[0] <= b_d_ratio) and
                                        (b_d_ratio_target[-1] >= b_d_ratio)) and \
                                            ((x_d_ratio_target[0] <= x_d_ratio) and
                                             (x_d_ratio_target[-1] >= x_d_ratio)) and \
                                            (rng[1] - rng[0] > min_candle_diff):
                                        # check the XD and BD ratio be the similar the target fibonacci number
                                        if not check_fibo_ratio(valid_fibbo_num, x_d_ratio, tol):
                                            continue
                                        if not check_fibo_ratio(valid_fibbo_num, b_d_ratio, tol):
                                            continue

                                        # check price channel of CD leg
                                        # print('leg CD')
                                        is_regression_cond = check_in_bound_price(middle, low, high, direction[3], \
                                                                                  harmonic_name, alpha, beta, \
                                                                                  np.arange(rng[0], rng[-1] + 1),
                                                                                  local_min_new, local_max,trend_direction)
                                        # is_regression_cond = True
                                        if not is_regression_cond:
                                            continue

                                        # check the d point be a string reversion by breaking high of previous price
                                        look_back = 2
                                        wait_candle = 3

                                        # if trend_direction == "bullish":
                                        #     last_price_condition = True if \
                                        #         np.mean(high[range(local_min_new[l]-look_back,local_min_new[l]+1)])\
                                        #         < np.max(high[range(local_min_new[l],local_min_new[l]+wait_candle)])\
                                        #         else False
                                        #     if not last_price_condition:
                                        #         continue
                                        # else:
                                        #     last_price_condition = True if \
                                        #         np.mean(high[range(local_min_new[l] - look_back, local_min_new[l] + 1)]) \
                                        #         > np.min(high[range(local_min_new[l], local_min_new[l] + wait_candle)]) \
                                        #         else False
                                        #     if not last_price_condition:
                                        #         continue

                                        # if trend_direction == "bullish":
                                        #     last_price_condition = True if \
                                        #         np.mean(high[range(local_min_new[l] - look_back, local_min_new[l])]) \
                                        #         > np.mean(high[range(local_min_new[l] + 1,
                                        #                              min(local_min_new[l] + wait_candle), len(high))]) \
                                        #         else False
                                        #     # if not last_price_condition:
                                        #     #     continue
                                        # else:  # ===> || ------------- injaaaaaa Bayad Dorost beshe  || <===
                                        #     last_price_condition = True if \
                                        #         np.mean(high[range(local_min_new[l] - look_back, local_min_new[l] + 1)]) \
                                        #         > np.mean(high[range(local_min_new[l] + 1,
                                        #                              min(local_min_new[l] + wait_candle, len(high)))]) \
                                        #         else False
                                        # if not last_price_condition:
                                        #     continue

                                        # check the length of wings with times or (candle Numbers)
                                        ac2bd_cond = True
                                        xb2ac_cond = True
                                        xb2bd_cond = True
                                        xb = local_min[k] - local_min[i]
                                        ac = local_max[p] - local_max[j]
                                        bd = local_min_new[l] - local_min[k]
                                        ac2bd = abs(ac - bd) / max([ac, bd])
                                        xb2bd = abs(xb - bd) / max([xb, bd])
                                        xb2ac = abs(xb - ac) / max([xb, ac])
                                        if harmonic_name == 'ABCD' and ac2bd > ac2bd_tr:
                                            ac2bd_cond = False
                                        if harmonic_name == 'ThreeDrives' and xb2bd > 1.5 * xb2bd_tr or xb2ac > 1.5 * xb2ac_tr:
                                            xb2bd_cond = False

                                        if ac2bd_cond and xb2ac_cond and xb2bd_cond:

                                            res.append(
                                                [local_min[i], local_max[j], local_min[k], local_max[p],
                                                 local_min_new[l], x, a, b, c,
                                                 d, x_b_ratio, a_c_ratio, b_d_ratio, x_d_ratio, xb2ac, xb2bd, ac2bd])

                                            # -------> find the Take profit and  <--------
                                            tp_sl = find_tp_sl(x, a, b, c, d, harmonic_name, trend_direction)
                                            res[-1].extend(tp_sl)

                                            # -------> find the Potential reverse zone  <--------
                                            prz = find_PRZ(local_min[i], local_max[j], local_min[k], local_max[p],
                                                 local_min_new[l], harmonic_name, trend_direction,high, low)
                                            res[-1].extend(prz)

    if is_visual:
        p_bar.close()
    if is_visual:
        return res
    else:
        if len(res) > 0:
            return 1
        else:
            return 0

# Build the Take profit and Stop Loss Value
def find_tp_sl(x, a, b, c, d,harmonic_name,trend_direction):
    fibo_ratio = np.array([0.38, 0.62, 0.79, 1, 1.27, 1.382])
    # find TP
    xa = np.abs(a - x)
    if trend_direction == "Bullish":
        tp_level = d + xa*fibo_ratio
        sl_level = d - xa*fibo_ratio

    elif trend_direction =="Bearish":
        tp_level = d - xa * fibo_ratio
        sl_level = d + xa * fibo_ratio

    tp_sl_levels = np.array([*tp_level, *sl_level]).tolist()
    return tp_sl_levels

def find_PRZ(xIdx, aIdx, bIdx, cIdx, dIdx, harmonic_name,trend_direction,top, bottom):
    fibo_ratio = np.array([0.38, 0.62, 0.79, 1, 1.27, 1.382])
    Diff = top[xIdx:dIdx]-bottom[xIdx:dIdx]
    avr_candle = np.mean(Diff)

    # get the height of the prz box
    h = avr_candle

    # get the width of the prz box
    # width
    w = np.round((dIdx - cIdx)/6)

    prz  = np.array([top[dIdx],dIdx, top[dIdx]-h,dIdx+w])

    return prz

# check the Fibonacci ratio
def check_fibo_ratio(ref_fibo, target_fibo, tol):
    fib_tr = [ref_fibo * (1 - tol), ref_fibo, ref_fibo * (1 + tol)]
    condition = (target_fibo > fib_tr[0]) & (target_fibo < fib_tr[2])
    if np.isin(True, condition):
        return True
    else:
        return False


# check the length of a leg
def check_the_leg_length(rng, max_length_tr):
    if rng > max_length_tr:
        return False
    else:
        return True


# check Regression Condition function
def regression_check(middle, rng, reg_tol):
    # cast the number to single precision
    c = middle[rng[0]:rng[1] + 1]

    # ----- regression Line of harmonic pattern
    S = (c[-1] - c[0]) / (rng[-1] - rng[0])  # slope
    I = c[0] - S * rng[0]  # intersect
    p2 = np.array([S, I])

    # -----  regression Line of candles on
    p = regression_fit(rng, c)

    #   comperasion between the Line of Harmonic and candle line
    return np.sum(np.abs(p2 - p) < abs(p * reg_tol)) == len(p)

    # evaluate Slope and intersect with regression


def regression_fit(rng, middle):
    n = rng[1] - rng[0] + 1

    n_floor = math.floor(n / 2)
    numerator = np.sum(((n - 1) / 2 - np.arange(0, n_floor - 1)) * (
            middle[n - np.arange(1, n_floor)] - middle[np.arange(0, n_floor - 1)]))
    denumerator = ((n ** 3) - n) / 12

    # slop of regression
    p1 = (numerator / denumerator)

    # intersect of regression
    p2 = (np.sum(middle) / n) - p1 * ((rng[1] + rng[0]) / 2)
    return np.array([p1, p2])


# -------------------- || check if the price move around the leg || --------------------
# find boundary of the legs
def check_in_bound_price(middle, low, high, direction, harmonic_name, alpha, beta, rng, local_min, local_max,trend):
    local_min = np.array(local_min)
    local_max = np.array(local_max)

    boundary_mode = 'TopBottom_rotation'  # STD_rotation  TopBottom_rotation body_average
    boundary_points = 'EqualityExtremumNumber'  # LocalExtremum  ALLPoints EqualityExtremumNumber

    # ---------- check all of points in the Channel
    if boundary_points == 'ALLPoints':
        lower_bound, upper_bound = find_boundary(boundary_mode, boundary_points, direction, middle, high, low, rng,
                                                 alpha, local_min, local_max)
        high = middle
        low = middle
        # check the satisfaction conditions of boundaries
        situation = np.sum(np.logical_and(lower_bound < low[rng], high[rng] < upper_bound)) >= rng.size * beta

    # ---------- check only extremum of points in the Channel
    elif boundary_points == 'LocalExtremum':
        rng, local_min, local_max
        lower_bound, upper_bound = find_boundary(boundary_mode, boundary_points, direction, middle, high, low, rng,
                                                 alpha, local_min, local_max)
        # high = middle
        # low  = middle
        # check the satisfaction conditions of boundaries
        situation = np.sum(np.logical_and(lower_bound < low[rng], high[rng] < upper_bound)) >= rng.size * beta

    elif boundary_points == 'EqualityExtremumNumber':
        min_idx = local_min[np.array(list(np.where(np.logical_and(local_min >= rng[0], local_min <= rng[-1]))))]
        # min_idx = min_idx[0]
        max_idx = local_max[np.array(list(np.where(np.logical_and(local_max >= rng[0], local_max <= rng[-1]))))]
        # max_idx = max_idx[0]

        if trend == 'Bearish':
            min_idx, max_idx = max_idx, min_idx

        if np.size(max_idx) <= 1 or np.size(min_idx) <= 1:
            local_extremum_proportion = np.inf
            local_extremum_std = np.Inf
            condition_height = True
        else:
            # check the number of extremum to be equal to each others
            eps = 0.00001
            local_extremum_proportion = max(np.size(max_idx) - 1, np.size(min_idx) - 1) / (
                    min(np.size(max_idx) - 1, np.size(min_idx) - 1) + eps)
            local_extremum_std = max(np.std(np.diff(high[max_idx])), np.std(np.diff(low[min_idx]))) / (
                    min(np.std(np.diff(high[max_idx])), np.std(np.diff(low[min_idx]))) + eps)

            omega = 0.05

            if direction == 1:
                leg_height = high[max_idx[0][-1]] - low[min_idx[0][0]]
                leg_time_length = max_idx[0][-1] - min_idx[0][0]
                condition_height = (np.array(low[min_idx[0][0]] - omega * leg_height) <= np.min(low[rng])) and (
                        np.array(high[max_idx[0][-1]] + (omega * leg_height)) >= np.max(high[rng]))
            elif direction == -1:
                leg_height = high[max_idx[0][0]] - low[min_idx[0][-1]]
                leg_time_length = max_idx[0][-1] - min_idx[0][0]
                condition_height = (np.array(low[min_idx[0][-1]] - omega * leg_height) <= np.min(low[rng])) and (
                        np.array(high[max_idx[0][0]] + (omega * leg_height)) >= np.max(high[rng]))




        # if local_extremum_proportion<1.5 and local_extremum_std<1.5:
        #     situation = True
        # else:
        #     situation = False
        if condition_height:
            situation = True
        else:
            situation = False

    if harmonic_name == 'ABCD':
        situation = True

    return situation


def find_boundary(boundary_mode, boundary_points, direction, middle, high, low, x, alpha, local_min,
                  local_max):  # alpha = .50
    # find boundary based on two approach
    # first approach works based on the rotation of line and a percent of the average price of that line
    # second approach define base on the percent of the body average
    is_plot_the_channel = True

    local_min = np.array(local_min)
    local_max = np.array(local_max)
    if boundary_points == 'LocalExtremum':
        min_idx = local_min[np.array(list(np.where(np.logical_and(local_min >= x[0], local_min <= x[-1]))))]
        max_idx = local_max[np.array(list(np.where(np.logical_and(local_max >= x[0], local_max <= x[-1]))))]

    # if direction == 1: # Low2High
    #     p = np.polyfit([x[0], x[-1]], [low[x[0]], high[x[-1]]], 1)
    #
    # else:  #High2Low
    #     p = np.polyfit([x[0], x[-1]], [high[x[0]], low[x[-1]]], 1)

    p = np.polyfit([x[0], x[-1]], [low[x[0]], high[x[-1]]], 1)
    y = np.polyval(p, x)

    if boundary_mode == 'body_average':
        candle_avg = np.mean(high - low)
        deg = (np.pi / 2) - (np.abs(middle[x[-1]] - middle[x[0]]) / (x[-1] - x[0]))
        h = alpha * candle_avg * np.sin(deg)
        upper_bound_hat = y + h
        lower_bound_hat = y - h

    elif boundary_mode == 'STD_rotation':
        # ------------------ find the rotation degree
        slope = np.rad2deg(np.arctan((middle[x[-1]] - middle[x[0]]) / (x[-1] - x[0])))

        # ------------------ rotate line
        x_hat, y_hat_line = rotate_line(x, y, -slope)
        x_hat, y_hat = rotate_line(x, middle[x], -slope)

        # ------------------ find bound of line
        upper_bound = y_hat_line + (1 + alpha) * np.std(y_hat)
        lower_bound = y_hat_line - (1 + alpha) * np.std(y_hat)

        # ------------------ de - rotate boundary lines
        upper_bound_hat_x, upper_bound_hat = rotate_line(x_hat, upper_bound, slope)
        lower_bound_hat_x, lower_bound_hat = rotate_line(x_hat, lower_bound, slope)

        if is_plot_the_channel:
            fig = plt.figure()
            ax = plt.axes()
            fig = plt.figure()
            ax = plt.axes()

            # ----- original points
            shift_val = 15  # shift value between three graph
            rng = np.arange(x[0], x[-1] + 1)
            yText = np.max(middle[rng]) + (np.max(middle[rng]) - np.min(middle[rng])) / 5
            x_original = x - np.min(x) + shift_val
            plt.plot(x_original, y, 'k--', linewidth=1.0)
            plt.scatter(x_original, middle[rng], marker='s', s=8, c='black', alpha=1)
            plt.text(np.min(x_original), yText, "Original Chart", fontsize=8)

            # ----- rotated point
            x_rotated_point = np.max(x_original) - np.min(x_hat) + x_hat + shift_val
            plt.plot(x_rotated_point, upper_bound, 'r:', linewidth=1.0)
            plt.plot(x_rotated_point, lower_bound, 'g:', linewidth=1.0)
            plt.plot(x_rotated_point, y_hat_line, 'k:', linewidth=1.0)
            plt.scatter(x_rotated_point, y_hat, marker='o', s=10, c='blue', alpha=1)
            plt.text(np.min(x_rotated_point), yText, "Rotation Degree:" + str(np.round(slope, 2)) + "\nSTD= 0.9",
                     fontsize=8)

            # ----- de rotated lines
            x_de_rotate = np.max(x_rotated_point) - np.min(upper_bound_hat_x) + upper_bound_hat_x + shift_val
            plt.plot(x_de_rotate, upper_bound_hat, 'r--', linewidth=1.0)
            plt.plot(x_de_rotate, lower_bound_hat, 'g--', linewidth=1.0)
            plt.scatter(x_de_rotate, middle[rng], marker='s', s=8, c='black', alpha=1)
            plt.text(np.min(x_de_rotate), yText, "Boundary on Original chart ", fontsize=8)
            plt.show()

    elif boundary_mode == 'TopBottom_rotation':
        sort_diff = np.sort(np.array(high - low))
        body_width = np.mean(sort_diff[-20:-1])
        beta = 0.3
        X = np.linspace(4, len(x) + 4, len(x) + 4)
        coff = np.log10(X)
        coff -= np.min(coff)
        coff = coff[len(x)]
        # ------------------ find the rotation degree

        slope = np.rad2deg(np.arctan((high[x[-1]] - low[x[0]]) / (x[-1] - x[0])))

        # ------------------ rotate line
        x_hat, y_hat_line = rotate_line(x, y, -slope)
        x_hat, y_hat_high = rotate_line(x, high[x], -slope)
        x_hat, y_hat_low = rotate_line(x, low[x], -slope)

        # ------------------ find bound of line
        upper_bound = y_hat_line + beta * coff * body_width
        lower_bound = y_hat_line - beta * coff * body_width

        # ------------------ de - rotate boundary lines
        upper_bound_hat_x, upper_bound_hat = rotate_line(x_hat, upper_bound, slope)
        lower_bound_hat_x, lower_bound_hat = rotate_line(x_hat, lower_bound, slope)

        # plot the rotation boundary
        if is_plot_the_channel:
            fig = plt.figure()
            ax = plt.axes()
            fig = plt.figure()
            ax = plt.axes()

            # ----- original points
            shift_val = 15  # shift value between three graph
            rng = np.arange(x[0], x[-1] + 1)
            yText = np.max(middle[rng]) + (np.max(middle[rng]) - np.min(middle[rng])) / 5
            x_original = x - np.min(x) + shift_val
            plt.plot(x_original, y, 'k--', linewidth=1.0)
            # plt.scatter(x_original, middle[rng], marker='s', s=8, c='black', alpha=0.5)
            plt.scatter(x_original, high[rng], marker='s', s=8, c='green', alpha=0.1)
            plt.scatter(x_original, low[rng], marker='s', s=8, c='red', alpha=0.1)
            plt.scatter(x_original[(min_idx - np.min(min_idx))], low[min_idx], marker='p', s=40, c='red', alpha=1)
            plt.scatter(x_original[(max_idx - np.min(min_idx))], high[max_idx], marker='p', s=40, c='green', alpha=1)

            plt.text(np.min(x_original), yText, "Original Chart", fontsize=8)

            # ----- rotated point
            x_rotated_point = np.max(x_original) - np.min(x_hat) + x_hat + shift_val
            plt.plot(x_rotated_point, upper_bound, 'r:', linewidth=1.0)
            plt.plot(x_rotated_point, lower_bound, 'g:', linewidth=1.0)
            plt.plot(x_rotated_point, y_hat_line, 'k:', linewidth=1.0)
            plt.scatter(x_rotated_point, y_hat_high, marker='o', s=10, c='green', alpha=0.1)
            plt.scatter(x_rotated_point, y_hat_low, marker='o', s=10, c='red', alpha=0.1)

            plt.scatter(x_rotated_point[(max_idx - np.min(min_idx))], y_hat_high[(max_idx - np.min(min_idx))],
                        marker='p', s=40, c='green', alpha=1)
            plt.scatter(x_rotated_point[(min_idx - np.min(min_idx))], y_hat_low[(min_idx - np.min(min_idx))],
                        marker='p', s=40, c='red', alpha=1)

            plt.text(np.min(x_rotated_point), yText, "Rotation Degree:" + str(np.round(slope, 2)) + \
                     "\nCoefficient= " + str(np.round(coff, 2)) + \
                     "\nCandle Number= " + str(np.round(len(x), 2)) + \
                     "\nCandleBody Width= " + str(np.round(body_width, 2)) + \
                     "\nChannel Width = " + str(np.round(beta * coff * body_width, 2)), fontsize=8)

            # ----- de rotated lines
            x_de_rotate = np.max(x_rotated_point) - np.min(upper_bound_hat_x) + upper_bound_hat_x + shift_val
            plt.plot(x_de_rotate, upper_bound_hat, 'r--', linewidth=1.0)
            plt.plot(x_de_rotate, lower_bound_hat, 'g--', linewidth=1.0)
            plt.scatter(x_de_rotate, middle[rng], marker='s', s=8, c='black', alpha=1)
            plt.text(np.min(x_de_rotate), yText, "Boundary on Original chart ", fontsize=8)
            plt.show()

    return lower_bound_hat, upper_bound_hat


def rotate_line(x, y, deg):  # Vertices matrix
    v = np.array((x, y, np.zeros(y.size))).transpose()
    v_centre = np.mean(v, 0)  # Centre, of line
    vc = v - np.ones((v.shape[0], 1)) * v_centre  # Centering coordinates
    a_rad = ((deg * math.pi) / 180)  # Angle in radians

    e = np.array([0, 0, a_rad])  # Euler angles for X, Y, Z - axis rotations

    # Direction Cosines (rotation matrix) construction
    rx = np.array([[1, 0, 0],
                   [0, np.cos(e[0]), -np.sin(e[0])],
                   [0, np.sin(e[0]), -np.cos(e[0])]])  # X-Axis rotation

    ry = np.array([[np.cos(e[1]), 0, np.sin(e[1])],
                   [0, 1, 0],
                   [-np.sin(e[1]), 0, np.cos(e[1])]])  # Y-axis rotation

    rz = np.array([[np.cos(e[2]), -np.sin(e[2]), 0],
                   [np.sin(e[2]), np.cos(e[2]), 0],
                   [0, 0, 1]])  # Z-axis rotation

    r = rx.dot(ry.dot(rz))  # Rotation matrix
    vrc = (r.dot(vc.transpose())).transpose()  # Rotating centred coordinates
    vr = vrc + np.ones((v.shape[0], 1)) * v_centre  # Shifting back to original location
    x = vr[:, 0]
    y = vr[:, 1]
    return x, y
