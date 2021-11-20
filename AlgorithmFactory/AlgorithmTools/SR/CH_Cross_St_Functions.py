import numpy as np
import pandas as pd

def Check_Candle_power(data,n=2,prev_range=11):
    # __________________________________________________________________________
    # input:
    # data_input is a data sequence
    # data is a dictionary contains 'Time' 'Open' High' 'Low' 'Close' 'Volume' keys which each one is a numpy array
    # n indicates number of candles to be compared with 10 previos of each one.
    # prev_range is the number of prev candles for  comparison + 1 (1 for last candle) (11->10 prev candles)

    # output: power, index
    # power is a float number which indicate the power of last candle against a
    # bunch of (#10) prev candles! power is in range [0 1]
    # the returned power is the maximum of n powers (n -> input)
    # index indicate where the power maximized. in fact it is the number of cnadles to the end.
    # for example if index is 1 -> the last candle maximized the power (data[-1*index])
    # __________________________________________________________________________
    comparison_ratio = np.array([1.5, 2, 3])
    power = 0

    for i in range(n):
        #last candle power:
        idx = -1 - i
        idx2 = -1*prev_range-i
        last_candle_len = abs(data['Open'][idx] - data['Close'][idx])
        candles_len = abs(data['Open'][idx2:idx] - data['Close'][idx2:idx])

        ratio = candles_len / last_candle_len

        # check how much of prev candles are smaller than last candle (based on
        # comparison ration)
        flags1 = (ratio < 1/comparison_ratio[0]) * 1
        flags2 = (ratio < 1/comparison_ratio[1]) * 1
        flags3 = (ratio < 1/comparison_ratio[2]) * 1

        tmp = (sum(flags1) + sum(flags2) + sum(flags3)) / (3 * len(flags1))
        if tmp > power:
            power = tmp
            index = i+1

    return power, index

def Check_last_optima_touch(optimas_touch):
    # __________________________________________________________________________
    # input:
    # optimas_touch is a vector contains -1, -2, 1 and 2 for minimum, minimum which
    # touch lower line, maximum and maximum which touch upper line respectively.
    # more specificaly it is "optimas_touch" output of "Oblique_channel_and_SRLines" function (in SR_Lines)

    # output: score_lower, score_upper
    # score is 1 if last 2 optimas do not touch the line and 0.6 if only last
    # optima do not touch the line.
    # score_lower detrmine score about lower line
    # score_upper detrmine score about upper line
    # __________________________________________________________________________
    score_lower = 0
    score_upper = 0

    min_without_touch = np.where(optimas_touch == -1)[0]
    min_with_touch = np.where(optimas_touch == -2)[0]
    max_without_touch = np.where(optimas_touch == 1)[0]
    max_with_touch = np.where(optimas_touch == 2)[0]

    if len(min_without_touch) > 0 and min_without_touch[-1] > min_with_touch[-1]:
        score_lower = 0.6
        if len(min_without_touch) > 1 and min_without_touch[-2] > min_with_touch[-1]:
            score_lower = 1

    if len(max_without_touch) > 0 and max_without_touch[-1] > max_with_touch[-1]:
        score_upper = 0.6
        if len(max_without_touch) > 1 and max_without_touch[-2] > max_with_touch[-1]:
            score_upper = 1

    return score_lower,score_upper

def Check_consolidation(data,ignoring_candles_num=2,batch_size=7,batch_number=5):
    # __________________________________________________________________________
    # input:
    # data is a data sequence
    # data is a dictionary contains 'Time' 'Open' High' 'Low' 'Close' 'Volume' keys which each one is a numpy array
    # ignoring_candles_num is the number of candles in the end of data to be ignored. In my opinion, it is better to set by using
    # index output of "Check_Candle_power" function.
    # batch_size is the number of participated candles in each calculation (batch_size=7 -> slope of 7 candles)
    # batch_number is number of last batches for calculation in order to caompare with avg of all batches in trend

    # output: score_slope, score_STD
    # score is consolidation score for prev candles of last candle. 
    # (scores calculated based on slope ans standard deviation)
    # score is in range [0,inf] 1 means last batches have same slope or std as trend AVG,
    # score<1 means smaller than trend avg and score>1 means greater than trend AVG.
    # score -> (last batches avg / whole trend avg)
    # __________________________________________________________________________
    

    trend_data = data[:-ignoring_candles_num]
    trend_means = (trend_data['Open'] + trend_data['Close']) / 2 #candle body means

    #slope
    means_slope = abs(trend_means[batch_size:] - trend_means[:-batch_size]) #the slope of all batches
    means_slope_AVG = sum(means_slope) / len(means_slope) #means slope avg of all batches
    last_batches_mean_slope_AVG = sum(means_slope[-batch_number:]) / batch_number

    score_slope = (last_batches_mean_slope_AVG / means_slope_AVG)

    #STD
    df_means = pd.series(trend_means)
    means_STD = df_means.rolling(batch_size).std()
    means_STD = means_STD[batch_size:]
    means_STD_AVG = sum(means_STD) / len(means_STD)
    last_batches_mean_STD_AVG = sum(means_STD[-batch_number:]) / batch_number

    score_STD = (last_batches_mean_STD_AVG / means_STD_AVG)

    return score_slope, score_STD


