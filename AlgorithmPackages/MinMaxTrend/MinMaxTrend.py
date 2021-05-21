
import copy

from AlgorithmTools.CandleTools import *
from AlgorithmTools.LocalExtermums import *


def min_max_trend_detect(open, high, low, close, top, bottom, local_min, local_max, is_visual):
    x_up_trend, y_up_trend, x_down_trend, y_down_trend, x_extend_inc, y_extend_inc, x_extend_dec, y_extend_dec = \
        [], [], [], [], [], [], [], []

    # up trend
    window = 1
    low_diff = np.r_[[0], np.diff(low[local_min])] > 0
    up_trend = get_trend(len(open), window, low_diff)
    past_local_min = get_past_local_extremum(up_trend, local_min, low_diff)

    mode = 'Last'
    x_best_up_trend = [0] * len(up_trend)
    for i in range(len(up_trend)):
        if up_trend[i] != 0 and past_local_min[i] != 0:
            rng = np.arange(past_local_min[i], up_trend[i] + 1)
            # find all permutations
            cnt = -1
            x = []
            p = []
            x_better_up_trend = []
            for j in range(past_local_min[i], up_trend[i] + 1):
                for k in range(past_local_min[i], up_trend[i] + 1):
                    if j > k:
                        cnt = cnt + 1
                        x.append([k, j])
                        y = np.transpose(low[local_min[x[cnt]]])
                        p.append(np.polyfit(local_min[x[cnt]], y, 1))
                        line = np.polyval(p[cnt], local_min[rng])
                        if np.sum(line <= low[local_min[rng]]) == int(np.size(rng)):
                            x_better_up_trend.append([p[cnt][0], int(k), int(j)])

            if mode == 'Mean':
                if len(x_better_up_trend) != 0:
                    tmp = copy.copy(x_better_up_trend)
                    if len(tmp) != 0:
                        slope = tmp[::3]
                        [_, idx] = np.sort((abs(slope - np.mean(slope))))
                        x_best_up_trend[i] = (x_better_up_trend[idx[0]])

            elif mode == 'Atan':
                if len(x_better_up_trend) != 0:
                    tmp = copy.copy(x_better_up_trend)
                    if len(tmp) != 0:
                        slope = tmp[::3]
                        [_, idx] = np.sort((abs(np.arctan(slope) - np.mean(np.arctan(slope)))))
                        x_best_up_trend[i] = (x_better_up_trend[idx[0]])

            elif mode == 'First':
                if len(x_better_up_trend) != 0:
                    tmp = copy.copy(x_better_up_trend)
                    if len(tmp) != 0:
                        x_best_up_trend[i] = (x_better_up_trend[0])
            elif mode == 'Last':
                if len(x_better_up_trend) != 0:
                    tmp = copy.copy(x_better_up_trend)
                    if len(tmp) != 0:
                        x_best_up_trend[i] = (x_better_up_trend[-1])

    x_best_up_trend = np.array(list(filter(lambda num: num != 0, x_best_up_trend)))
    if len(x_best_up_trend) != 0:

        x_up_trend = x_best_up_trend.flatten()
        x_up_trend = np.delete(x_up_trend, range(0, len(x_up_trend), 3))
        x_up_trend = x_up_trend.astype(int)
        x_up_trend = local_min[x_up_trend.reshape(int(np.size(x_up_trend) / 2), 2)]
        y_up_trend = low[x_up_trend]

        # find crossing points
        sell_idx = [0] * len(x_best_up_trend)
        sell = [0] * len(x_best_up_trend)
        x_extend_inc = [0] * len(x_best_up_trend)
        y_extend_inc = [0] * len(x_best_up_trend)
        for i in range(len(x_best_up_trend)):
            x = local_min[[int(x_best_up_trend[i][1]), int(x_best_up_trend[i][2])]]
            y = low[x]
            p = np.polyfit(x, y, 1)
            y = np.polyval(p, np.arange(x[1], len(low)))
            t = np.nonzero(top[local_min[int(x_best_up_trend[i][2])]:] < np.transpose(
                y[:]))[0]
            if len(t) != 0:
                t = t[0]
                x_extend_inc[i] = (np.transpose(
                    np.arange(local_min[int(x_best_up_trend[i][2])], local_min[int(x_best_up_trend[i][2])] + t + 1)))
                y_extend_inc[i] = (np.transpose(y[:t + 1]))
                sell_idx[i] = x_extend_inc[i][-1]
                sell[i] = close[sell_idx[i]]
        sell_idx = np.array(list(filter(lambda num: num != 0, sell_idx)))
        sell = np.array(list(filter(lambda num: num != 0, sell)))
    else:
        sell_idx = []
        sell = []

    # DownTrend
    window = 1
    high_diff = np.r_[[0], np.diff(high[local_max])] < 0
    down_trend = get_trend(len(open), window, high_diff)
    past_local_max = get_past_local_extremum(down_trend, local_max, high_diff)

    alpha = .000001
    # % mode = 'last'
    x_best_down_trend = [0] * len(down_trend)
    for i in range(len(down_trend)):
        if down_trend[i] != 0 and past_local_max[i] != 0:
            A = np.arange(past_local_max[i],down_trend[i]+1)
            # find all permutations
            cnt = -1
            x = []
            p = []
            x_better_down_trend = []
            for j in range(past_local_max[i], down_trend[i]+1):
                for k in range(past_local_max[i], down_trend[i]+1):
                    if j > k:
                        cnt = cnt + 1
                        x.append([k, j])
                        y = np.transpose(high[local_max[x[cnt]]])
                        p.append(np.polyfit(local_max[x[cnt]], y, 1))
                        line = np.polyval(p[cnt], local_max[A])
                        if np.sum(line + alpha >= high[local_max[A]]) == int(np.size(A)):
                            x_better_down_trend.append([p[cnt][0], int(k), int(j)])
            if mode == 'Mean':
                if len(x_better_down_trend) != 0:
                    tmp = copy.copy(x_better_down_trend)
                    if len(tmp) != 0:
                        slope = tmp[::3]
                        [_, idx] = np.sort((np.abs(slope - np.mean(slope))))
                        x_best_down_trend[i] = (x_better_down_trend[idx[0]])
                elif mode == 'Atan':
                    if len(x_better_down_trend) == 0:
                        tmp = copy.copy(x_better_down_trend)
                        if len(tmp) != 0:
                            slope = tmp[::3]
                            [_, idx] = np.sort((np.abs(np.arctan(slope) - np.mean(np.arctan(slope)))))
                            x_best_down_trend[i] = (x_better_down_trend[idx[0]])
            elif mode == 'First':
                if len(x_better_down_trend) != 0:
                    tmp = copy.copy(x_better_down_trend)
                    if len(tmp) != 0:
                        x_best_down_trend[i] = (x_better_down_trend[0])
            elif mode == 'Last':
                if len(x_better_down_trend) != 0:
                    tmp = copy.copy(x_better_down_trend)
                    if len(tmp) != 0:
                        x_best_down_trend[i] = (x_better_down_trend[-1])


    x_best_down_trend = np.array(list(filter(lambda num: num != 0,x_best_down_trend)))
    if len(x_best_down_trend) != 0:
        x_down_trend = x_best_down_trend.flatten()
        x_down_trend = np.delete(x_down_trend, range(0,len(x_down_trend), 3))
        x_down_trend = x_down_trend.astype(int)
        x_down_trend = local_max[x_down_trend.reshape(int(np.size(x_down_trend) / 2), 2)]
        y_down_trend = high[x_down_trend]

        # find crossing points
        buy_idx = [0] * len(x_best_down_trend)
        buy = [0] * len(x_best_down_trend)
        x_extend_dec = [0] * len(x_best_down_trend)
        y_extend_dec = [0] * len(x_best_down_trend)
        for i in range(len(x_best_down_trend)):
            x = local_max[[int(x_best_down_trend[i][1]), int(x_best_down_trend[i][2])]]
            y = high[x]
            p = np.polyfit(x, y, 1)
            y = np.polyval(p, np.arange(x[1], len(high)))
            t = np.nonzero(bottom[local_max[int(x_best_down_trend[i][2])]:] >
                           y[:])[0]
            if len(t) != 0:
                t = t[0]
                x_extend_dec[i] = (np.transpose(np.arange(local_max[int(x_best_down_trend[i][2])],
                                                          local_max[int(x_best_down_trend[i][2])] + t + 1)))
                y_extend_dec[i] = (np.transpose(y[: t + 1]))
                buy_idx[i] = x_extend_dec[i][-1]
                buy[i] = close[buy_idx[i]]

        buy_idx = np.array(list(filter(lambda num: num != 0, buy_idx)))
        buy = np.array(list(filter(lambda num: num != 0, buy)))
    else:
        buy_idx = []
        buy = []

    if is_visual:
        return x_up_trend, y_up_trend, x_down_trend, y_down_trend, x_extend_inc, y_extend_inc, x_extend_dec, y_extend_dec, \
               sell_idx, sell, buy_idx, buy
    else:
        predict = 0

        cur_idx = len(open) - 1
        i = len(buy_idx) - 1
        while i >= 0 and buy_idx[i] == cur_idx:
            predict = 1
            i -= 1
        i = len(sell_idx) - 1
        while i >= 0 and sell_idx[i] == cur_idx:
            predict = -1
            i -= 1

        return predict


def get_trend(data_size, window, diff):
    trend = [0] * data_size
    for i in range(window, len(diff)):
        if np.sum(diff[i - window:i + 1]) == window + 1:
            trend[i] = i
    return list(filter(lambda num: num != 0, trend))


def get_past_local_extremum(trend, local_extremum, diff):
    past_local_extremum = [0] * len(trend)
    for i in range(len(trend)):
        local_extremum_idx = np.nonzero(local_extremum[trend[i]] == local_extremum)
        past_local_extremum[i] = np.nonzero(~diff[:local_extremum_idx[0][0]])[0][-1]
    return past_local_extremum

