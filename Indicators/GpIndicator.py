
import pandas as pd
import numpy as np
import GPy

# Main function: it tries to predict High and Low of a next candle based on a higher and lower time frame!
# The main time frame is hourly, higher time frame is 4 hours and lower time frame is 5 min.
# All of them are based on Volume Bars.


class GpIndicator:

    def __init__(self, prediction_multiplayer, deal_rate_enable):
        self.prediction_multiplayer = prediction_multiplayer

        # Kernel parameters
        self.sigmaMin = 0.0005
        self.sigmaInit = 0.0003
        self.deal_rate_enable = deal_rate_enable

        self.days_from_st = 0

        nStep = int(24*60*60/30)

        self.seconds2nextVBfastCandle = np.zeros(nStep, dtype=float)

    def update(self, is_new_week, is_new_day, totalFastData, slowData, targetData, fastData, slowObs, targetObs,
               target_predict_data, slow_predict_data, predict_num):
        # initialization part

        # nayaghini dar GP
        if self.deal_rate_enable:
            if is_new_day:
                self.days_from_st = self.days_from_st + 1
            if is_new_week:
                if self.days_from_st >= 5:
                    self.seconds2nextVBfastCandle = dealRate(totalFastData, 5, 30)
                elif self.days_from_st <= 2:
                    xpred = fastData[-1]['CandleXCenter'] + self.prediction_multiplayer * (
                                fastData[-1]['CandleXCenter'] - fastData[-2]['CandleXCenter'])
                elif self.days_from_st < 5:
                    self.seconds2nextVBfastCandle = dealRate(totalFastData, self.days_from_st, 30)
            else:
                xpred = fastData[-1]['CandleXCenter'] + self.prediction_multiplayer * (
                        fastData[-1]['CandleXCenter'] - fastData[-2]['CandleXCenter'])

            if not self.days_from_st <= 2:
                xPredInc = self.seconds2nextVBfastCandle[
                    int(1 + np.mod(np.floor(fastData[-2]['CandleXCenter'] * 60 * 2), 24 * 60 * 60 / 30))]

                xpred = fastData[-1]['CandleXCenter'] + self.prediction_multiplayer * xPredInc
        else:
            xpred = fastData[-1]['CandleXCenter'] + self.prediction_multiplayer * (fastData[-1]['CandleXCenter'] - fastData[-2]['CandleXCenter'])

        #  Slow GP

        # Specify X train and Y train

        kern1 = GPy.kern.Matern52(1, self.sigmaInit, 0.03)
        kern2 = GPy.kern.Matern52(1, self.sigmaInit, 0.03)
        kern3 = GPy.kern.Matern52(1, self.sigmaInit, 0.03)
        slowXtrain = np.array([[item['CandleXCenter'],] for item in slowObs])  # slowData.CandleX[i:i+wind.SlowWindow[0]-1,None]
        slowYtrain = np.array([[item['WAP'],] for item in slowObs])  # slowData.WAP[i:i+wind.SlowWindow[0]-1,None]

        # GP initialization and GP learning part

        # pp = np.random.randn(35,1)*0.005
        fitSlowWAP = GPy.models.GPRegression(slowXtrain, slowYtrain, kern1)

        fitSlowWAP.optimize()

        # Interpolation Part based on Slow Data

        [slowWAPInterpolate, slowStdInterpolate, slowXInterpolate] = GP_VB_Interpolator(slow_predict_data, self.sigmaMin,
                                                                                               self.sigmaInit, fitSlowWAP)

        # Prediction

        # generating array for prediction
        predArray = np.reshape(
            np.linspace(np.array([[fastData[-1]['CandleXCenter']]]), xpred, num=predict_num, endpoint=True), [predict_num, 1])
        newX = np.hstack([np.zeros_like(predArray)])
        # prediction part

        [slowPredWAP, slowStdWAP] = fitSlowWAP.predict(predArray,
                                                       Y_metadata={'output_index': newX[:, None].astype(int)})

        #  Target GP

        # Specify X train and Y train

        targetXtrain = np.array([[item['CandleXCenter'],] for item in targetObs])  # slowData.CandleX[i:i+wind.SlowWindow[0]-1,None]
        targetYtrain = np.array([[item['WAP'],] for item in targetObs])  # slowData.WAP[i:i+wind.SlowWindow[0]-1,None]

        # GP initialization and GP learning part

        fitTargetWAP = GPy.models.GPRegression(targetXtrain, targetYtrain, kern2)

        fitTargetWAP.optimize()

        # Interpolation Part based on Target Data

        [targetWAPInterpolate, targetStdInterpolate, targetXInterpolate] = GP_VB_Interpolator(
            target_predict_data, self.sigmaMin, self.sigmaInit, fitTargetWAP)
        [targetPredWAP, targetStdWAP] = fitTargetWAP.predict(predArray, Y_metadata={
            'output_index': newX[:, None].astype(int)})

        #  Fast GP

        # Specify X train and Y train

        fastXtrain = np.array([[item['CandleXCenter'],] for item in fastData])  # slowData.CandleX[i:i+wind.SlowWindow[0]-1,None]
        fastYtrain = np.array([[item['WAP'],] for item in fastData])  # slowData.WAP[i:i+wind.SlowWindow[0]-1,None]

        # GP initialization and GP learning part

        fitFastWAP = GPy.models.GPRegression(fastXtrain, fastYtrain, kern3)

        fitFastWAP.optimize()

        # Interpolation Part based on Target Data

        [fastWAPInterpolate, fastStdInterpolate, fastXInterpolate] = GP_VB_Interpolator(
            fastData, self.sigmaMin, self.sigmaInit, fitFastWAP)
        [fastPredWAP, fastStdWAP] = fitFastWAP.predict(predArray, Y_metadata={
            'output_index': newX[:, None].astype(int)})

        return fastPredWAP, fastStdWAP, fastWAPInterpolate, fastStdInterpolate, targetPredWAP, targetStdWAP,\
                targetWAPInterpolate, targetStdInterpolate, slowPredWAP, slowStdWAP, slowWAPInterpolate, slowStdInterpolate, xpred


def dealRate(fastData, k, nSec):
    fastData = pd.DataFrame(fastData)
    nStep = int(24 * 60 * 60 / nSec)
    xPred = np.zeros(nStep, dtype=float)
    diffData = fastData.Time - fastData.Time[0]
    fastDuration = (diffData.dt.total_seconds() / 3600).diff()
    fastDuration = fastDuration.dropna()
    fastDuration.reset_index(drop=True, inplace=True)
    idx = np.empty(k + 2, dtype=int)
    idx[0] = 0

    for i in list(range(1, k + 2)):
        d = (fastData.Time[idx[i - 1]]).day
        m = (fastData.Time[idx[i - 1]]).month
        y = (fastData.Time[idx[i - 1]]).year

        condition1 = ((fastData.Time).dt.day > d) & ((fastData.Time).dt.month == m) & ((fastData.Time).dt.year == y)
        condition2 = ((fastData.Time).dt.month > m) & ((fastData.Time).dt.year == y)
        condition3 = ((fastData.Time).dt.year > y)

        satisfied_conditions = (condition1 | condition2 | condition3)
        idx[i] = (satisfied_conditions.to_numpy().nonzero())[0][0]


    for i in list(range(nStep - 1)):
        ii = [None] * 6
        s = np.mod(i * nSec, 60)
        m = np.mod(np.floor(i * nSec / 60), 60)
        h = np.floor(i * nSec / 3600)
        for j in list(range(1, k + 1)):
            fast = fastData.loc[idx[j]:idx[j + 1], 'Time']
            c1 = fast.dt.hour > h
            c2 = (fast.dt.minute > m) & (fast.dt.hour == h)
            c3 = (fast.dt.second > s) & (fast.dt.minute == m) & (fast.dt.hour == h)
            temp = (c1 | c2 | c3)
            tmp = temp.to_numpy().nonzero()
            if len(tmp) > 0 and len(tmp[0]) > 0:
                tmp = tmp[0][0]
            else:
                tmp = idx[j + 1] - idx[j]

            ii[j] = idx[j] + tmp

        del ii[0]
        tmp = fastDuration[ii]
        xPred[i] = np.mean(tmp[tmp <= 12])

    return xPred


def GP_VB_Interpolator(dataVB, sigmaMin, sigmaInit, trained_model):

    # initialization part
    subDivFactor = 1
    ypredVB = np.zeros((len(dataVB) * subDivFactor,))
    ystVB = ypredVB
    xpred = ypredVB
    wind = len(dataVB)
    extrapolateFactor = 0.5

    # bulid interpolation array

    for i in list(range(wind - 1)):
        xx = np.linspace(dataVB[i]['CandleXCenter'], dataVB[i + 1]['CandleXCenter'], subDivFactor + 1)
        xpred[i * subDivFactor: (i + 1) * subDivFactor] = xx[0:-1]

    xx = np.linspace(dataVB[wind - 1]['CandleXCenter'],
                     (2 + extrapolateFactor) * dataVB[wind - 1]['CandleXCenter'] - (1 + extrapolateFactor) *
                     dataVB[wind - 2]['CandleXCenter'], subDivFactor + 1)
    xpred[(wind - 1) * subDivFactor: wind * subDivFactor] = xx[0:-1]

    # train a GP modle for interpolation

    # prediction part

    xPredict = np.array([(xpred)[:]]).T
    [ypredVB, ystVB] = trained_model.predict(xPredict, Y_metadata={'output_index': np.zeros((1, 1))[:, None].astype(int)})

    return ypredVB, ystVB, xpred