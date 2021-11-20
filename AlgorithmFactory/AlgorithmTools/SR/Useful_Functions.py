import numpy as np


def local_extrema_sliding_window(vector,winsize_half,consider=True):
    #____________________________________________________________________________________
    # vector is a data sequance
    # win_size_half is (window size - 1) / 2 . optimas are compared in a locality with winsize_half values before and after it.
    # if consider=True then:
    # (index=0 and index=len(vector) can be considered as an optima)
    # else function looking for optimas in range vector[winsize_half:-winsize_half]
    
    # return local optimas indices
    #____________________________________________________________________________________
    winsize_half = int(winsize_half)
    len_data = int(len(vector))
    localMax = np.zeros((len_data))
    localMin = np.zeros((len_data))
    if consider:
        val = 0
        for i in range(len_data):
            win_start_idx = max(0,i-winsize_half)
            win_end_idx = min(len_data,i+winsize_half+1)

            if max(vector[win_start_idx:win_end_idx]) == vector[i]:
                localMax[i] = i

            if min(vector[win_start_idx:win_end_idx]) == vector[i]:
                localMin[i] = i
    else:
        for i in range(winsize_half,len_data-winsize_half-1):
            win_start_idx = i-winsize_half
            win_end_idx = i+winsize_half+1

            if max(vector[win_start_idx:win_end_idx]) == vector[i]:
                localMax[i] = i

            if min(vector[win_start_idx:win_end_idx]) == vector[i]:
                localMin[i] = i
    
    tmp = localMax[1:] - localMax[:-1]
    tmp = np.concatenate([np.array([0]),tmp])
    localmax_idx = np.where(tmp > 1)[0]

    tmp = localMin[1:] - localMin[:-1]
    tmp = np.concatenate([np.array([0]),tmp])
    localmin_idx = np.where(tmp > 1)[0]

    return localmin_idx, localmax_idx


def local_extrema__of_2vec_sliding_window(upper_vector,lower_vector,winsize_half,consider=True):
    #____________________________________________________________________________________
    # upper/lower vector are a data sequance with same size (high and low price for example)
    # win_size_half is (window size - 1) / 2 . optimas are compared in a locality with winsize_half values before and after it.
    # if consider=True then:
    # (index=0 and index=len(vector) can be considered as an optima)
    # else function looking for optimas in range vector[winsize_half:-winsize_half]
    
    # return local optimas indices maxes of upper_vector and mins of lower_vector
    #____________________________________________________________________________________
    len_data = len(upper_vector)
    localMax = np.zeros((len_data))
    localMin = np.zeros((len_data))
    if consider:
        val = 0
        for i in range(len_data):
            win_start_idx = max(0,i-winsize_half)
            win_end_idx = min(len_data,i+winsize_half+1)

            if max(upper_vector[win_start_idx:win_end_idx]) == upper_vector[i]:
                localMax[i] = i

            if min(lower_vector[win_start_idx:win_end_idx]) == lower_vector[i]:
                localMin[i] = i
    else:
        for i in range(winsize_half,len_data-winsize_half-1):
            win_start_idx = i-winsize_half
            win_end_idx = i+winsize_half+1

            if max(upper_vector[win_start_idx:win_end_idx]) == upper_vector[i]:
                localMax[i] = i

            if min(lower_vector[win_start_idx:win_end_idx]) == lower_vector[i]:
                localMin[i] = i
    
    tmp = localMax[1:] - localMax[:-1]
    tmp = np.concatenate([np.array([0]),tmp])
    localmax_idx = np.where(tmp > 1)[0]

    tmp = localMin[1:] - localMin[:-1]
    tmp = np.concatenate([np.array([0]),tmp])
    localmin_idx = np.where(tmp > 1)[0]

    return localmin_idx, localmax_idx


def local_extrema_sliding_window_maxwinsize(vector,winsize_half):
    #____________________________________________________________________________________
    # vector is a data sequance
    # win_size_half is (window size - 1) / 2 . optimas are compared in a locality with winsize_half values before and after it.
    # if consider=True then:
    # (index=0 and index=len(vector) can be considered as an optima)
    # else function looking for optimas in range vector[winsize_half:-winsize_half]
    
    # return local optimas indices and max winsize for each optima which it is still optima in that locality
    #____________________________________________________________________________________
    localmin_idx, localmax_idx = local_extrema_sliding_window(vector,winsize_half,consider=False)
    localmax_win = (localmax_idx * 0) + winsize_half
    localmin_win = (localmin_idx * 0) + winsize_half
    len_data = len(vector)

    for i in range(len(localmax_idx)):
        winsize = winsize_half
        while True:
            winsize += 1
            win_start_idx = localmax_idx[i] - winsize
            win_end_idx = localmax_idx[i] + winsize+1
            if win_start_idx >= 0 and win_end_idx <= len_data:
                if max(vector[win_start_idx:win_end_idx]) == vector[localmax_idx[i]]:
                    localmax_win[i] = winsize
                else:
                    break
            else:
                break
    
    for i in range(len(localmin_idx)):
        winsize = winsize_half
        while True:
            winsize += 1
            win_start_idx = localmin_idx[i] - winsize
            win_end_idx = localmin_idx[i] + winsize+1
            if win_start_idx >= 0 and win_end_idx <= len_data:
                if min(vector[win_start_idx:win_end_idx]) == vector[localmin_idx[i]]:
                    localmin_win[i] = winsize
                else:
                    break
            else:
                break
    
    return localmin_idx, localmin_win, localmax_idx, localmax_win


def find_trend_begining_HHLL(data,win_size_half,SR_bound,HHLL_num=2):
    #____________________________________________________________________________________
    # data is a dictionary contains 'Time' 'Open' High' 'Low' 'Close' 'Volume' keys which each one is a numpy array
    # win_size_half is (window size - 1) / 2 . optimas are compared in a locality with winsize_half values before and after it.
    # SR_bound is a price threshold to consider optimas higher or lower
    # HHLL_num is the number of consecutive higher lows/lower highs to detect up/down trend

    # outputs:
    # prev_range is the number of candles which passed from the begining of trend till now
    # length(data)-prev_range is the start index of trend
    # trend_type with value 1 indicates up trend and -1 for downtrend
    # price_fluctuation is the mean of optimas distances divide by 10
    #____________________________________________________________________________________

    #find HH LL for dynamic prev range
    max_indices = local_extrema_sliding_window(data['High'],win_size_half,consider=False)[1]
    min_indices = local_extrema_sliding_window(data['Low'],win_size_half,consider=False)[0]
    optims = np.zeros((len(data['High'])))
    optims[max_indices] = data['High'][max_indices]
    optims[min_indices] = data['Low'][min_indices]
    optims = optims[np.where(optims > 0)[0]]
    optim_diff = abs(optims[:-1] - optims[1:])
    price_fluctuation = np.mean(optim_diff)/10

    #diffs of second optima to last optima (compare to their prev optima)
    H_diff = data['High'][max_indices[1:]] - data['High'][max_indices[:-1]]
    tmp = np.where(abs(H_diff) >= SR_bound)[0]
    H_diff = H_diff[tmp]
    max_indices = max_indices[np.concatenate([np.array([0]), tmp+1])]
    L_diff = data['Low'][min_indices[1:]] - data['Low'][min_indices[:-1]]
    tmp = np.where(abs(L_diff) >= SR_bound)[0]
    L_diff = L_diff[tmp]
    min_indices = min_indices[np.concatenate([np.array([0]), tmp+1])]

    #specify HH LL HL LH: (+1 for higher, -1 for lower, 0 for equal)
    H_diff[np.where(H_diff > 0)[0]] = 1
    H_diff[np.where(H_diff <= 0)[0]] = -1
    #find a sequence of HH LH LH ...
    prev_range_1 = 0
    for i in range(len(H_diff)-1,HHLL_num-1,-1):
        if sum(H_diff[i-HHLL_num+1:i+1]) == -1*HHLL_num:
            if H_diff[i-HHLL_num] == 1:
                prev_range_1 = len(data['High']) - max_indices[i-HHLL_num+1]+win_size_half+1
                break
    
    #specify HH LL HL LH: (+1 for higher, -1 for lower, 0 for equal)
    L_diff[np.where(L_diff > 0)[0]] = 1
    L_diff[np.where(L_diff <= 0)[0]] = -1
    #find a sequence of LL HL HL ...
    prev_range_2 = 0
    for i in range(len(L_diff)-1,HHLL_num-1,-1):
        if sum(L_diff[i-HHLL_num+1:i+1]) == HHLL_num:
            if L_diff[i-HHLL_num] == -1:
                prev_range_2 = len(data['High']) - min_indices[i-HHLL_num+1]+win_size_half+1
                break

    if prev_range_1 < prev_range_2:
        trend_type = -1
        prev_range = prev_range_1
    else:
        trend_type = 1
        prev_range = prev_range_2

    return prev_range, trend_type, price_fluctuation

    a=0




