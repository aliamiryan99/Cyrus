from Indicators.LocalExtremum import localExtremum
import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline
import copy

def forecastingMultiInterpolation(data):
    s = 2
    step = 10
    e = 50
    stp = {}
    stp['s'] = s
    stp['step'] = step
    stp['e'] = e

    X, XE, XExtend, LUE, LLE = [], [], [], [], []
    for i in range(s,e+1, step):
        [X_v, XE_v, XExtend_v, LUE_v, LLE_v] = interpolation(data, i)
        X.append(X_v)
        XE.append(XE_v)
        XExtend.append(XExtend_v)
        LUE.append(LUE_v)
        LLE.append(LLE_v)

    return stp, X, XE, XExtend, LUE, LLE

def interpolation(data, winSize):
    high = np.array([d['high'] for d in data])
    low = np.array([d['low'] for d in data])

    extendView = 24

    [localMin, localMax] = localExtremum(data, winSize)
    if len(localMin) < 2 or len(localMax) < 2:
        X = []
        XE = []
        LUE = []
        LLE = []
        return

    # interpolation for Upper bound
    xUpper = copy.copy(localMax)
    X = np.arange(0,len(data), 0.1)
    XE = np.arange(0, len(data) + extendView, 0.1)
    XEtend = np.arange(len(data), len(data) + extendView, 0.1)
    yUpper = high[localMax]

    fUpper = InterpolatedUnivariateSpline(xUpper, yUpper)
    fUpper.set_smoothing_factor(0.001)
    LUE = fUpper(XE)

    # Lower Line
    xLower = copy.copy(localMin)
    yLower = low[localMin]
    fLower = InterpolatedUnivariateSpline(xLower, yLower)
    fLower.set_smoothing_factor(0.001)
    LLE = fLower(XE)

    return X, XE, XEtend, LUE, LLE

