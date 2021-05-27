
from AlgorithmTools.LocalExtermums import *
import math
from tqdm import tqdm


# find Harmonic Patterns function
def harmonic_pattern(high, low, middle, local_min, local_max, harmonic_name, trend_direction, is_visual):

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
        b_d_ratio = [1.13,  1.618]
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
        x_b_ratio = [0.000, 10.000]
        a_c_ratio = [0.618, 0.786]
        b_d_ratio = [1.272, 1.618]
        x_d_ratio = [0.000,  10.00]
    elif harmonic_name == 'ExpandingFlag':
        x_b_ratio = [1.272, 1.618]
        a_c_ratio = [2.240]
        b_d_ratio = [1.272]
        x_d_ratio = [0.000, 10.00]
    elif harmonic_name == 'Inverse':
        alpha = 1
        x_b_ratio = [alpha]
        a_c_ratio = [1 / alpha]
        b_d_ratio = [alpha]
        x_d_ratio = [0.000, 10.00]
    results = harmonic_patterns_detector(high, low, middle, local_min, local_max, harmonic_name, trend_direction,
                                         x_b_ratio, a_c_ratio, b_d_ratio, x_d_ratio, is_visual)
    return results


def harmonic_patterns_detector(high, low, middle, local_min, local_max,
                               harmonic_name, trend_direction, x_b_ratio_target, a_c_ratio_target, b_d_ratio_target,
                               x_d_ratio_target, is_visual):

    res = []

    ac2bd_tr = .15  # threshold of ac wings to bd based on Time and candle num
    xb2bd_tr = ac2bd_tr
    xb2ac_tr = ac2bd_tr
    # if we need  to find Bearish Patterns Just change the High / Low
    if trend_direction == 'Bearish':
        high, low = low, high
        local_min, local_max = local_max, local_min

    if harmonic_name == 'ExpandingFlag':
        max_candle_diff = 350
    else:
        max_candle_diff = 150
    min_candle_diff = 3

    # fibonacci number Tolerance
    if harmonic_name == 'Inverse':
        tol = 0.035  # default 0.003
    else:
        tol = 0.005

    reg_tol = 0.15  # regression Line Tolerance

    # ----  build the targets bounds
    if len(x_b_ratio_target) == 1:
        x_b_ratio_target = [x_b_ratio_target[0] * (1 - tol), x_b_ratio_target[0] * (1 + tol)]
    if len(a_c_ratio_target) == 1:
        a_c_ratio_target = [a_c_ratio_target[0] * (1 - tol), a_c_ratio_target[0] * (1 + tol)]
    if len(b_d_ratio_target) == 1:
        b_d_ratio_target = [b_d_ratio_target[0] * (1 - tol), b_d_ratio_target[0] * (1 + tol)]
    if len(x_d_ratio_target) == 1:
        x_d_ratio_target = [x_d_ratio_target[0] * (1 - tol), x_d_ratio_target[0] * (1 + tol)]

    # find complete pattern with X A B C D
    # bearish patterns
    if is_visual:
        p_bar = tqdm(total=len(local_min))
    tmp_a, tmp_b, tmp_c, tmp_d = 0, 0, 0, 0
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

            # check for the range of the waves
            a = high[local_max[j]]

            # Check regression Similarity of X and A
            rng = [local_min[i], local_max[j]]
            is_regression_cond = regression_check(middle, rng, reg_tol)

            # find for the B point
            while local_min[tmp_b] <= local_max[j]:
                tmp_b += 1
                if tmp_b >= len(local_min):
                    break
            if tmp_b >= len(local_min):
                break
            tmp_c = j
            if is_regression_cond and rng[1] - rng[0] > min_candle_diff:
                for k in range(tmp_b, len(local_min)):
                    # check for the range of the waves
                    if local_min[k] - local_min[i] > max_candle_diff:
                        break

                    b = low[local_min[k]]

                    # Check regression Similarity of A and B wave
                    rng = [local_max[j], local_min[k]]
                    is_regression_cond = regression_check(middle, rng, reg_tol)

                    # make XB wave ratio
                    xa = a - x
                    ab = a - b

                    x_b_ratio = ab / xa
                    if local_min[k] - local_max[j] > min_candle_diff:
                        cond_len_ab = True
                    else:
                        cond_len_ab = False
                    # check the XB wave ratio
                    if ((x_b_ratio_target[0] <= x_b_ratio) and (x_b_ratio_target[-1] >= x_b_ratio)) and\
                            is_regression_cond and (rng[1] - rng[0] > min_candle_diff) and cond_len_ab:
                        # find for the C point
                        while local_max[tmp_c] <= local_min[k]:
                            tmp_c += 1
                            if tmp_c >= len(local_max):
                                break
                        if tmp_c >= len(local_max):
                            break
                        tmp_d = k
                        for p in range(tmp_c, len(local_max)):
                            # Check the Patterns Trend
                            if ab > 0 and trend_direction == 'Bearish':
                                break
                            elif ab < 0 and trend_direction == 'Bullish':
                                break

                            # check for the range of the waves
                            if local_max[p] - local_min[i] > max_candle_diff:
                                break

                            c = high[local_max[p]]

                            # make AC wave ratio
                            bc = (c - b)
                            a_c_ratio = bc / ab
                            # check the AC wave ratio
                            if local_max[p] - local_min[k] > min_candle_diff:
                                cond_len_bc = True
                            else:
                                cond_len_bc = False

                            if (a_c_ratio_target[0] <= a_c_ratio) and (a_c_ratio_target[-1] >= a_c_ratio) and\
                                    cond_len_bc:
                                # find for the d point
                                tmp_d = local_max[p] + 1
                                if tmp_d >= len(high):
                                    break
                                for l in range(tmp_d, len(high)):
                                    # Check the Patterns Trend
                                    if not is_visual and l != len(high) - 1:
                                        continue
                                    if bc > 0 and trend_direction == 'Bearish':
                                        break
                                    elif bc < 0 and trend_direction == 'Bullish':
                                        break
                                    # check for the range of the waves
                                    if l - local_min[i] > max_candle_diff:
                                        break

                                    d = low[l]
                                    # make BD wave ratio
                                    cd = (c - d)
                                    b_d_ratio = cd / bc

                                    # make BD wave ratio
                                    xd = (d - x)
                                    x_d_ratio = 1 - (xd / xa)

                                    # Check regression Similarity
                                    rng = [local_max[p], l]
                                    is_regression_cond = regression_check(middle, rng, reg_tol)

                                    # check the AC wave ratio
                                    if is_regression_cond and ((b_d_ratio_target[0] <= b_d_ratio) and
                                                               (b_d_ratio_target[-1] >= b_d_ratio)) and\
                                            ((x_d_ratio_target[0] <= x_d_ratio) and
                                             (x_d_ratio_target[-1] >= x_d_ratio)) and\
                                            (rng[1] - rng[0] > min_candle_diff):

                                        # check the length of wings with times or (candle Numbers)
                                        ac2bd_cond = True
                                        xb2ac_cond = True
                                        xb2bd_cond = True
                                        xb = local_min[k] - local_min[i]
                                        ac = local_max[p] - local_max[j]
                                        bd = l - local_min[k]
                                        ac2bd = abs(ac - bd) / max([ac, bd])
                                        xb2bd = abs(xb - bd) / max([xb, bd])
                                        xb2ac = abs(xb - ac) / max([xb, ac])
                                        if harmonic_name == 'ABCD' and ac2bd > ac2bd_tr:
                                            ac2bd_cond = False
                                        if harmonic_name == 'ThreeDrives' and xb2bd > 1.5 * xb2bd_tr or xb2ac > 1.5 * xb2ac_tr:
                                            xb2bd_cond = False

                                        if ac2bd_cond and xb2ac_cond and xb2bd_cond:
                                            res.append([local_min[i], local_max[j], local_min[k], local_max[p], l, x, a, b, c, d, x_b_ratio, a_c_ratio, b_d_ratio, x_d_ratio, xb2ac, xb2bd, ac2bd])
    if is_visual:
        p_bar.close()
    if is_visual:
        return res
    else:
        if len(res) > 0:
            return 1
        else:
            return 0


# check Regression Condition function
def regression_check(middle, rng, reg_tol):

    # cast the number to single precision
    c = middle[rng[0]:rng[1]+1]

    # ----- regression Line of harmonic pattern
    S = (c[-1] - c[0]) / (rng[-1] - rng[0])     # slope
    I = c[0] - S * rng[0]   # intersect
    p2 = np.array([S, I])

    # -----  regression Line of candles on
    p = regression_fit(rng, c)

    #   comperasion between the Line of Harmonic and candle line
    return np.sum(np.abs(p2 - p) < abs(p * reg_tol)) == len(p)

    # evaluate Slope and intersect with regression


def regression_fit(rng, middle):
    n = rng[1]-rng[0]+1

    n_floor = math.floor(n / 2)
    numerator = np.sum(((n - 1) / 2 - np.arange(0, n_floor-1)) * (middle[n - np.arange(1, n_floor)] - middle[np.arange(0, n_floor-1)]))
    denumerator = ((n ** 3) - n) / 12

    # slop of regression
    p1 = (numerator / denumerator)

    # intersect of regression
    p2 = (np.sum(middle) / n) - p1 * ((rng[1] + rng[0]) / 2)
    return np.array([p1, p2])


