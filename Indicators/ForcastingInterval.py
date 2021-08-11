import numpy as np
from Indicators.LocalExtremum import localExtremum
from AlgorithmFactory.AlgorithmPackages.SimpleIdea.SimpleIdeaPkg import simple_idea


def Forecasting_Interval(symbol, data, winExtermum, winSimpleIdea):
    time = np.array([d['GMT'] for d in data])
    open = np.array([d['open'] for d in data])
    high = np.array([d['high'] for d in data])
    low = np.array([d['low'] for d in data])
    close = np.array([d['close'] for d in data])

    a = np.c_[open, close].max(1)
    b = np.c_[open, close].min(1)

    # find extremum
    # [localMin, localMax] = LocalExtremum(Data)
    [localMin, localMax] = localExtremum(data, winExtermum)
    # call simple idea or any Buy or sell algorithm
    winDec = 3
    winInc = 3
    [sellIdx, sell, buyIdx, buy] = simple_idea(symbol, data, winSimpleIdea, winSimpleIdea, 0, 0, 1, 0)

    # predict latest candles based on regression line
    # find which situation happen for the latest signal.it was buy or sell

    if sellIdx[-1] >= buyIdx[-1]:
        latesIdx = sellIdx[-1]
        latestMode = 'sell'
        preLatestIdx = localMax[np.nonzero(localMax < latesIdx)[0][0]]
        x = np.arange(preLatestIdx,len(data))
        yOpen = a[x]
        yClose = b[x]
        yHigh = high[x]
        yLow = low[x]
    else:
        latesIdx = buyIdx[-1]
        latestMode = 'buy'
        preLatestIdx = localMin(np.nonzero(localMin < latesIdx)[0][0])
        x = np.arange(preLatestIdx, len(data))
        yOpen = b[x]
        yClose = a[x]
        yHigh = high[x]
        yLow = low[x]
    # --------- regression on the latest candles
    # x = (preLatestIdx:height(Data))';
    # yOpen = a(x);
    # yClose = b(x);
    # yHigh = Data.High(x);
    # yLow = Data.Low(x);

    fitDegree = 1
    pOpen = np.polyfit(x, yOpen, fitDegree)
    pClose = np.polyfit(x, yClose, fitDegree)
    pHigh = np.polyfit(x, yHigh, fitDegree)
    pLow = np.polyfit(x, yLow, fitDegree)

    lineOpen = np.polyval(pOpen, x)
    lineClose = np.polyval(pClose, x)
    lineHigh = np.polyval(pHigh, x)
    lineLow = np.polyval(pLow, x)

    mode = 'ShiftedCandle' # Normal SameClose ShiftedCandle

    if mode == 'SameClose':
        forecastOpen = close[-1]
        forecastClose = np.polyval(pClose, x[-1] + 1)
        forecastHigh = np.polyval(pHigh, x[-1] + 1)
        forecastLow = np.polyval(pLow, x[-1] + 1)

        if forecastClose < forecastOpen and forecastHigh < forecastOpen:
            tmp = forecastHigh
            forecastHigh = forecastOpen
            forecastOpen = tmp
        if forecastClose < forecastOpen and forecastLow > forecastClose:
            tmp = forecastLow
            forecastLow = forecastClose
            forecastClose = tmp

        if forecastClose > forecastOpen and forecastHigh < forecastClose:
            tmp = forecastHigh
            forecastHigh = forecastClose
            forecastClose = tmp
        if forecastClose > forecastOpen and forecastLow > forecastOpen:
            tmp = forecastLow
            forecastLow = forecastOpen
            forecastOpen = tmp

    elif mode == 'Normal':
        forecastOpen = np.polyval(pOpen, x[-1] + 1)
        forecastClose = np.polyval(pClose, x[-1] + 1)
        forecastHigh = np.polyval(pHigh, x[-1] + 1)
        forecastLow = np.polyval(pLow, x[-1] + 1)

        if forecastClose < forecastOpen and forecastHigh < forecastOpen:
            tmp = forecastHigh
            forecastHigh = forecastOpen
            forecastOpen = tmp
        if forecastClose < forecastOpen and forecastLow > forecastClose:
            tmp = forecastLow
            forecastLow = forecastClose
            forecastClose = tmp

        if forecastClose > forecastOpen and forecastHigh < forecastClose:
            tmp = forecastHigh
            forecastHigh = forecastClose
            forecastClose = tmp
        if forecastClose > forecastOpen and forecastLow > forecastOpen:
            tmp = forecastLow
            forecastLow = forecastOpen
            forecastOpen = tmp

    elif mode == 'ShiftedCandle':
        forecastOpen = np.polyval(pOpen, x[-1] + 1)
        forecastClose = np.polyval(pClose, x[-1] + 1)
        forecastHigh = np.polyval(pHigh, x[-1] + 1)
        forecastLow = np.polyval(pLow, x[-1] + 1)

        if forecastClose < forecastOpen and forecastHigh < forecastOpen:
            tmp = forecastHigh
            forecastHigh = forecastOpen
            forecastOpen = tmp
        if forecastClose < forecastOpen and forecastLow > forecastClose:
            tmp = forecastLow
            forecastLow = forecastClose
            forecastClose = tmp
        if forecastClose > forecastOpen and forecastHigh < forecastClose:
            tmp = forecastHigh
            forecastHigh = forecastClose
            forecastClose = tmp
        if forecastClose > forecastOpen and forecastLow > forecastOpen:
            tmp = forecastLow
            forecastLow = forecastOpen
            forecastOpen = tmp

        shiftVal = (close[-1] - forecastOpen)

        forecastOpen = forecastOpen + shiftVal
        forecastClose = forecastClose + shiftVal
        forecastHigh = forecastHigh + shiftVal
        forecastLow = forecastLow + shiftVal

    # append forecast candle
    uniqueTime = np.unique(np.diff(time))
    Sum = np.zeros(len(uniqueTime))
    for i in range(len(uniqueTime)):
        Sum[i] = sum(np.diff(time) == uniqueTime[i])

    [_, idx] = max(Sum)
    Duration = uniqueTime[idx]

    forecastData = {}
    forecastData['Open'] = forecastOpen
    forecastData['Close'] = forecastClose
    forecastData['High'] = forecastHigh
    forecastData['Low'] = forecastLow
    forecastData['Time'] = time[-1] + Duration

    # Duration = min(diff(Data.Time))
    #
    # [~, idx] = min(diff(Data.Time))
    # [a, b] = histcounts(diff(Data.Time));
    # [~, idx] = max(a);
    # histcounts(edges)
    # edges(idx) + (edges(2) - edges(1)) / 3;
