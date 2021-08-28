import numpy as np
import math
import pandas as pd
import matplotlib.pyplot as plt


# ---------- filter patterns function
def filter_results(high, low, res, middle, harmonic_name, trend_direction, alpha, beta):
    if len(res) == 0:
        return []

    # define Candle Size
    res = get_pattern_size(res)  # 1 to 5 from very small to very large.very small, small, medium, large, very large
    filter_mode = 'Percent'
    res = eliminate_duplicate_patterns(res, trend_direction)

    if filter_mode == 'std':
        res = eliminate_high_std_patterns(res, middle)
    elif filter_mode == 'Percent':
        # alpha = .37  # .37 STD coefficient.higher led to bigger channel
        # beta = .90  # .94 percent of should be in the channel
        res = eliminate_out_of_bound_patterns(res, middle, low, high, harmonic_name, alpha, beta)

    # ---- check the ratio is near to fibonacci number or not
    res = check_the_fibbo_ratio(res, harmonic_name, trend_direction)

    return res


# -- filte based on STD
def eliminate_high_std_patterns(res, middle):
    x_idx = 0
    a_idx = 1
    b_idx = 2
    c_idx = 3
    d_idx = 4

    situation = [False] * len(res)
    for i in range(len(res)):
        situation_x_a = check_std_of_waves(res[i][x_idx:a_idx], middle[res[i][x_idx]: res[i][a_idx]])
        situation_a_b = check_std_of_waves(res[i][a_idx:b_idx], middle[res[i][a_idx]: res[i][b_idx]])
        situation_b_c = check_std_of_waves(res[i][b_idx:c_idx], middle[res[i][b_idx]: res[i][c_idx]])
        situation_c_d = check_std_of_waves(res[i][c_idx:d_idx], middle[res[i][c_idx]: res[i][d_idx]])
        if situation_x_a and situation_a_b and situation_b_c and situation_c_d:
            situation[i] = True
        res[i].append(situation[i])
    return res


def check_std_of_waves(rng, middle):
    alpha = 2 # STD coefficient
    beta = .85 # numberr of candles which be out of theSTD boundery
    situation = False
    range = np.arange(rng[0], rng[-1])
    p = np.polyfit([rng[0], rng[-1]], [middle[0], middle[-1]], 1)
    line = np.polyval(p, range)

    lower_std = line - alpha * np.std(line)
    upper_std = line + alpha * np.std(line)

    if np.sum(middle >= lower_std) > lower_std.size * beta and np.sum(middle <= upper_std) > lower_std.size * beta:
        situation = True
    return situation


# classifiy pattern by their size
def get_pattern_size(res):
    x_idx = 0
    a_idx = 1
    b_idx = 2
    c_idx = 3
    d_idx = 4

    tr1 = 15
    tr2 = 30
    tr3 = 45
    tr4 = 60

    patt_size = np.zeros((len(res), 1))
    for i in range(len(res)):
        pattern_len = res[i][d_idx] - res[i][x_idx]
        if pattern_len <= tr1:
            patt_size[i] = 1
        elif pattern_len > tr1 and pattern_len <= tr2:
            patt_size[i] = 2
        elif pattern_len > tr2 and pattern_len <= tr3:
            patt_size[i] = 3
        elif pattern_len > tr3 and pattern_len <= tr4:
            patt_size[i] = 4
        elif pattern_len > tr4:
            patt_size[i] = 5
        res[i].append(patt_size[i])
    return res


# -- filter Based on percentage of line
def eliminate_out_of_bound_patterns(res, middle, low, high, harmonic_name, alpha, beta):
    mean_of_candle = np.mean(high - low)

    high = middle
    low = middle

    x_idx = 0
    a_idx = 1
    b_idx = 2
    c_idx = 3
    d_idx = 4

    situation = [False] * len(res)
    new_res = []
    for i in range(len(res)):
        rng = np.arange(int(res[i][x_idx]), int(res[i][a_idx] + 1))

        p = np.polyfit([rng[0], rng[-1]], [low[rng[0]], high[rng[-1]]], 1)
        l = np.polyval(p, rng)
        lower_bound, upper_bound = find_boundery(mean_of_candle, middle, low[rng[0]], high[rng[-1]], rng, l, alpha) # XA Leg
        situation_xa = np.sum(np.logical_and(lower_bound < low[rng], high[rng] < upper_bound)) >= rng.size * beta
        if harmonic_name == 'ABCD':
            situation_xa = True

        rng = np.arange(int(res[i][a_idx]), int(res[i][b_idx] + 1))

        p = np.polyfit([rng[0], rng[-1]], [high[rng[0]], low[rng[-1]]], 1)
        l = np.polyval(p, rng)
        lower_bound, upper_bound = find_boundery(mean_of_candle, middle, high[rng[0]], low[rng[-1]], rng, l, alpha)  # AB Leg
        situation_ab = np.sum(np.logical_and(lower_bound < low[rng], high[rng] < upper_bound)) >= rng.size * beta

        rng = np.arange(int(res[i][b_idx]), int(res[i][c_idx] + 1))

        p = np.polyfit([rng[0], rng[-1]], [low[rng[0]], high[rng[-1]]], 1)
        l = np.polyval(p, rng)
        lower_bound, upper_bound = find_boundery(mean_of_candle, middle, low[rng[0]], high[rng[-1]], rng, l, alpha)  # BC Leg
        situation_bc = np.sum(np.logical_and(lower_bound < low[rng], high[rng] < upper_bound)) >= rng.size * beta

        rng = np.arange(int(res[i][c_idx]), int(res[i][d_idx] + 1))

        p = np.polyfit([rng[0], rng[-1]], [low[rng[0]], high[rng[-1]]], 1)
        l = np.polyval(p, rng)
        lower_bound, upper_bound = find_boundery(mean_of_candle, middle, low[rng[0]], high[rng[-1]], rng, l, alpha)  # CD Leg
        situation_cd = np.sum(np.logical_and(lower_bound < low[rng], high[rng] < upper_bound)) >= rng.size * beta

        if situation_xa and situation_ab and situation_bc and situation_cd:
            situation[i] = True
            res[i].append(situation[i])
            new_res.append(res[i])
    return new_res


def get_the_coefficient_of_bound(rng1, rng2):
    tr1 = 8
    tr2 = 20
    tr3 = 40
    tr4 = 70

    alpha, beta = 0, 0
    if rng2 - rng1 <= tr1:
        alpha = .60
        beta = .92
    elif rng2 - rng1 >= tr1 and rng2 - rng1 < tr2:
        alpha = .63
        beta = .92
    elif rng2 - rng1 >= tr2 and rng2 - rng1 < tr3:
        alpha = .64
        beta = .92
    elif rng2 - rng1 >= tr3 and rng2 - rng1 < tr4:
        alpha = .65
        beta = .92
    elif rng2 - rng1 >= tr4:
        alpha = .70
        beta = .92
    return alpha, beta


def find_boundery(mean_of_candle, middle, start_val, end_val, x, y, alpha):  # alpha = .50
    # Example coordinates
    # y = [1 4 7 10 13 16];
    # x = 101:numel(y) + 100;

    # ------------------ find the rotation degree
    slope = np.rad2deg(np.arctan((end_val - start_val) / (x[-1] - x[0])))

    # ------------------ rotate line
    x_hat, y_hat = rotate_line(x, y, -slope)

    # ------------------ find bound of line \
    # upperBound = yHat * (1 + alpha);
    # lowerBound = yHat * (1 - alpha);
    upper_bound = y_hat + (1 + alpha) * np.std(middle[x])
    lower_bound = y_hat - (1 + alpha) * np.std(middle[x])
    # ------------------ de - rotate boundery lines
    _, upper_bound_hat = rotate_line(x_hat, upper_bound, slope)
    _, lower_bound_hat = rotate_line(x_hat, lower_bound, slope)

    return lower_bound_hat, upper_bound_hat


def rotate_line(x, y, deg): # Vertices matrix
    v = np.array((x, y, np.zeros(y.size))).transpose()
    v_centre = np.mean(v, 0)  # Centre, of line
    vc = v - np.ones((v.shape[0], 1)) * v_centre  # Centering coordinates
    a_rad = ((deg * math.pi) / 180)  # Angle in radians
    e = [0,  0, a_rad]  # Euler angles for X, Y, Z - axis rotations

    # Direction Cosines (rotation matrix) construction
    rx = np.array([[1, 0, 0],
                 [0,math.cos(e[0]),  -math.sin(e[0])],
                 [0, math.sin(e[0]),  -math.cos(e[0])]])  # X-Axis rotation

    ry = np.array([[math.cos(e[1]), 0, math.sin(e[1])],
                 [0, 1, 0],
                 [-math.sin(e[1]), 0, math.cos(e[1])]])  # Y-axis rotation

    rz = np.array([[math.cos(e[2]), -math.sin(e[2]), 0],
                 [math.sin(e[2]),  math.cos(e[2]),  0],
                 [0, 0, 1]]) # Z-axis rotation

    r = rx.dot(ry.dot(rz))  # Rotation matrix
    vrc = (r.dot(vc.transpose())).transpose()  # Rotating centred coordinates
    vr = vrc+np.ones((v.shape[0], 1)) * v_centre  # Shifting back to original location
    x = vr[:, 0]
    y = vr[:, 1]
    return x, y


# eliminate duplicate pattern with common D point
def eliminate_duplicate_patterns(res, trend_direction):
    d_idx = 4
    x_val_idx = 5
    a_val_idx = 6
    b_val_idx = 7
    c_val_idx = 8

    ascending = [True, False, True, False]
    if trend_direction == 'Bearish':
        ascending = [True, False, True, False]
    elif trend_direction == 'Bullish':
        ascending = [False, True, False, True]

    if len(res) == 0:
        return []

    res = np.array(res)
    unique_mem = np.unique(res[:, d_idx])
    unique_patterns = np.zeros((res.shape[1], unique_mem.size))

    for i in range(len(unique_mem)):
        unique_idx = unique_mem[i] == res[:, d_idx]
        res_df = pd.DataFrame(res[unique_idx, :])
        # -------- select best patterns, Bullish Patterns
        b = res_df.sort_values(by=[c_val_idx, x_val_idx, a_val_idx, b_val_idx], ascending=ascending).to_numpy()
        unique_patterns[:, i] = b[0, :]
    return unique_patterns.transpose().tolist()


def check_vertex(harmonic_name, res):
    res = np.array(res)
    if harmonic_name == 'ABCD':
        alpha = 2
        res = res[:, np.sum(res[-3: -1,:]) >= alpha & res[-2,:] == 1 & res[-1,:] == 1]
    else:
        alpha = 3
        res = res[:, np.sum(res[-4: -1,:]) >= alpha & res[-2,:] == 1 & res[-1,:] == 1]

    return res

# ---
def check_the_fibbo_ratio(res, harmonic_name, trend_direction):
    return res
