import numpy as np
import math


def regression_line_detection(open, high, low, close, top, bottom, local_min, local_max, is_visual):

    # suppose that we have window
    alpha = 1
    beta = 1
    # ---- finding the best window
    # window = 3

    # -----
    len_min_max = np.zeros((len(local_min)))
    hgt_min_max = np.zeros((len(local_min)))
    len_max_min = np.zeros((len(local_max)))
    hgt_max_min = np.zeros((len(local_max)))
    after_local_min = np.zeros((len(local_min)), 'int')
    for i in range(len(local_min)):
        tmp = local_max[np.nonzero(local_min[i] < local_max)[0]]
        if len(tmp) != 0:
            after_local_min[i] = tmp[0]
        else:
            after_local_min[i] = len(open) - 1
        len_min_max[i] = after_local_min[i] - local_min[i]
        hgt_min_max[i] = open[after_local_min[i]] - low[local_min[i]]

    after_local_min = np.array(list(filter(lambda num: num != 0, after_local_min)))

    after_local_max = [float('nan')] * len(local_max)
    for i in range(len(local_max)):
        tmp = local_min[np.nonzero(local_max[i] < local_min)[0]]
        if len(tmp) != 0:
            after_local_max[i] = tmp[0]
        else:
            after_local_max[i] = len(open) - 1

        len_max_min[i] = after_local_max[i] - local_max[i]
        hgt_max_min[i] = open[after_local_max[i]] - high[local_max[i]]

    alpha = 1
    mean_min_max = np.floor(alpha * np.mean(len_min_max))
    mean_max_min = np.floor(alpha * np.mean(len_max_min))
    window_up = mean_min_max.copy().astype(np.int64)
    window_down = mean_max_min.copy().astype(np.int64)

    # Trend Line
    # ----- Posetive trend
    x = np.zeros((2, len(open))).astype(np.int64)
    y = np.zeros((2, len(open)))
    p = np.zeros((2, len(open)))
    l_pos = np.zeros((2, len(open)))
    for i in range(window_up, len(open)):
        x[:, i] = np.array([i - window_up, i]).astype(np.int64)
        p[:, i] = np.polyfit((np.arange(x[0][i], (x[1][i]+1))), (bottom[x[0][i]:(x[1][i] + 1)]), 1)
        #    p(:,i) = polyfit(x(:,i),top(x(:,i)),1)';
        l_pos[:, i] = np.polyval(p[:, i], x[:, i])

    s_pos_idx = np.nonzero(p[0, :] > alpha * np.mean(p[0, p[0, :] > 0]))[0]
    pos_line = p[:, p[0, :] > alpha * np.mean(p[0, p[0, :] > 0])]

    # ---- Negative trend
    x = np.zeros((2, len(open))).astype(np.int64)
    y = np.zeros((2, len(open)))
    p = np.zeros((2, len(open)))
    l_neg = np.zeros((2, len(open)))
    for i in range(window_down, len(open)):
        x[:, i] = np.array([i - window_down, i]).astype(np.int64)
        p[:, i] = (np.polyfit((np.arange(x[0][i], (x[1][i]+1))), top[x[0][i]:(x[1][i] + 1)], 1))
        l_neg[:, i] = np.polyval(p[:, i], x[:, i])

    s_neg_idx = np.nonzero(p[0, :] < beta * np.mean(p[0, p[0, :] < 0]))[0]
    neg_line = p[:, p[0, :] < beta * np.mean(p[0, p[0, :] < 0])]

    # find crossing points
    l_cross_pos_idx = np.zeros((2, len(pos_line[0, :])))
    l_cross_pos = np.zeros((2, len(pos_line[0, :])))

    for i in range(len(s_pos_idx)):
        x = np.arange(s_pos_idx[i], len(open))
        l = np.polyval(np.transpose(pos_line[:, i]), x)
        c = np.nonzero(np.logical_and(np.transpose(l) > open[x], close[x] < open[x]))[0]
        if len(c) != 0:
            l_cross_pos_idx[:, i] = [x[0], x[c[0]]]
            l_cross_pos[:, i] = [l[0], l[c[0]]]
        else:
            l_cross_pos_idx[:, i] = [x[0], float('nan')]
            l_cross_pos[:, i] = [l[0], l[-1]]

    # down trend
    l_cross_neg_idx = np.zeros((2, len(neg_line[0, :])))
    l_cross_neg = np.zeros((2, len(neg_line[0, :])))

    for i in range(len(s_neg_idx)):
        x = np.arange(s_neg_idx[i], len(open))
        l = np.polyval(np.transpose(neg_line[:, i]), x)
        c = np.nonzero(np.logical_and(np.transpose(l) < open[x], close[x] > open[x]))[0]
        if len(c) != 0:
            l_cross_neg_idx[:, i] = [x[0], x[c[0]]]
            l_cross_neg[:, i] = [l[0], l[c[0]]]
        else:
            l_cross_neg_idx[:, i] = [x[0], float('nan')]
            l_cross_neg[:, i] = [l[0], l[-1]]

    x_up = [s_pos_idx - window_up, s_pos_idx]
    y_up = l_pos[:, s_pos_idx]
    x_ext_up = l_cross_pos_idx.copy()
    np.nan_to_num(x_ext_up[1], nan=np.sum(np.isnan(x_ext_up[1])))
    y_ext_up = l_cross_pos.copy()
    x_sell = l_cross_pos_idx[1, ~np.isnan(l_cross_pos_idx[1, :])].astype(np.int64)
    y_sell = close[x_sell]

    x_down = [s_neg_idx - window_down, s_neg_idx]
    y_down = l_neg[:, s_neg_idx]
    x_ext_down = l_cross_neg_idx.copy()
    np.nan_to_num(x_ext_down[1], nan=np.sum(np.isnan(x_ext_down[1])))
    y_ext_down = l_cross_neg.copy()
    x_buy = l_cross_neg_idx[1, ~np.isnan(l_cross_neg_idx[1, :])].astype(np.int64)
    y_buy = close[x_buy]
    if is_visual:
        return x_up, y_up, x_ext_up, y_ext_up, x_buy, y_buy, x_down, y_down, x_ext_down, y_ext_down, x_sell, y_sell
    else:
        predict = 0
        curIdx = len(open) - 1
        if len(x_buy) != 0 and x_buy[len(x_buy) - 1] == curIdx:
            predict = 1
        if len(x_sell) != 0 and x_sell[len(x_sell) - 1] == curIdx:
            predict = -1
        return predict
