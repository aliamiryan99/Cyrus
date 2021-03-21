import numpy as np

def forecasting_ParabolicApproach(data):
    open = np.array([d['open'] for d in data])
    close = np.array([d['close'] for d in data])

    a = np.c_[open, close].max(1)
    b = np.c_[open, close].min(1)

    window = 4
    coffLower = [0]*len(data)
    coffUpper = [0]*len(data)
    x, Y, LU, xExtend, LUExtend, y, LD, LDExtend = [], [], [], [], [], [], [], []
    for i in range(window, len(data)):
        # upper bound line
        x.append(np.arange(i - window, i+1, 0.1))
        rng = (np.arange(i - window, i+1))
        Y.append(a[rng])
        c = np.polyfit(rng, Y[i - window], 2)
        LU.append(np.polyval(c, x[i - window]))
        coffUpper[i] = c[0]

        xExtend.append(np.arange(i, i+window+1, 0.1))
        LUExtend.append(np.polyval(c, xExtend[i - window]))

        # Lower bound line
        y.append(b[rng])
        c = np.polyfit(rng, y[i - window], 2)
        LD.append(np.polyval(c, x[i - window]))
        coffLower[i] = c[0]
        LDExtend.append(np.polyval(c, xExtend[i - window]))

    upIdx = np.r_[[0], np.diff(coffUpper) < 0]
    downIdx = np.r_[[0], np.diff(coffLower) >= 0]

    upIdx = np.bool_(upIdx)
    downIdx = np.bool_(downIdx)
    # find Uptrend and down trend

    # -- uptrend
    tr = 4

    detector = np.r_[[0], np.diff(b) > 0]
    detector[open < close] = 1

    idxPosB = np.bool_(detector)
    cumUp = np.zeros(len(idxPosB))
    for i in range(1, len(idxPosB)):
        if idxPosB[i] == 1:
            cnt = 1
            cumUp[i] = cumUp[i-1] + cnt
        else:
            cumUp[i] = 0

    idxPosB = (cumUp >= tr)
    idxUp = np.nonzero(cumUp >= tr)

    # --- downtrend
    detector = np.r_[[0], np.diff(a) > 0]
    detector[open > close] = 1

    idxNegB = np.bool_(detector)
    cumDown = np.zeros(len(idxNegB))
    for i in range(1, len(idxNegB)):
        if idxNegB[i] == 1:
            cnt = 1
            cumDown[i] = cumDown[i-1] + cnt
        else:
            cumDown[i] = 0

    idxNegB = (cumDown >= tr)
    idxDown = np.nonzero(cumDown >= tr)

    # filter results
    sellIdx = np.unique(np.r_[np.nonzero(np.logical_and(idxPosB, upIdx))[0], np.nonzero(np.logical_and(np.r_[[0], idxPosB[:-1]], upIdx))[0]])
    buyIdx = np.unique(np.r_[(np.nonzero(np.logical_and(idxNegB, downIdx)))[0], np.nonzero(np.logical_and(np.r_[[0], idxNegB[:-1]], downIdx))[0]])

    return x, xExtend, LUExtend, LDExtend, buyIdx, sellIdx






