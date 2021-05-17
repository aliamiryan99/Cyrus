import numpy as np
import math

def RegressionLine(data):
    open = np.array([d['open'] for d in data])
    high = np.array([d['high'] for d in data])
    low = np.array([d['low'] for d in data])
    close = np.array([d['close'] for d in data])

    a = np.c_[open, close].max(1)
    b = np.c_[open, close].min(1)
    c = np.c_[open, close].mean(1)
    d = a - b

    # soppose that we have window
    alpha = 1
    beta = 1
    # ---- finding the best window
    window = 3
    localMin = [0] * len(open)
    localMax = [0] * len(open)
    for i in range(window, len(open) - window + 1):
        if low[i] <= low[i - window:i + window].min():
            localMin[i] = i
        if high[i] >= high[i - window:i + window].max():
            localMax[i] = i

    localMax = np.array(list(filter(lambda num: num != 0, localMax)))
    localMin = np.array(list(filter(lambda num: num != 0, localMin)))

    # -----
    lenMinMax = np.zeros((len(localMin)))
    hgtMinMax = np.zeros((len(localMin)))
    lenMaxMin = np.zeros((len(localMax)))
    hgtMaxMin = np.zeros((len(localMax)))
    afterLocalMin = np.zeros((len(localMin)), 'int')
    for i in range(len(localMin)):
        tmp = localMax[np.nonzero(localMin[i] < localMax)[0]]
        if len(tmp) != 0:
            afterLocalMin[i] = tmp[0]
        else:
            afterLocalMin[i] = len(open) - 1
        lenMinMax[i] = afterLocalMin[i] - localMin[i]
        hgtMinMax[i] = open[afterLocalMin[i]] - low[localMin[i]]

    afterLocalMin = np.array(list(filter(lambda num: num != 0, afterLocalMin)))

    afterLocalMax = [float('nan')] * len(localMax)
    for i in range(len(localMax)):
        tmp = localMin[np.nonzero(localMax[i] < localMin)[0]]
        if len(tmp) != 0:
            afterLocalMax[i] = tmp[0]
        else:
            afterLocalMax[i] = len(open) - 1

        lenMaxMin[i] = afterLocalMax[i] - localMax[i]
        hgtMaxMin[i] = open[afterLocalMax[i]] - high[localMax[i]]

    alpha = 1
    meanMinMax = np.floor(alpha * np.mean(lenMinMax))
    meanMaxMin = np.floor(alpha * np.mean(lenMaxMin))
    windowUP = meanMinMax.copy().astype(np.int64)
    windowDown = meanMaxMin.copy().astype(np.int64)

    # Trend Line
    # ----- Posetive trend
    x = np.zeros((2, len(open))).astype(np.int64)
    y = np.zeros((2, len(open)))
    p = np.zeros((2, len(open)))
    lPos = np.zeros((2, len(open)))
    for i in range(windowUP, len(open)):
        x[:, i] = np.array([i - windowUP, i]).astype(np.int64)
        p[:, i] = np.polyfit((np.arange(x[0][i], (x[1][i]+1))), (b[x[0][i]:(x[1][i]+1)]), 1)
        #    p(:,i) = polyfit(x(:,i),a(x(:,i)),1)';
        lPos[:, i] = np.polyval(p[:, i], x[:, i])

    sPosIdx = np.nonzero(p[0, :] > alpha * np.mean(p[0, p[0, :] > 0]))[0]
    posLine = p[:, p[0, :] > alpha * np.mean(p[0, p[0, :] > 0])]

    # ---- Negative trend
    x = np.zeros((2, len(open))).astype(np.int64)
    y = np.zeros((2, len(open)))
    p = np.zeros((2, len(open)))
    lNeg = np.zeros((2, len(open)))
    for i in range(windowDown, len(open)):
        x[:, i] = np.array([i - windowDown, i]).astype(np.int64)
        p[:, i] = (np.polyfit((np.arange(x[0][i], (x[1][i]+1))), a[x[0][i]:(x[1][i]+1)], 1))
        lNeg[:, i] = np.polyval(p[:, i], x[:, i])

    sNegIdx = np.nonzero(p[0, :] < beta * np.mean(p[0, p[0, :] < 0]))[0]
    negLine = p[:, p[0, :] < beta * np.mean(p[0, p[0, :] < 0])]

    # find crossing points
    lCrossPosIdx = np.zeros((2, len(posLine[0, :])))
    lCrossPos = np.zeros((2, len(posLine[0, :])))

    for i in range(len(sPosIdx)):
        x = np.arange(sPosIdx[i], len(open))
        l = np.polyval(np.transpose(posLine[:, i]), x)
        c = np.nonzero(np.logical_and(np.transpose(l) > open[x], close[x] < open[x]))[0]
        if len(c) != 0:
            lCrossPosIdx[:, i] = [x[0], x[c[0]]]
            lCrossPos[:, i] = [l[0], l[c[0]]]
        else:
            lCrossPosIdx[:, i] = [x[0], float('nan')]
            lCrossPos[:, i] = [l[0], l[-1]]

    # down trend
    lCrossNegIdx = np.zeros((2, len(negLine[0, :])))
    lCrossNeg = np.zeros((2, len(negLine[0, :])))

    for i in range(len(sNegIdx)):
        x = np.arange(sNegIdx[i], len(open))
        l = np.polyval(np.transpose(negLine[:, i]), x)
        c = np.nonzero(np.logical_and(np.transpose(l) < open[x], close[x] > open[x]))[0]
        if len(c) != 0:
            lCrossNegIdx[:, i] = [x[0], x[c[0]]]
            lCrossNeg[:, i] = [l[0], l[c[0]]]
        else:
            lCrossNegIdx[:, i] = [x[0], float('nan')]
            lCrossNeg[:, i] = [l[0], l[-1]]

    xUp = [sPosIdx - windowUP, sPosIdx]
    yUp = lPos[:, sPosIdx]
    xExtUp = lCrossPosIdx.copy()
    np.nan_to_num(xExtUp[1], nan=np.sum(np.isnan(xExtUp[1])))
    yExtUp = lCrossPos.copy()
    xSell = lCrossPosIdx[1, ~np.isnan(lCrossPosIdx[1, :])].astype(np.int64)
    ySell = close[xSell]

    xDown = [sNegIdx - windowDown, sNegIdx]
    yDown = lNeg[:, sNegIdx]
    xExtDown = lCrossNegIdx.copy()
    np.nan_to_num(xExtDown[1], nan=np.sum(np.isnan(xExtDown[1])))
    yExtDown = lCrossNeg.copy()
    xBuy = lCrossNegIdx[1, ~np.isnan(lCrossNegIdx[1, :])].astype(np.int64)
    yBuy = close[xBuy]

    return xUp, yUp, xExtUp, yExtUp, xBuy, yBuy, xDown, yDown, xExtDown, yExtDown, xSell, ySell
