import numpy as np
from AlgorithmFactory.AlgorithmTools.SR.Useful_Functions import local_extrema_sliding_window
import zigzag
from scipy.stats import gaussian_kde
from sklearn.cluster import MeanShift
from scipy.signal import find_peaks


def SR_levels_MTF(data_input,one_pip, SR_num=4):
    # __________________________________________________________________________
    #  data_input is a list contains 3 data sequence in different TFs from small to big TF
    #  one_pip indicates the scale of one pip. for instance: 0.0001 in EURUSD
    #  SR_num indicates the number of output data
    # data is a dictionary contains 'Time' 'Open' High' 'Low' 'Close' 'Volume' keys which each one is a numpy array

    # output is a numpy array. each row is an SR level with cols:[score, price]
    # __________________________________________________________________________

    TF_minutes = np.min(data_input[0]['Time'][1:] - data_input[0]['Time'][:-1]).total_seconds() / 60
    SR_distniction_bound = (50 + np.sqrt(40*TF_minutes)) * one_pip

    SR_limit = SR_distniction_bound * (SR_num+1)
    SR_selected = np.zeros([SR_num,2])

    current_price = data_input[0]['Close'][-1]
    SR_up_limit = current_price + SR_limit
    SR_down_limit = current_price - SR_limit
    up_down_limit_diff = int(round((SR_up_limit - SR_down_limit) * 1/one_pip))
    scores = np.zeros([up_down_limit_diff, 3])

    for i in range(3):
        data = data_input[i]
        TF_minutes = np.min(data['Time'][1:] - data['Time'][:-1]).total_seconds() / 60
        SR_bound = (0.6+(1/(1+np.exp(TF_minutes*0.0001)))) * (np.sqrt(1.5*TF_minutes)) * one_pip

        data_a = np.maximum(data['Open'], data['Close'])
        data_b = np.minimum(data['Open'], data['Close'])

        for j in range(up_down_limit_diff):
            level_price = SR_down_limit + (j+1) * one_pip

            la = level_price - data_a
            lb = level_price - data_b
            ################################################################
            scores[j,0] -= np.sum(np.logical_and(la < 0, lb > 0))
            scores[j,0] += np.sum(np.logical_and(la > 0, lb < SR_bound)) + np.sum(np.logical_and(lb < 0, lb > (SR_bound*-1)))
            ################################################################

    scores[:, 1] = (np.linspace(1,up_down_limit_diff,up_down_limit_diff) * one_pip) + SR_down_limit #prices of levels
    scores[:, 2] = abs(scores[:, 1] - current_price) #distances of levels to current price

    ascending_sorted_indices = np.lexsort((scores[:,2], scores[:,0])) #sorted based on score and then price distance
    descending_sorted_indices = np.flip(ascending_sorted_indices)
    scores = scores[descending_sorted_indices, :]

    counter = 0
    for i in range(up_down_limit_diff):
        selection_permiss = True
        candid = scores[i,0:2]
        for j in range(counter):
            if np.abs(candid[1] - SR_selected[j,1]) < SR_distniction_bound:
                selection_permiss = False
                break
        if selection_permiss:
            SR_selected[counter,:] = candid
            counter += 1
        if counter == SR_num:
            break
    SR_selected = SR_selected[:counter, :]
    
    #refine scores:
    SR_selected = SR_selected.reshape(-1,2)
    SR_selected[:,0] = SR_selected[:,0] / sum(SR_selected[:,0])

    return SR_selected


def SR_levels_optima(data_input,one_pip, SR_num=4):
    # __________________________________________________________________________
    #  data_input is a data sequence
    #  one_pip indicates the scale of one pip. for instance: 0.0001 in EURUSD
    #  SR_num indicates the number of output data
    #  data is a dictionary contains 'Time' 'Open' High' 'Low' 'Close' 'Volume' keys which each one is a numpy array

    #  output is a numpy array. each row is an SR level with cols:[score, price]
    # __________________________________________________________________________

    local_extreme_win = 200

    TF_minutes = np.min(data_input['Time'][1:] - data_input['Time'][:-1]).total_seconds() / 60
    SR_distniction_bound = (50 + np.sqrt(40*TF_minutes)) * one_pip
    SR_bound = (0.6+(1/(1+np.exp(TF_minutes*0.0001)))) * (np.sqrt(1.5*TF_minutes)) * one_pip
    SR_limit = SR_distniction_bound * (SR_num+1)
    SR_selected = np.zeros([SR_num,2])

    # data_a = np.maximum(data_input['Open'], data_input['Close'])
    # data_b = np.minimum(data_input['Open'], data_input['Close'])
    data_a = data_input['High']
    data_b = data_input['Low']

    current_price = data_input['Close'][-1]
    SR_up_limit = current_price + SR_limit
    SR_down_limit = current_price - SR_limit

    max_indices = local_extrema_sliding_window(data_a,local_extreme_win)[1]
    min_indices = local_extrema_sliding_window(data_b,local_extreme_win)[0]

    optimas = np.concatenate((data_a[max_indices],data_b[min_indices]))
    optimas_counter = np.zeros((len(optimas)))

    for i in range(len(optimas)):
        optimas_counter[i] = sum(np.logical_and(optimas >= optimas[i] - SR_bound, optimas <= optimas[i] + SR_bound))

    tmp_idx = np.where(np.logical_and(optimas > SR_down_limit, optimas < SR_up_limit))[0]
    scores = np.array([optimas_counter, optimas, np.concatenate((np.linspace(1,len(max_indices),len(max_indices)), np.linspace(1,len(min_indices),len(min_indices))))])
    scores = scores.T
    scores = scores[tmp_idx,:]
    #sort rows:
    ascending_sorted_indices = np.lexsort((scores[:,2], scores[:,0])) #sorted based on score and then price distance
    descending_sorted_indices = np.flip(ascending_sorted_indices)
    scores = scores[descending_sorted_indices, :]

    counter = 0
    for i in range(scores.shape[0]):
        selection_permiss = True
        candid = scores[i,0:2]
        for j in range(counter):
            if abs(candid[1] - SR_selected[j,1]) < SR_distniction_bound:
                selection_permiss = False
                break
        if selection_permiss:
            SR_selected[counter,:] = candid
            counter += 1
        if counter == SR_num:
            break
    SR_selected = SR_selected[:counter, :]

    if counter == 0:
        SR_selected = np.array([[1, 1], [max(data_input['High']), min(data_input['Low'])]])
    
    #refine scores:
    SR_selected = SR_selected.reshape(-1,2)
    SR_selected[:,0] = SR_selected[:,0] / sum(SR_selected[:,0])

    return SR_selected


def SR_Levels_PeaksAndTroughs(data_input,one_pip, SR_num=4):
    # __________________________________________________________________________
    #  data_input is a list contains 3 data sequence in different TFs from small to big TF
    #  one_pip indicates the scale of one pip. for instance: 0.0001 in EURUSD
    #  SR_num indicates the number of output data
    #  data is a dictionary contains 'Time' 'Open' High' 'Low' 'Close' 'Volume' keys which each one is a numpy array

    #  output is a numpy array. each row is an SR level with cols:[score, price]
    # __________________________________________________________________________
    local_extreme_win = 7

    TF_minutes = np.min(data_input[0]['Time'][1:] - data_input[0]['Time'][:-1]).total_seconds() / 60
    SR_distniction_bound = (50 + np.sqrt(40*TF_minutes)) * one_pip
    SR_bound = (0.6+(1/(1+np.exp(TF_minutes*0.0001)))) * (np.sqrt(1.5*TF_minutes)) * one_pip
    SR_limit = SR_distniction_bound * (SR_num+1)
    SR_selected = np.zeros([SR_num,2])

    for i in range(3):
        data = data_input[i]
        # data_a = np.maximum(data['Open'], data['Close'])
        # data_b = np.minimum(data['Open'], data['Close'])
        data_a = data['High']
        data_b = data['Low']

        if i == 0:
            current_price = data['Close'][-1]
            SR_up_limit = current_price + SR_limit
            SR_down_limit = current_price - SR_limit

            max_indices = local_extrema_sliding_window(data_a,local_extreme_win)[1]
            min_indices = local_extrema_sliding_window(data_b,local_extreme_win)[0]

            optimas_tmp = np.concatenate((data_a[max_indices],data_b[min_indices]))
            optimas = np.unique(optimas_tmp)
            optimas_counter = np.zeros((len(optimas)))

            for j in range(len(optimas)):
                optimas_counter[j] = sum(np.logical_and(optimas_tmp >= optimas[j] - SR_bound, optimas_tmp <= optimas[j] + SR_bound))
        else:
            max_indices = local_extrema_sliding_window(data_a,local_extreme_win)[1]
            min_indices = local_extrema_sliding_window(data_b,local_extreme_win)[0]
            for j in range(len(optimas)):
                optimas_counter[j] += sum(np.logical_and(optimas_tmp >= optimas[j] - SR_bound, optimas_tmp <= optimas[j] + SR_bound))

    tmp_idx = np.where(np.logical_and(optimas > SR_down_limit, optimas < SR_up_limit))[0]
    scores = np.array([optimas_counter, optimas])
    scores = scores.T
    scores = scores[tmp_idx,:]
    #sort rows:
    ascending_sorted_indices = np.lexsort((scores[:,1], scores[:,0])) #sorted based on score and then price distance
    descending_sorted_indices = np.flip(ascending_sorted_indices)
    scores = scores[descending_sorted_indices, :]

    counter = 0
    for i in range(scores.shape[0]):
        selection_permiss = True
        candid = scores[i,0:2]
        for j in range(counter):
            if abs(candid[1] - SR_selected[j,1]) < SR_distniction_bound:
                selection_permiss = False
                break
        if selection_permiss:
            SR_selected[counter,:] = candid
            counter += 1
        if counter == SR_num:
            break
    SR_selected = SR_selected[:counter, :]

    #refine scores:
    SR_selected = SR_selected.reshape(-1,2)
    SR_selected[:,0] = SR_selected[:,0] / sum(SR_selected[:,0])

    return SR_selected


def SR_Levels_PDFPeaks(data_input, one_pip, price_type='HL', SR_num=6):
    # __________________________________________________________________________
    #  data_input is a data sequence
    #  one_pip indicates the scale of one pip. for instance: 0.0001 in EURUSD
    #  SR_num indicates the number of output data
    #  price type indicate used price for calculations -> HL OC zigzag
    #  data is a dictionary contains 'Time' 'Open' High' 'Low' 'Close' 'Volume' keys which each one is a numpy array

    #  output is a numpy array. each row is an SR level with cols:[score, price]
    # __________________________________________________________________________

    local_extreme_win = 20
    
    TF_minutes = np.min(data_input['Time'][1:] - data_input['Time'][:-1]).total_seconds() / 60
    SR_distniction_bound = (50 + np.sqrt(40*TF_minutes)) * one_pip
    SR_limit = SR_distniction_bound * (SR_num+1)

    current_price = data_input['Close'][-1]
    SR_up_limit = current_price + SR_limit
    SR_down_limit = current_price - SR_limit

    if price_type == 'HL':
        points = np.concatenate((data_input['High'],data_input['Low']))
    elif price_type == 'OC':
        points = np.concatenate((data_input['Open'],data_input['Close']))
    else:
        mids = (data_input['Low'] + data_input['High']) / 2
        zigzag_idx = zigzag.peak_valley_pivots(mids, 0.0003, -0.0003)
        zigzag_idx = abs(zigzag_idx)
        zigzag_idx = np.where(zigzag_idx == 1)[0]
        points = np.concatenate((data_input['High'][zigzag_idx],data_input['Low'][zigzag_idx]))
    
    points = points[np.where(np.logical_and(points > SR_down_limit, points < SR_up_limit))]
    
    kde = gaussian_kde(points, bw_method='silverman')
    xmesh = np.arange(min(points),max(points),one_pip)
    density = kde.evaluate(xmesh)
    max_indices = local_extrema_sliding_window(density,local_extreme_win)[1]

    SR_selected = np.zeros((len(max_indices),2))
    SR_selected[:,0] = density[max_indices]
    SR_selected[:,1] = xmesh[max_indices]

    #refine scores:
    SR_selected = SR_selected.reshape(-1,2)
    SR_selected[:,0] = SR_selected[:,0] / sum(SR_selected[:,0])

    return SR_selected


def calcul_myapproach_bandwidtth(data, alpha):
    d = abs(data[:-1] - data[1:])
    avg = sum(d)/len(d)
    bandwidth = alpha * (np.std(d) + avg)
    return bandwidth


def SR_Levels_MeanShiftClustering(data_input, one_pip, price_type='HL', SR_num=4,alpha=1):
    # __________________________________________________________________________
    #  data_input is a data sequence
    #  one_pip indicates the scale of one pip. for instance: 0.0001 in EURUSD
    #  SR_num indicates the number of output data
    #  price type indicate used price for calculations -> HL OC zigzag
    #  data is a dictionary contains 'Time' 'Open' High' 'Low' 'Close' 'Volume' keys which each one is a numpy array
    # alpha -> bandwidth param (for calculation)smaller alpha mins more clusters and bigger trurn less clusters

    #  output is a numpy array. each row is an SR level with cols:[score, price]
    # __________________________________________________________________________
    
    TF_minutes = np.min(data_input['Time'][1:] - data_input['Time'][:-1]).total_seconds() / 60
    SR_distniction_bound = (50 + np.sqrt(40*TF_minutes)) * one_pip
    SR_limit = SR_distniction_bound * (SR_num+1)

    current_price = data_input['Close'][-1]
    SR_up_limit = current_price + SR_limit
    SR_down_limit = current_price - SR_limit

    if price_type == 'HL':
        points = np.concatenate((data_input['High'],data_input['Low']))
    elif price_type == 'OC':
        points = np.concatenate((data_input['Open'],data_input['Close']))
    else:
        mids = (data_input['Low'] + data_input['High']) / 2
        zigzag_idx = zigzag.peak_valley_pivots(mids, 0.0005, -0.0005)
        zigzag_idx = abs(zigzag_idx)
        zigzag_idx = np.where(zigzag_idx == 1)[0]
        points = np.concatenate((data_input['High'][zigzag_idx],data_input['Low'][zigzag_idx]))

    bw = calcul_myapproach_bandwidtth(points, alpha)
    MSclustering = MeanShift(bandwidth = bw, cluster_all = False).fit(points.reshape(-1,1))
    clusters_num = max(MSclustering.labels_) + 1 
    scores = np.zeros((clusters_num*2,2))
    for i in range(clusters_num):
        j = i*2
        idx = np.where(MSclustering.labels_ == i)[0]
        scores[j:j+2,0] = len(idx)
        scores[j,1] = max(points[idx])
        scores[j+1,1] = min(points[idx])
    
    SRs = np.unique(scores[:,1])
    unq_sr_num = len(SRs)
    unq_scores = np.zeros((unq_sr_num,2))
    for i in  range(unq_sr_num):
        unq_scores[i,0] = sum(scores[np.where(scores[:,1] == SRs[i])[0],0])
        unq_scores[i,1] = SRs[i]

    in_range_idx = np.where(np.logical_and(unq_scores[:,1] >= SR_down_limit, unq_scores[:,1] <= SR_up_limit))[0]
    unq_scores = unq_scores[in_range_idx,:]
    #sort rows:
    ascending_sorted_indices = np.lexsort((unq_scores[:,1], unq_scores[:,0])) #sorted based on score
    descending_sorted_indices = np.flip(ascending_sorted_indices)
    unq_scores = unq_scores[descending_sorted_indices, :]

    SR_selected = unq_scores[:min(SR_num,len(in_range_idx)),:]
    #refine scores:
    SR_selected = SR_selected.reshape(-1,2)
    SR_selected[:,0] = SR_selected[:,0] / sum(SR_selected[:,0])

    return SR_selected


def SR_Levels_fiboret(data_input):
    # __________________________________________________________________________
    #  data_input is a data sequence
    #  data is a dictionary contains 'Time' 'Open' High' 'Low' 'Close' 'Volume' keys which each one is a numpy array
    
    #  output is a numpy array. each row is an SR level with cols:[score, price]
    # __________________________________________________________________________
    fibo_levels = np.array([0, 0.236, 0.382, 0.5, 0.618, 1])

    h = max(data_input['High'])
    h_idx = np.where(data_input['High'] == h)[0]
    l = max(data_input['Low'])
    l_idx = np.where(data_input['Low'] == l)[0]

    if l_idx < h_idx:
        fibo_lev_price = fibo_levels * (h - l)
        SR_prices = h - fibo_lev_price
    else:
        fibo_lev_price = (1 - fibo_levels) * (h - l)
        SR_prices = l + fibo_lev_price

    SR_selected = np.zeros((len(SR_prices), 2))
    SR_selected[:,0] = 1/len(SR_prices)
    SR_selected[:,1] = SR_prices

    return SR_selected


def Dynamic_SR_levels(data1, data2, data3, one_pip):
    # __________________________________________________________________________
    #  data1, data2 and data3 are data sequences
    #  one_pip indicates the scale of one pip. for instance: 0.0001 in EURUSD
    #  data is a dictionary contains 'Time' 'Open' High' 'Low' 'Close' 'Volume' keys which each one is a numpy array

    #  output is a numpy array. each row is an SR level with cols:[score, price]
    # __________________________________________________________________________
    final_pip_thresh = one_pip * 4
    rounding_number = len(str(one_pip).split('.')[1])

    data_3d = [data1, data2, data3]

    scores_price1 = SR_levels_MTF(data_3d,one_pip)
    scores_price2 = SR_levels_optima(data1,one_pip)
    scores_price3 = SR_Levels_PeaksAndTroughs(data_3d,one_pip)
    scores_price4 = SR_Levels_PDFPeaks(data1, one_pip, price_type='HL')
    scores_price5 = SR_Levels_PDFPeaks(data1, one_pip, price_type='zigzag')
    scores_price6 = SR_Levels_MeanShiftClustering(data1, one_pip, price_type='HL',alpha=3)
    scores_price7 = SR_Levels_MeanShiftClustering(data1, one_pip, price_type='zigzag')
    scores_price8 = SR_Levels_fiboret(data1)
    tot_score_price = np.concatenate([scores_price1, scores_price2, scores_price3, scores_price4, scores_price5, scores_price6, scores_price7, scores_price8])
    tot_score_price[:,1] = np.round(tot_score_price[:,1],rounding_number)

    #sort rows:
    ascending_sorted_indices = np.lexsort((tot_score_price[:,0], tot_score_price[:,1])) #sorted based on price and then score
    descending_sorted_indices = np.flip(ascending_sorted_indices)
    tot_score_price = tot_score_price[descending_sorted_indices, :]

    hann_win_half_size = np.round((10**rounding_number) * np.mean(tot_score_price[:-1,1] - tot_score_price[1:,1]))
    price_vec = np.arange(tot_score_price[-1,1]-((hann_win_half_size+10)*one_pip),tot_score_price[0,1]+((hann_win_half_size+10)*one_pip),one_pip)
    price_vec = np.round(price_vec,rounding_number)
    score_vec = price_vec * 0
    
    for i in range(tot_score_price.shape[0]):
        idx = np.where(price_vec == tot_score_price[i,1])
        score_vec[idx] = tot_score_price[i,0]
    
    score_vec = np.convolve(score_vec,np.hanning(hann_win_half_size*2),mode='same')

    peaks = find_peaks(score_vec)[0]
    SR_selected = np.zeros((len(peaks), 2))
    SR_selected[:,0] = score_vec[peaks]
    SR_selected[:,1] = price_vec[peaks]

    return SR_selected


def Static_SR_levels(data_monthly,root=2,level_degree=5,zone_extra_degree=3,forecast_lines=2):
    # __________________________________________________________________________
    #  data_monthly is alll monthly candles
    #  data is a dictionary contains 'Time' 'Open' High' 'Low' 'Close' 'Volume' keys which each one is a numpy array
    #  root indicates division parameter and each segment will divide by it
    #  level_degree indicates how much division will be applied on data
    #  zone_extra_degree will add to level_degree to calcul zone step
    #  forecast_lines is the number of lines above ATH and below ATL
    
    #  output is a numpy array. each row is an SR level with cols:[score, price]
    #  all output scores are based on levels and smaller value means stronger SR (max(score) is level_degree and min(score) is 0)
    # __________________________________________________________________________
    bot = min(data_monthly['Low'])
    top = max(data_monthly['High'])

    levels_prices = np.zeros((1+root**level_degree,2))

    for i in range(level_degree,-1,-1):
        
        step = (top - bot) / (root**i)
        price = bot
        if i == level_degree:
            idx = 0
            while price <= top:
                levels_prices[idx,1] = price
                levels_prices[idx,0] = i
                price += step
                idx += 1
        else:
            while price <= top:
                tmp = levels_prices[:,1] - price
                tmp = abs(tmp)
                idx = np.where(tmp == min(tmp))
                levels_prices[idx,0] = i
                price += step
    
    top_forecast = np.zeros((forecast_lines,2))
    bot_forecast = np.zeros((forecast_lines,2))
    step = (top - bot) / (root**level_degree)
    top_tmp = top + step
    bot_tmp = bot - (step * forecast_lines)
    for i in range(forecast_lines):
        top_forecast[i,0] = level_degree
        bot_forecast[i,0] = level_degree
        top_forecast[i,1] = top_tmp
        bot_forecast[i,1] = bot_tmp
        top_tmp += step
        bot_tmp += step

    levels_prices = np.concatenate([bot_forecast, levels_prices, top_forecast])

    zone_step = (top - bot) / (root**(level_degree+zone_extra_degree))

    return levels_prices, zone_step




