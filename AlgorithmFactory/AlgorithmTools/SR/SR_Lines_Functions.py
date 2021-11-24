import numpy as np
from AlgorithmFactory.AlgorithmTools.SR.Useful_Functions import find_trend_begining_HHLL, local_extrema_sliding_window_maxwinsize, local_extrema_sliding_window
from AlgorithmFactory.AlgorithmTools.SR.Useful_Functions import local_extrema_sliding_window_maxwinsize, local_extrema__of_2vec_sliding_window


def OSR_find_potential_main_complement_lines(data,win_size_half=7,price_type='HL'):

    data_len = len(data['High'])

    if price_type == 'HL':
        d1 = data['High']
        d2 = data['Low']
    elif price_type == 'OC':
        d1 = np.maximum(data['Open'], data['Close'])
        d2 = np.minimum(data['Open'], data['Close'])

    #down trends:
    max_indices = local_extrema_sliding_window(data['High'],win_size_half,consider=False)[1]

    s = len(max_indices)
    #number of trends is number of total permutations of optimas:
    down_trend_lines = np.zeros((int((s*(s-1))/2), 4))
    down_trend_lines[:,-1] = data_len
    #permutate optimas:
    idx = 0
    for i in range(s-1):
        for j in range(i+1,s):
            down_trend_lines[idx,0] = max_indices[i] #x1
            down_trend_lines[idx,1] = d1[max_indices[i]] #y1
            down_trend_lines[idx,2] = (d1[max_indices[j]] - d1[max_indices[i]]) / (max_indices[j] - max_indices[i]) #slope

            idx = idx+1
    
    up_trend_lines_complement = down_trend_lines[np.where(down_trend_lines[:,2] >= 0)[0]]
    down_trend_lines = down_trend_lines[np.where(down_trend_lines[:,2] < 0)[0]]

    #up trends:
    min_indices = local_extrema_sliding_window(data['Low'],win_size_half,consider=False)[0]

    s = len(min_indices)
    #number of trends is number of total permutations of optimas:
    up_trend_lines = np.zeros((int((s*(s-1))/2), 4))
    up_trend_lines[:,-1] = data_len
    #permutate optimas:
    idx = 0
    for i in range(s-1):
        for j in range(i+1,s):
            up_trend_lines[idx,0] = min_indices[i] #x1
            up_trend_lines[idx,1] = d2[min_indices[i]] #y1
            up_trend_lines[idx,2] = (d2[min_indices[j]] - d2[min_indices[i]]) / (min_indices[j] - min_indices[i]) #slope = delta y / delta x

            idx = idx+1
    
    down_trend_lines_complement = up_trend_lines[np.where(up_trend_lines[:,2] <= 0)[0]]
    up_trend_lines = up_trend_lines[np.where(up_trend_lines[:,2] > 0)[0]]

    return up_trend_lines, up_trend_lines_complement, down_trend_lines, down_trend_lines_complement


def OSR_compare_regtrendlineslope_extractedtrendlineslope(data,trendlines,one_pip):
    data_len = len(data['High'])

    #count one_pip digits for rounding slopes:
    rounding_number = len(str(one_pip).split('.')[1])

    scores = np.zeros((trendlines.shape[0]))
    if trendlines[0,2] < 0:
        for i in range(trendlines.shape[0]):
            X = np.linspace(int(data_len - trendlines[i,3]),data_len-1,int(trendlines[i,3])).astype(int)
            Y = data['High'][X]
            coeffs = np.polyfit(X,Y,1)
            Y_reg = np.polyval(coeffs,X)
            scores[i] = np.round(abs(trendlines[i,2] - (Y_reg[1] - Y_reg[0])), rounding_number)
    else:
        for i in range(trendlines.shape[0]):
            X = np.linspace(int(data_len - trendlines[i,3]),data_len-1,int(trendlines[i,3])).astype(int)
            Y = data['Low'][X]
            coeffs = np.polyfit(X,Y,1)
            Y_reg = np.polyval(coeffs,X)
            scores[i] = np.round(abs(trendlines[i,2] - (Y_reg[1] - Y_reg[0])), rounding_number)

    return scores


def OSR_count_touches(data,trendlines,one_pip,win_size_half,price_type):
    alpha = 1 #touch coefficient
    beta = 1.5 #penalty coefficient

    data_len = len(data['High'])
    distance_weights = np.ones((data_len)) #np.linspace(0,data_len-1,data_len) / data_len
    trend_num = trendlines.shape[0]
    #find minutes of TF to calcul touch threshold
    TF_minutes = np.min(data['Time'][1:] - data['Time'][:-1]).total_seconds() / 60
    SR_bound = ((0.6+(1/(1+np.exp(TF_minutes*0.0001)))) * (np.sqrt(1.5*TF_minutes)) * one_pip) /4    
    #calcul candles max and min(a and b)
    data_a = np.maximum(data['Open'], data['Close'])
    data_b = np.minimum(data['Open'], data['Close'])
    #find optimas and their max window
    _,_,max_indices_w, max_wins = local_extrema_sliding_window_maxwinsize(data['High'],win_size_half)
    min_indices_w,min_wins,_,_ = local_extrema_sliding_window_maxwinsize(data['Low'],win_size_half)

    max_weights = np.zeros((data_len))
    max_weights[max_indices_w] = max_wins / max(max_wins)
    max_weights = max_weights + 1
    min_weights = np.zeros((data_len))
    min_weights[min_indices_w] = min_wins / max(min_wins)
    min_weights = min_weights + 1

    optimas_wx = np.zeros((data_len))
    optimas_wn = np.zeros((data_len))

    optimas_wx[max_indices_w] = 1
    optimas_wn[min_indices_w] = 1

    scores = np.zeros((trend_num))
    for i in range(trend_num):
        #calcul line positions:
        X = np.linspace(0,data_len-1,data_len)
        Y_trend_line = (trendlines[i,2] * (X-trendlines[i,0])) + trendlines[i,1] #y = m(x-x1)+y1
        #find touches:
        h_diff = data['High'] - Y_trend_line
        high_touches = abs(h_diff) < SR_bound
        l_diff = data['Low'] - Y_trend_line
        low_touches = abs(l_diff) < SR_bound
        bh_diff = data_a - Y_trend_line
        bodyh_touches = abs(bh_diff) < SR_bound
        bl_diff = data_b - Y_trend_line
        bodyl_touches = abs(bl_diff) < SR_bound

        if price_type == 'L':
            total_touches = np.logical_or(low_touches,bodyl_touches)
            optim_touches_w = np.logical_and(total_touches,optimas_wn) * distance_weights * min_weights
            #penalty:
            penalty = np.sum((h_diff < 0) + (l_diff < 0) + (bh_diff < 0) + (bl_diff < 0) * distance_weights) / data_len

        elif price_type == 'H':
            total_touches = np.logical_or(high_touches,bodyh_touches)
            optim_touches_w = np.logical_and(total_touches,optimas_wx) * distance_weights * max_weights
            #penalty:
            penalty = np.sum((h_diff > 0) + (l_diff > 0) + (bh_diff > 0) + (bl_diff > 0) * distance_weights) / data_len
        else:
            total_touches = np.logical_or(np.logical_or(np.logical_or(low_touches,bodyl_touches), high_touches), bodyh_touches)
            optim_touches_w = np.logical_and(np.logical_or(optimas_wx,optimas_wn)) * distance_weights * ((min_weights + max_weights) / 2)
            #penalty:
            penalty = 0

        score_touch = sum(optim_touches_w)
        scores[i] = (alpha * score_touch) - (beta * penalty)
    
    return scores


def OCH_channel_cross_score(data,channels,win_size_half):
    channel_percentage_for_cross = 0.1
    data_len = len(data['High'])
    channels_num = channels.shape[0]
    if channels_num > 0:
        scores = np.zeros((channels_num))
        if channels[0,3] > 0:
            lower_lines = channels[:,0:3]
            upper_lines = channels[:,3:6]
        elif channels[0,3] < 0:
            lower_lines = channels[:,3:6]
            upper_lines = channels[:,0:3]
        else:
            print('Error in channels slope!!!')
            return
        
        data_a = np.maximum(data['Open'], data['Close'])
        data_b = np.minimum(data['Open'], data['Close'])

        #calcul average distance of optimas:
        _, max_indices = local_extrema_sliding_window(data['High'],win_size_half,False)
        min_indices, _ = local_extrema_sliding_window(data['High'],win_size_half,False)
        optimas_AVG_dist = (sum(max_indices[1:]-max_indices[:-1]) + sum(min_indices[1:]-min_indices[:-1])) / (len(max_indices)+len(min_indices)-2)
        optimas_AVG_dist = round(optimas_AVG_dist)

        tmp11,tmp12 = local_extrema__of_2vec_sliding_window(data['High'],data['Low'],win_size_half,False)
        tmp21,tmp22 = local_extrema__of_2vec_sliding_window(data_a,data_b,win_size_half,False)
        localmin = np.unique(np.concatenate([tmp11,tmp21]))
        localmax = np.unique(np.concatenate([tmp12,tmp22]))

        for i in range(channels_num):
            #find intersection point of lines
            #m1(x-x1)+y1 = m2(x-x2)+y2  => m1x+(y1-m1x1) = m2x+(y2 - m2x2)
            # => x(m1-m2) = (y2-m2x2)-(y1-m1x1) => x = ((y2-m2x2)-(y1-m1x1)) / (m1-m2)
            intersection_idx = ((upper_lines[i,1]-upper_lines[i,2]*upper_lines[i,0]) - (lower_lines[i,1]-lower_lines[i,2]*lower_lines[i,0])) / (lower_lines[i,2] - upper_lines[i,2])
            intersection_idx = np.round(intersection_idx) #this is x!!!!!!!!!!

            #calcul line positions:
            X = np.linspace(0,data_len-1,data_len)
            Y_lower_line = (lower_lines[i,2] * (X-lower_lines[i,0])) + lower_lines[i,1]; #y = m(x-x1)+y1
            Y_upper_line = (upper_lines[i,2] * (X-upper_lines[i,0])) + upper_lines[i,1]; #y = m(x-x1)+y1

            #(touch) calcul channel crosses and touches:
            tmp = np.zeros((data_len))
            optimas_touch = np.zeros((data_len))
            optimas_touch[localmin] = -1
            optimas_touch[localmax] = 1
            for j in range(len(localmin)):
                #take care about intersection area!!!!
                if localmin[j] >= intersection_idx + optimas_AVG_dist or localmin[j] <= intersection_idx - optimas_AVG_dist:
                    channel_width = abs(Y_upper_line[localmin[j]] - Y_lower_line[localmin[j]])
                    if Y_lower_line[localmin[j]] >= (data['Low'][localmin[j]]-(channel_width*channel_percentage_for_cross)) and Y_lower_line[localmin[j]] <= data['High'][localmin[j]]:
                        tmp[localmin[j]] = tmp[localmin[j]] - 2
                        optimas_touch[localmin[j]] = -2
                
            for j in range(len(localmax)):
                #take care about intersection area!!!!
                if localmax[j] >= intersection_idx + optimas_AVG_dist or localmax[j] <= intersection_idx - optimas_AVG_dist:
                    channel_width = abs(Y_upper_line[localmax[j]] - Y_lower_line[localmax[j]])
                    if Y_upper_line[localmax[j]] >= data['Low'][localmax[j]] and Y_upper_line[localmax[j]] <= (data['High'][localmax[j]]+(channel_width*channel_percentage_for_cross)):
                        tmp[localmax[j]] = tmp[localmax[j]] + 1
                        optimas_touch[localmax[j]] = 2
            
            optimas_touch = optimas_touch[np.where(optimas_touch != 0)[0]]
            tmp = tmp[np.where(tmp != 0)[0]]
            tmp = tmp[:-1] + tmp[1:]
            scores[i] = sum(np.logical_and(tmp <= 0, tmp >= -3))

        return scores, optimas_touch


def OCH_AreaOfTrendLinesAndPrice_score(data,channels,price_type='AB-mid'):
    data_len = len(data['High'])
    channels_num = channels.shape[0]
    if channels_num > 0:
        scores = np.zeros((channels_num))
        if channels[0,3] > 0:
            lower_lines = channels[:,0:3]
            upper_lines = channels[:,3:6]
        elif channels[0,3] < 0:
            lower_lines = channels[:,3:6]
            upper_lines = channels[:,0:3]
        else:
            print('Error in channels slope!!!')
            return

        if price_type == 'AB-mid':
            data_a = np.maximum(data['Open'], data['Close'])
            data_b = np.minimum(data['Open'], data['Close'])
            price = (data_a + data_b) / 2
        elif price_type == 'HL-mid':
            price = (data['High'] + data['Low']) / 2
        else:
            print('Wrong price_type!!!')
            return
        for i in range(channels_num):
            #find intersection point of lines
            #m1(x-x1)+y1 = m2(x-x2)+y2  => m1x+(y1-m1x1) = m2x+(y2 - m2x2)
            # => x(m1-m2) = (y2-m2x2)-(y1-m1x1) => x = ((y2-m2x2)-(y1-m1x1)) / (m1-m2)
            intersection_idx = ((upper_lines[i,1]-upper_lines[i,2]*upper_lines[i,0]) - (lower_lines[i,1]-lower_lines[i,2]*lower_lines[i,0])) / (lower_lines[i,2] - upper_lines[i,2])
            intersection_idx = np.round(intersection_idx) #this is x!!!!!!!!!!
            if intersection_idx >= data_len:
                comparison_start_idx = 1
            else:
                comparison_start_idx = int(max(1,intersection_idx))
            
            #calcul line positions:
            X = np.linspace(0,data_len-1,data_len)
            Y_lower_line = (lower_lines[i,2] * (X-lower_lines[i,0])) + lower_lines[i,1]; #y = m(x-x1)+y1
            Y_upper_line = (upper_lines[i,2] * (X-upper_lines[i,0])) + upper_lines[i,1]; #y = m(x-x1)+y1

            Y_lower_line = Y_lower_line[comparison_start_idx:]
            Y_upper_line = Y_upper_line[comparison_start_idx:]
            p = price[comparison_start_idx:]

            scores[i] = abs(sum(abs(Y_lower_line - p)) - sum(abs(Y_upper_line - p)))
        
        return scores


def Oblique_channel_and_SRLines(data_inp, one_pip):
    #__________________________________________________________________________
    #inputs:
    #data_input is a data sequence
    #data is a dictionary contains 'Time' 'Open' High' 'Low' 'Close' 'Volume' keys which each one is a numpy array
    #one_pip is equal to one pip depend on data (eg 0.0001 for EUR_USD)

    #outputs: line_coordinates, current_lines,current_CH,number_of_prev_candles,trend_flags,break_flags,touch_flags,optimas_touch
    #line_coordinates contains coordinates of start and end of each line. each row 
    #present [start_date, start_price, end_date, end_price] of line (price==0 means nothing found!!)
    #current_lines contains best current lines. first row is main trend line and
    #second row is its complement. cols: (x y slope). it may be zeros if the 
    #line cant be found.
    #current_CH contains current channel. cols: (x y slope x y slope) which
    #1:3 contains main line and 4:6 contains complement.
    #number_of_prev_candles is a number which indicate the number of passed
    #candles by current trend.
    #trend_flags is an array contain flags about trend: vals are 0 or 1
    #cols: (1: uptrend, 2:downtrend, 3:channel broked, 4:channel_touched
    #break_flags contain flags about trend break or cross by price
    #cols: 1: whole candle crossed the channel, 
    #2,3,4,5: channel broke by open,close,high,low price
    #rows: first row is about upper line and 2nd row for lower line
    #touch_flags contain flags about channel touch
    #cols: 1,2,3,4:channel touched by open,close,high,low price) 
    #rows: first row is about upper line and 2nd row for lower line
    #touches and crosses are based on last candle price!!!
    #optimas_touch is a vector contains -1, -2, 1 and 2 for minimum, minimum which
    #touch lower line, maximum and maximum which touch upper line respectively.
    #__________________________________________________________________________
    #Oblique SR params:
    win_size_half = 7

    current_lines = np.zeros((2,3))
    current_CH = np.zeros((6))

    trend_flags = np.zeros((4))
    break_flags = np.zeros((2,5))
    touch_flags = np.zeros((2,4))

    TF_minutes = np.min(data_inp['Time'][1:] - data_inp['Time'][:-1]).total_seconds() / 60
    SR_bound1 = ((0.6+(1/(1+np.exp(TF_minutes*0.0001)))) * (np.sqrt(1.5*TF_minutes)) * one_pip) /2000
    SR_bound2 = ((0.6+(1/(1+np.exp(TF_minutes*0.0001)))) * (np.sqrt(1.5*TF_minutes)) * one_pip)

    #find begining of current trend:
    OCH_prev_candles_dynamic, trend_type, price_fluctuation = find_trend_begining_HHLL(data_inp,win_size_half,SR_bound1,2)
    line_price_diff_thresh = price_fluctuation
    number_of_prev_candles = OCH_prev_candles_dynamic
    OCH_prev_candles_dynamic = int(OCH_prev_candles_dynamic)
    #prepare data:
    data = {}
    data['Time'] = data_inp['Time'][-1*OCH_prev_candles_dynamic:]
    data['Open'] = data_inp['Open'][-1*OCH_prev_candles_dynamic:]
    data['High'] = data_inp['High'][-1*OCH_prev_candles_dynamic:]
    data['Low'] = data_inp['Low'][-1*OCH_prev_candles_dynamic:]
    data['Close'] = data_inp['Close'][-1*OCH_prev_candles_dynamic:]
    data['Volume'] = data_inp['Volume'][-1*OCH_prev_candles_dynamic:]
    #find optimas max window
    _,_,_, max_wins = local_extrema_sliding_window_maxwinsize(data['High'],1)
    _,min_wins,_,_ = local_extrema_sliding_window_maxwinsize(data['Low'],1)
    win_size_half = int(np.round(np.mean(np.concatenate([max_wins, min_wins]))))
    prices = np.array([data['Open'][-1], data['Close'][-1], data['High'][-1], data['Low'][-1]])
    data_len = len(data_inp['High'])
    offset = data_len - OCH_prev_candles_dynamic
    
    if trend_type == -1: #down trend
        trend_flags[1] = 1
        #######################################################################################################################
        #                                                    OSR Lines Part                                                   #
        #######################################################################################################################
        #find potential OSR:
        _, _, down_trend_lines, down_trend_lines_complement = OSR_find_potential_main_complement_lines(data,win_size_half,'HL')
        #filter OSRs:
        #down trends:
        if down_trend_lines.shape[0] > 0:
            trend_lines_score_regslope = OSR_compare_regtrendlineslope_extractedtrendlineslope(data,down_trend_lines,one_pip)
            trend_lines_score_touches = OSR_count_touches(data,down_trend_lines,one_pip,win_size_half,'H')
            down_trend_lines_score = np.zeros((down_trend_lines.shape[0],6)) # 4col for line(x,y,slope,candle_nums) and 2 for scores
            down_trend_lines_score[:,:4] = down_trend_lines
            down_trend_lines_score[:,-2] = trend_lines_score_regslope
            down_trend_lines_score[:,-1] = trend_lines_score_touches
            tmp = np.where(trend_lines_score_regslope < line_price_diff_thresh)[0]
            down_trend_lines_score = down_trend_lines_score[tmp, :]
            if down_trend_lines_score.shape[0] > 0:
                #sort rows:
                ascending_sorted_indices = np.lexsort((down_trend_lines_score[:,-1], down_trend_lines_score[:,-2]*-1)) #sorted based on touch and then slope diff
                descending_sorted_indices = np.flip(ascending_sorted_indices)
                down_trend_lines_score = down_trend_lines_score[descending_sorted_indices, :]

                current_lines[0,:] = down_trend_lines_score[0,:3]
                #set indices based on input data indexing:
                current_lines[0,0] += offset
        
        #down trends complements:
        if down_trend_lines_complement.shape[0] > 0:
            trend_lines_score_regslope = OSR_compare_regtrendlineslope_extractedtrendlineslope(data,down_trend_lines_complement,one_pip)
            trend_lines_score_touches = OSR_count_touches(data,down_trend_lines_complement,one_pip,win_size_half,'L')
            down_trend_lines_complement_score = np.zeros((down_trend_lines_complement.shape[0],6)) # 4col for line(x,y,slope,candle_nums) and 2 for scores
            down_trend_lines_complement_score[:,:4] = down_trend_lines_complement
            down_trend_lines_complement_score[:,-2] = trend_lines_score_regslope
            down_trend_lines_complement_score[:,-1] = trend_lines_score_touches
            tmp = np.where(trend_lines_score_regslope < line_price_diff_thresh)[0]
            down_trend_lines_complement_score = down_trend_lines_complement_score[tmp, :]
            if down_trend_lines_complement_score.shape[0] > 0:
                #sort rows:
                ascending_sorted_indices = np.lexsort((down_trend_lines_complement_score[:,-1], down_trend_lines_complement_score[:,-2]*-1)) #sorted based on touch and then slope diff
                descending_sorted_indices = np.flip(ascending_sorted_indices)
                down_trend_lines_complement_score = down_trend_lines_complement_score[descending_sorted_indices, :]

                current_lines[1,:] = down_trend_lines_complement_score[0,:3]
                #set indices based on input data indexing:
                current_lines[1,0] += offset
        #######################################################################################################################
        #                                           OCH Part (pair of lines!)                                                 #
        #######################################################################################################################
        if down_trend_lines_score.shape[0] > 0 and down_trend_lines_complement_score.shape[0] > 0:
            #channels contain 6 cols:[x1 y1 s1 x2 y2 s2]
            potential_down_channels = np.concatenate([down_trend_lines_score[0,:3], down_trend_lines_complement_score[0,:3]])
            potential_down_channels = potential_down_channels.reshape(-1,6)
            #these are extra computations: (in case of multiple channels are useful. but not here which there is only one CH!):
            down_channels_cross_score, optimas_touch = OCH_channel_cross_score(data,potential_down_channels,win_size_half)
            down_channels_area_score = OCH_AreaOfTrendLinesAndPrice_score(data,potential_down_channels,'AB-mid')
            
            if down_channels_cross_score > 2:
                down_channels_score = np.concatenate([potential_down_channels[0,:], down_channels_cross_score, down_channels_area_score])
                
                X = np.linspace(0,OCH_prev_candles_dynamic-1,OCH_prev_candles_dynamic)
                Y1 = (down_channels_score[2] * (X-down_channels_score[0])) + down_channels_score[1]; #y = m(x-x1)+y1 upper line (main line)
                Y2 = (down_channels_score[5] * (X-down_channels_score[3])) + down_channels_score[4]; #y = m(x-x1)+y1 lower line

                current_CH = down_channels_score[:6]
                #set indices based on input data indexing:
                current_CH[0] += offset
                current_CH[3] += offset
                if data['Low'][-1] > Y1[-1]:
                    trend_flags[2] = 1
                    break_flags[0,0] = 1
                elif data['High'][-1] < Y2[-1]:
                    trend_flags[2] = 1
                    break_flags[1,0] = 1
                
                tmp1 = prices > Y1[-1]
                break_flags[0,1:5] = tmp1*1
                tmp2 = prices < Y2[-1]
                break_flags[1,1:5] = tmp2*1

                tmp1 = abs(prices - Y1[-1]) < SR_bound2
                touch_flags[0,:4] = tmp1*1
                tmp1 = abs(prices - Y2[-1]) < SR_bound2
                touch_flags[1,:4] = tmp2*1
                trend_flags[3] = (sum(sum(touch_flags)) > 0) * 1
    else: #up trend:
        trend_flags[0] = 1
        #######################################################################################################################
        #                                                    OSR Lines Part                                                   #
        #######################################################################################################################
        #find potential OSR:
        up_trend_lines, up_trend_lines_complement, _, _ = OSR_find_potential_main_complement_lines(data,win_size_half,'HL')
        #filter OSRs:
        #down trends:
        if up_trend_lines.shape[0] > 0:
            trend_lines_score_regslope = OSR_compare_regtrendlineslope_extractedtrendlineslope(data,up_trend_lines,one_pip)
            trend_lines_score_touches = OSR_count_touches(data,up_trend_lines,one_pip,win_size_half,'L')
            up_trend_lines_score = np.zeros((up_trend_lines.shape[0],6)) # 4col for line(x,y,slope,candle_nums) and 2 for scores
            up_trend_lines_score[:,:4] = up_trend_lines
            up_trend_lines_score[:,-2] = trend_lines_score_regslope
            up_trend_lines_score[:,-1] = trend_lines_score_touches
            tmp = np.where(trend_lines_score_regslope < line_price_diff_thresh)[0]
            up_trend_lines_score = up_trend_lines_score[tmp, :]
            if up_trend_lines_score.shape[0] > 0:
                #sort rows:
                ascending_sorted_indices = np.lexsort((up_trend_lines_score[:,-1], up_trend_lines_score[:,-2]*-1)) #sorted based on touch and then slope diff
                descending_sorted_indices = np.flip(ascending_sorted_indices)
                up_trend_lines_score = up_trend_lines_score[descending_sorted_indices, :]

                current_lines[0,:] = up_trend_lines_score[0,:3]
                #set indices based on input data indexing:
                current_lines[0,0] += offset
        
        #down trends complements:
        if up_trend_lines_complement.shape[0] > 0:
            trend_lines_score_regslope = OSR_compare_regtrendlineslope_extractedtrendlineslope(data,up_trend_lines_complement,one_pip)
            trend_lines_score_touches = OSR_count_touches(data,up_trend_lines_complement,one_pip,win_size_half,'H')
            up_trend_lines_complement_score = np.zeros((up_trend_lines_complement.shape[0],6)) # 4col for line(x,y,slope,candle_nums) and 2 for scores
            up_trend_lines_complement_score[:,:4] = up_trend_lines_complement
            up_trend_lines_complement_score[:,-2] = trend_lines_score_regslope
            up_trend_lines_complement_score[:,-1] = trend_lines_score_touches
            tmp = np.where(trend_lines_score_regslope < line_price_diff_thresh)[0]
            up_trend_lines_complement_score = up_trend_lines_complement_score[tmp, :]
            if up_trend_lines_complement_score.shape[0] > 0:
                #sort rows:
                ascending_sorted_indices = np.lexsort((up_trend_lines_complement_score[:,-1], up_trend_lines_complement_score[:,-2]*-1)) #sorted based on touch and then slope diff
                descending_sorted_indices = np.flip(ascending_sorted_indices)
                up_trend_lines_complement_score = up_trend_lines_complement_score[descending_sorted_indices, :]

                current_lines[1,:] = up_trend_lines_complement_score[0,:3]
                #set indices based on input data indexing:
                current_lines[1,0] += offset
        #######################################################################################################################
        #                                           OCH Part (pair of lines!)                                                 #
        #######################################################################################################################
        if up_trend_lines_score.shape[0] > 0 and up_trend_lines_complement_score.shape[0] > 0:
            #channels contain 6 cols:[x1 y1 s1 x2 y2 s2]
            potential_up_channels = np.concatenate([up_trend_lines_score[0,:3], up_trend_lines_complement_score[0,:3]])
            potential_up_channels = potential_up_channels.reshape(-1,6)
            #these are extra computations: (in case of multiple channels are useful. but not here which there is only one CH!):
            up_channels_cross_score, optimas_touch = OCH_channel_cross_score(data,potential_up_channels,win_size_half)
            up_channels_area_score = OCH_AreaOfTrendLinesAndPrice_score(data,potential_up_channels,'AB-mid')
            
            if up_channels_cross_score > 2:
                up_channels_score = np.concatenate([potential_up_channels[0,:], up_channels_cross_score, up_channels_area_score])
                
                X = np.linspace(0,OCH_prev_candles_dynamic-1,OCH_prev_candles_dynamic)
                Y1 = (up_channels_score[2] * (X-up_channels_score[0])) + up_channels_score[1]; #y = m(x-x1)+y1 lower line (main line)
                Y2 = (up_channels_score[5] * (X-up_channels_score[3])) + up_channels_score[4]; #y = m(x-x1)+y1 upper line

                current_CH = up_channels_score[:6]
                #set indices based on input data indexing:
                current_CH[0] += offset
                current_CH[3] += offset
                if data['High'][-1] < Y1[-1]:
                    trend_flags[2] = 1
                    break_flags[1,0] = 1
                elif data['Low'][-1] > Y2[-1]:
                    trend_flags[2] = 1
                    break_flags[0,0] = 1
                
                tmp1 = prices < Y1[-1]
                break_flags[1,1:5] = tmp1*1
                tmp2 = prices > Y2[-1]
                break_flags[0,1:5] = tmp2*1
                
                tmp1 = abs(prices - Y1[-1]) < SR_bound2
                touch_flags[1,:4] = tmp1*1
                tmp2 = abs(prices - Y2[-1]) < SR_bound2
                touch_flags[0,:4] = tmp2*1
                trend_flags[3] = (sum(sum(touch_flags)) > 0) * 1

    start_date = data_inp['Time'][offset]
    end_date = data_inp['Time'][-1]
    start_price1 = (current_lines[0,2]*(offset-current_lines[0,0])) + current_lines[0,1]
    end_price1 = (current_lines[0,2]*(data_len-1-current_lines[0,0])) + current_lines[0,1]
    start_price2 = (current_lines[1,2]*(offset-current_lines[1,0])) + current_lines[1,1]
    end_price2 = (current_lines[1,2]*(data_len-1-current_lines[1,0])) + current_lines[1,1]
    
    line_coordinates = np.array([[start_date, start_price1, end_date, end_price1], [start_date, start_price2, end_date, end_price2]])

    return line_coordinates, current_lines,current_CH,number_of_prev_candles,trend_flags,break_flags,touch_flags,optimas_touch





