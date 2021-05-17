import numpy as np
import math


def predict(data, alpha, beta, windwo_exteremum):
    Open = np.array([d['Open'] for d in data])
    High = np.array([d['High'] for d in data])
    Low = np.array([d['Low'] for d in data])
    Close = np.array([d['Close'] for d in data])

    a = np.c_[Open, Close].max(1)
    b = np.c_[Open, Close].min(1)
    c = np.c_[Open, Close].mean(1)
    d = a - b

    # ---- finding the best window
    window = windwo_exteremum
    localMin = [0] * len(Open)
    localMax = [0] * len(Open)
    for i in range(window, len(Open) - window + 1):
        if Low[i] <= Low[i - window:i + window].min():
            localMin[i] = i
        if High[i] >= High[i - window:i + window].max():
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
            afterLocalMin[i] = len(Open) - 1
        lenMinMax[i] = afterLocalMin[i] - localMin[i]
        hgtMinMax[i] = Open[afterLocalMin[i]] - Low[localMin[i]]

    afterLocalMin = np.array(list(filter(lambda num: num != 0, afterLocalMin)))

    afterLocalMax = [float('nan')] * len(localMax)
    for i in range(len(localMax)):
        tmp = localMin[np.nonzero(localMax[i] < localMin)[0]]
        if len(tmp) != 0:
            afterLocalMax[i] = tmp[0]
        else:
            afterLocalMax[i] = len(Open) - 1

        lenMaxMin[i] = afterLocalMax[i] - localMax[i]
        hgtMaxMin[i] = Open[afterLocalMax[i]] - High[localMax[i]]

    meanMinMax = np.floor(alpha * np.mean(lenMinMax))
    meanMaxMin = np.floor(alpha * np.mean(lenMaxMin))
    windowUP = meanMinMax.copy().astype(np.int64)
    windowDown = meanMaxMin.copy().astype(np.int64)

    # Trend Line
    # ----- Posetive trend
    x = np.zeros((2, len(Open))).astype(np.int64)
    y = np.zeros((2, len(Open)))
    p = np.zeros((2, len(Open)))
    lPos = np.zeros((2, len(Open)))
    for i in range(windowUP, len(Open)):
        x[:, i] = np.array([i - windowUP, i]).astype(np.int64)
        p[:, i] = np.polyfit((np.arange(x[0][i], (x[1][i]+1))), (b[x[0][i]:(x[1][i]+1)]), 1)
        #    p(:,i) = polyfit(x(:,i),a(x(:,i)),1)';
        lPos[:, i] = np.polyval(p[:, i], x[:, i])

    sPosIdx = np.nonzero(p[0, :] > alpha * np.mean(p[0, p[0, :] > 0]))[0]
    posLine = p[:, p[0, :] > alpha * np.mean(p[0, p[0, :] > 0])]

    # ---- Negative trend
    x = np.zeros((2, len(Open))).astype(np.int64)
    y = np.zeros((2, len(Open)))
    p = np.zeros((2, len(Open)))
    lNeg = np.zeros((2, len(Open)))
    for i in range(windowDown, len(Open)):
        x[:, i] = np.array([i - windowDown, i]).astype(np.int64)
        p[:, i] = (np.polyfit((np.arange(x[0][i], (x[1][i]+1))), a[x[0][i]:(x[1][i]+1)], 1))
        lNeg[:, i] = np.polyval(p[:, i], x[:, i])

    sNegIdx = np.nonzero(p[0, :] < beta * np.mean(p[0, p[0, :] < 0]))[0]
    negLine = p[:, p[0, :] < beta * np.mean(p[0, p[0, :] < 0])]

    # find crossing points
    lCrossPosIdx = np.zeros((2, len(posLine[0, :])))
    lCrossPos = np.zeros((2, len(posLine[0, :])))

    for i in range(len(sPosIdx)):
        x = np.arange(sPosIdx[i], len(Open))
        l = np.polyval(np.transpose(posLine[:, i]), x)
        c = np.nonzero(np.logical_and(np.transpose(l) > Open[x], Close[x] < Open[x]))[0]
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
        x = np.arange(sNegIdx[i], len(Open))
        l = np.polyval(np.transpose(negLine[:, i]), x)
        c = np.nonzero(np.logical_and(np.transpose(l) < Open[x], Close[x] > Open[x]))[0]
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
    ySell = Close[xSell]

    xDown = [sNegIdx - windowDown, sNegIdx]
    yDown = lNeg[:, sNegIdx]
    xExtDown = lCrossNegIdx.copy()
    np.nan_to_num(xExtDown[1], nan=np.sum(np.isnan(xExtDown[1])))
    yExtDown = lCrossNeg.copy()
    xBuy = lCrossNegIdx[1, ~np.isnan(lCrossNegIdx[1, :])].astype(np.int64)
    yBuy = Close[xBuy]

    predict = 0

    curIdx = len(data) - 1

    if xBuy[len(xBuy) - 1] == curIdx:
        predict = 1

    if xSell[len(xSell) - 1] == curIdx:
        predict = -1

    return predict