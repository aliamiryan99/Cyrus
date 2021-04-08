import numpy as np
import copy


def predict(data, window_exteremum, window_trend, mode_trend):
    Open = np.array([d['Open'] for d in data])
    High = np.array([d['High'] for d in data])
    Low = np.array([d['Low'] for d in data])
    Close = np.array([d['Close'] for d in data])

    a = np.c_[Open, Close].max(1)
    b = np.c_[Open, Close].min(1)

    window = window_exteremum
    localMin = [0] * len(Open)
    localMax = [0] * len(Open)
    for i in range(window, len(Open)-window+1):
        if Low[i] <= Low[i-window:i+window].min():
            localMin[i] = i
        if High[i] >= High[i-window:i+window].max():
            localMax[i] = i

    localMax = np.array(list(filter(lambda num: num != 0, localMax)))
    localMin = np.array(list(filter(lambda num: num != 0, localMin)))

    ## up trend
    window = window_trend
    lowDiff = np.r_[[0], np.diff(Low[localMin])] > 0
    upTrend = [0] * len(Open)
    for i in range(window, len(lowDiff)):
        if np.sum(lowDiff[i-window:i+1]) == window+1:
            upTrend[i] = i
    upTrend = list(filter(lambda num: num != 0, upTrend))


    pastLocalMin = [0] * len(upTrend)
    for i in range(len(upTrend)):
        localMinIdx = np.nonzero(localMin[upTrend[i]] == localMin)
        pastLocalMin[i] = np.nonzero(~lowDiff[:localMinIdx[0][0]])[0][-1]

    Mode = mode_trend
    xBestUptrend = [0] * len(upTrend)
    for i in range(len(upTrend)):
        if upTrend[i]!=0 and pastLocalMin[i] != 0:
            A = np.arange(pastLocalMin[i], upTrend[i]+1)
            # find all permutations
            cnt = -1
            X = []
            p = []
            xBetterUptrend = []
            for j in range(pastLocalMin[i], upTrend[i]+1):
                for k in range(pastLocalMin[i], upTrend[i]+1):
                    if j > k:
                        cnt = cnt + 1
                        X.append([k,j])
                        y = np.transpose(Low[localMin[X[cnt]]])
                        p.append(np.polyfit(localMin[X[cnt]], y, 1))
                        line = np.polyval(p[cnt], localMin[A])
                        if np.sum(line <= Low[localMin[A]]) == int(np.size(A)):
                            xBetterUptrend.append([p[cnt][0], int(k), int(j)])

            if Mode == 'Mean':
                if len(xBetterUptrend) != 0:
                    tmp = copy.copy(xBetterUptrend)
                    if len(tmp) != 0:
                        slope = tmp[::3]
                        [_, idx] = np.sort((abs(slope - np.mean(slope))))
                        xBestUptrend[i] = (xBetterUptrend[idx[0]])

            elif Mode == 'Atan':
                if len(xBetterUptrend) != 0:
                    tmp = copy.copy(xBetterUptrend)
                    if len(tmp) != 0:
                        slope = tmp[::3]
                        [_, idx] = np.sort((abs(np.arctan(slope) - np.mean(np.arctan(slope)))))
                        xBestUptrend[i] = (xBetterUptrend[idx[0]])

            elif Mode == 'First':
                if len(xBetterUptrend) != 0:
                    tmp = copy.copy(xBetterUptrend)
                    if len(tmp) != 0:
                        xBestUptrend[i] = (xBetterUptrend[0])
            elif Mode == 'Last':
                if len(xBetterUptrend) != 0:
                    tmp = copy.copy(xBetterUptrend)
                    if len(tmp) != 0:
                        xBestUptrend[i] = (xBetterUptrend[-1])


    xBestUptrend = np.array(list(filter(lambda num: num != 0, xBestUptrend)))
    if len(xBestUptrend) != 0:

        xUptrend = xBestUptrend.flatten()
        xUptrend = np.delete(xUptrend, range(0,len(xUptrend), 3))
        xUptrend = xUptrend.astype(int)
        xUptrend = localMin[xUptrend.reshape(int(np.size(xUptrend) / 2), 2)]
        yUptrend = Low[xUptrend]

        # find crossing points
        sellIdx = [0] * len(xBestUptrend)
        sell = [0] * len(xBestUptrend)
        xExtendInc = [0] * len(xBestUptrend)
        yExtendInc = [0] * len(xBestUptrend)
        for i in range(len(xBestUptrend)):
            x = localMin[[int(xBestUptrend[i][1]),int(xBestUptrend[i][2])]]
            y = Low[x]
            P = np.polyfit(x, y, 1)
            y = np.polyval(P, np.arange(x[1], len(Low)))
            t = np.nonzero(a[localMin[int(xBestUptrend[i][2])]:] < np.transpose(
                y[:]))[0]
            if len(t) != 0:
                t = t[0]
                xExtendInc[i] = (np.transpose(np.arange(localMin[int(xBestUptrend[i][2])], localMin[int(xBestUptrend[i][2])]+t + 1)))
                yExtendInc[i] = (np.transpose(y[:t + 1]))
                sellIdx[i] = xExtendInc[i][-1]
                sell[i] = Close[sellIdx[i]]
        sellIdx = np.array(list(filter(lambda num: num != 0, sellIdx)))
        sell = np.array(list(filter(lambda num: num != 0, sell)))
    else:
        sellIdx = []
        sell = []

    # DownTrend
    window = window_trend
    HighDiff = np.r_[[0], np.diff(High[localMax])] < 0
    downTrend = [0] * len(data)
    for i in range(window, len(HighDiff)):
        if np.sum(HighDiff[i-window:i+1]) == window+1:
            downTrend[i] = i

    downTrend = list(filter(lambda num: num != 0, downTrend))

    # % Candle(double(Data.Open),double(Data.High),double(Data.Low),double(Data.Close)),hold on, grid minor, title([char(Symbole) ', Daily']);
    # % plot(localMax,Data.High(localMax),'g*')
    # % plot(localMax(downTrend),Data.High(localMax(downTrend)),'r*')
    # %

    pastLocalMax = [0] * len(data)
    for i in range(len(downTrend)):
        localMaxIdx = np.nonzero(localMax[downTrend[i]] == localMax)
        pastLocalMax[i] = np.nonzero(~HighDiff[:localMaxIdx[0][0]])[0][-1]

    alpha = .000001
    # % Mode = 'last'
    xBestDowntrend = [0] * len(downTrend)
    for i in range(len(downTrend)):
        if downTrend[i]!=0 and pastLocalMax[i]!=0:
            A = np.arange(pastLocalMax[i],downTrend[i]+1)
            #% find all permutations
            cnt = -1
            X = []
            p = []
            xBetterDowntrend = []
            for j in range(pastLocalMax[i],downTrend[i]+1):
                for k in range(pastLocalMax[i],downTrend[i]+1):
                    if j > k:
                        cnt = cnt + 1
                        X.append([k, j])
                        y = np.transpose(High[localMax[X[cnt]]])
                        p.append(np.polyfit(localMax[X[cnt]], y, 1))
                        line = np.polyval(p[cnt], localMax[A])
                        if np.sum(line + alpha >= High[localMax[A]]) == int(np.size(A)):
                            xBetterDowntrend.append([p[cnt][0], int(k), int(j)])
            if Mode == 'Mean':
                if len(xBetterDowntrend) != 0:
                    tmp = copy.copy(xBetterDowntrend)
                    if len(tmp) != 0:
                        slope = tmp[::3]
                        [_, idx] = np.sort((np.abs(slope - np.mean(slope))))
                        xBestDowntrend[i] = (xBetterDowntrend[idx[0]])
                elif Mode == 'Atan':
                    if len(xBetterDowntrend) == 0:
                        tmp = copy.copy(xBetterDowntrend)
                        if len(tmp) != 0:
                            slope = tmp[::3]
                            [_, idx] = np.sort((np.abs(np.arctan(slope) - np.mean(np.arctan(slope)))))
                            xBestDowntrend[i] = (xBetterDowntrend[idx[0]])
            elif Mode == 'First':
                if len(xBetterDowntrend) != 0:
                    tmp = copy.copy(xBetterDowntrend)
                    if len(tmp) != 0:
                        xBestDowntrend[i] = (xBetterDowntrend[0])
            elif Mode == 'Last':
                if len(xBetterDowntrend) != 0:
                    tmp = copy.copy(xBetterDowntrend)
                    if len(tmp) != 0:
                        xBestDowntrend[i] = (xBetterDowntrend[-1])

    xBestDowntrend = np.array(list(filter(lambda num: num != 0,xBestDowntrend)))
    if len(xBestDowntrend) != 0:
        xDowntrend = xBestDowntrend.flatten()
        xDowntrend = np.delete(xDowntrend, range(0,len(xDowntrend), 3))
        xDowntrend = xDowntrend.astype(int)
        xDowntrend = localMax[xDowntrend.reshape(int(np.size(xDowntrend) / 2), 2)]
        yDowntrend = High[xDowntrend]

        #% find crossing points
        buyIdx = [0] * len(xBestDowntrend)
        buy = [0] * len(xBestDowntrend)
        xExtendDec = [0] * len(xBestDowntrend)
        yExtendDec = [0] * len(xBestDowntrend)
        for i in range(len(xBestDowntrend)):
            x = localMax[[int(xBestDowntrend[i][1]), int(xBestDowntrend[i][2])]]
            y = High[x]
            P = np.polyfit(x, y, 1)
            y = np.polyval(P, np.arange(x[1], len(High)))
            t = np.nonzero(b[localMax[int(xBestDowntrend[i][2])]:] >
                y[:])[0]
            if len(t) != 0:
                t = t[0]
                xExtendDec[i] = (np.transpose(np.arange(localMax[int(xBestDowntrend[i][2])], localMax[int(xBestDowntrend[i][2])] + t + 1)))
                yExtendDec[i] = (np.transpose(y[: t + 1]))
                buyIdx[i] = xExtendDec[i][-1]
                buy[i] = Close[buyIdx[i]]

        buyIdx = np.array(list(filter(lambda num: num != 0, buyIdx)))
        buy = np.array(list(filter(lambda num: num != 0, buy)))
    else:
        buyIdx = []
        buy = []

    predict = 0

    curIdx = len(data) - 1
    i = len(buyIdx) - 1
    while(i >= 0 and buyIdx[i] == curIdx):
        predict += 1
        i -= 1
    i = len(sellIdx) - 1
    while (i >= 0 and sellIdx[i] == curIdx):
        predict -= 1
        i -= 1
    return predict
