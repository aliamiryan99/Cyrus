import numpy as np


def divergence_calculation(ab, price, indicator, local_extremum_price_left, local_extremum_price_right,
                           local_extremum_indicator_left, local_extremum_indicator_right,
                           hidden_divergence_check_window,
                           down_direction, trend_direction, pip_difference, upper_line_tr, real_time):
    idx = []
    val = []
    localExtremumRng = range(0)
    for i in range(len(local_extremum_price_left)):
        # check existance of window number of local extremum of left local extrumum candles
        tmp = np.nonzero(local_extremum_price_right > local_extremum_price_left[i])[0]
        if len(tmp) != 0:
            tmp = tmp[0]
            if tmp + hidden_divergence_check_window <= len(local_extremum_price_right):
                localExtremumRng = range(tmp, tmp + hidden_divergence_check_window)
            else:
                localExtremumRng = range(tmp, len(local_extremum_price_right))
            isCondToSerach = True
        else:
            isCondToSerach = False

        for j in localExtremumRng:
            if real_time and local_extremum_price_right[j] < len(price) - 3:
                continue
            # check the local min price of left is lower than right
            if trend_direction:
                # the Bullish Divergence
                if down_direction:
                    if isCondToSerach and (price[local_extremum_price_left[i]] - price[
                        local_extremum_price_right[j]]) > pip_difference:
                        isPriceHasDiff = True
                    else:
                        isPriceHasDiff = False
                else:
                    if isCondToSerach and (price[local_extremum_price_right[j]] - price[
                        local_extremum_price_left[i]]) > pip_difference:
                        isPriceHasDiff = True
                    else:
                        isPriceHasDiff = False
            else:
                # the Bearish Divergence
                if down_direction:
                    if isCondToSerach and (price[local_extremum_price_left[i]] - price[
                        local_extremum_price_right[j]]) > pip_difference:
                        isPriceHasDiff = True
                    else:
                        isPriceHasDiff = False
                else:
                    if isCondToSerach and (price[local_extremum_price_right[j]] - price[
                        local_extremum_price_left[i]]) > pip_difference:
                        isPriceHasDiff = True
                    else:
                        isPriceHasDiff = False

            # draw the line between two local min to see all of candles are above the line
            if isPriceHasDiff:
                x = np.array([local_extremum_price_left[i], local_extremum_price_right[j]])
                y = price[x]
                p = np.polyfit(x, y, 1)
                l = np.polyval(p, np.arange(x[0], x[1]))

                # the Bullish Divergence
                if trend_direction:
                    if sum(ab[x[0]: x[1]] > l) > upper_line_tr * l.size:
                        isPriceHasALLCond = True
                    else:
                        isPriceHasALLCond = False

                # the Bearish Divergence
                else:
                    if sum(ab[x[0]: x[1]] < l) > upper_line_tr * l.size:
                        isPriceHasALLCond = True
                    else:
                        isPriceHasALLCond = False


            else:
                isPriceHasALLCond = False

            #           ---------  check the Condition of Indicator
            #           check left side of inicator to have an equvalent localextrimum in indicator
            Xindc = [0, 0]
            if isPriceHasALLCond and x[0] in local_extremum_indicator_left:
                Xindc[0] = x[0]
                isFindLeftEqvalentInd = True
            elif isPriceHasALLCond and (x[0] - 1) in local_extremum_indicator_left:
                Xindc[0] = x[0] - 1
                isFindLeftEqvalentInd = True
            elif isPriceHasALLCond and (x[0] - 2) in local_extremum_indicator_left:
                Xindc[0] = x[0] - 2
                isFindLeftEqvalentInd = True
            elif isPriceHasALLCond and (x[0] + 1) in local_extremum_indicator_left:
                Xindc[0] = x[0] + 1
                isFindLeftEqvalentInd = True
            elif isPriceHasALLCond and (x[0] + 2) in local_extremum_indicator_left:
                Xindc[0] = x[0] + 2
                isFindLeftEqvalentInd = True
            else:
                isFindLeftEqvalentInd = False

            # right side equvalent
            if isFindLeftEqvalentInd and (x[1]) in local_extremum_indicator_right:
                Xindc[1] = x[1]
                isFindRightEqvalentInd = True
            elif isFindLeftEqvalentInd and (x[1] - 1) in local_extremum_indicator_right:
                Xindc[1] = x[1] - 1
                isFindRightEqvalentInd = True
            elif isFindLeftEqvalentInd and (x[1] - 2) in local_extremum_indicator_right:
                Xindc[1] = x[1] - 2
                isFindRightEqvalentInd = True
            elif isFindLeftEqvalentInd and (x[1] + 1) in local_extremum_indicator_right:
                Xindc[1] = x[1] + 1
                isFindRightEqvalentInd = True
            elif isFindLeftEqvalentInd and (x[1] + 2) in local_extremum_indicator_right:
                Xindc[1] = x[1] + 2
                isFindRightEqvalentInd = True
            else:
                isFindRightEqvalentInd = False

            if isFindLeftEqvalentInd and isFindRightEqvalentInd:
                p = np.polyfit(Xindc, indicator[Xindc], 1)
                l = np.polyval(p, np.arange(Xindc[0], Xindc[1]))
                # the Bullish Divergence
                if trend_direction:
                    if down_direction:
                        if sum(indicator[Xindc[0]: Xindc[1]] > l) > upper_line_tr * l.size and indicator[Xindc[0]] < \
                                indicator[Xindc[1]]:
                            isIndicatorHasALLCond = True
                        else:
                            isIndicatorHasALLCond = False
                    else:
                        if sum(indicator[Xindc[0]: Xindc[1]] > l) > upper_line_tr * l.size and indicator[Xindc[0]] > \
                                indicator[Xindc[1]]:
                            isIndicatorHasALLCond = True
                        else:
                            isIndicatorHasALLCond = False

                # the Bearish Divergence
                else:
                    if down_direction:
                        if sum(indicator[Xindc[0]: Xindc[1]] < l) > upper_line_tr * l.size and indicator[Xindc[0]] < \
                                indicator[Xindc[1]]:
                            isIndicatorHasALLCond = True
                        else:
                            isIndicatorHasALLCond = False
                    else:
                        if sum(indicator[Xindc[0]: Xindc[1]] < l) > upper_line_tr * l.size and indicator[Xindc[0]] > \
                                indicator[Xindc[1]]:
                            isIndicatorHasALLCond = True
                        else:
                            isIndicatorHasALLCond = False
            else:
                isIndicatorHasALLCond = False

            if isPriceHasALLCond and isIndicatorHasALLCond:
                idx.append(np.array([x, Xindc]))
                val.append(np.array([price[x], indicator[Xindc]]))

    # lines = []

    # end_indexes = []
    # for i in range(len(idx)):
    #     end_indexes.append(idx[i][0][1])
    # end_indexes = np.array(end_indexes)
    # sort_idx = np.argsort(end_indexes)
    # end_indexes = list(end_indexes[sort_idx])
    # idx = list(np.array(idx)[sort_idx])
    # val = list(np.array(val)[sort_idx])
    #
    # for i in range(len(idx)):
    #     index = idx[i]
    #     value = val[i]
    #     lines.append([index[0][0], index[0][1], value[0][0], value[0][1]])
    #
    # scores = []
    # for line in lines:
    #     score = calculate_score(high, low, close, middle, line, 14)
    #     scores.append(score)
    #
    # end_indexes, scores = remove_neighbors(end_indexes, scores, 4)
    #
    # new_scores, new_idx, new_val = [], [], []
    # for i in range(len(scores)):
    #     if scores[i] is not None:
    #         new_scores.append(scores[i])
    #         new_idx.append(idx[i])
    #         new_val.append(val[i])
    # scores, idx, val = new_scores, new_idx, new_val

    return idx, val


def calculate_score(high, low, close, middle, line, look_forward):
    if line[1] + look_forward <= len(close):
        look_forward = line[1] + look_forward
    else:
        return 0

    # evaluation of score 1 and 2

    max_idx = np.argmax(high[line[1] + 1:look_forward + 1]) + line[1] + 1
    max_price = high[max_idx]
    min_idx = np.argmin(low[line[1] + 1:look_forward + 1]) + line[1] + 1
    min_price = low[min_idx]

    in_range_min_price = min(low[line[1] + 1:max_idx + 2])
    in_range_max_price = max(high[line[1] + 1:min_idx + 2])

    if in_range_max_price < close[line[1]]:
        in_range_max_price = close[line[1]]
    if in_range_min_price > close[line[1]]:
        in_range_min_price = close[line[1]]

    a = max_price - close[line[1]]
    b = close[line[1]] - in_range_min_price

    score_max = (a - b) / (a + b)

    a = in_range_max_price - close[line[1]]
    b = close[line[1]] - min_price

    score_min = (a - b) / (a + b)

    score1 = (max_price - close[line[1]]) * score_max / (max_price - min_price)
    score2 = (close[line[1]] - min_price) * score_min / (max_price - min_price)

    # --- sloppe approach score method
    slope = np.diff(middle[line[1]: look_forward])
    slope = slope / (max(slope) + 1)

    n = slope.size
    coeff = exp_coff(n) * slope
    score3 = np.mean(coeff)

    # --- drawdown vs profit
    neg = np.min(low[line[1]: look_forward]) - close[line[1]]
    pos = np.max(high[line[1]: look_forward]) - close[line[1]]
    if abs(neg) > abs(pos) * 2:
        score4 = -0.5
    elif abs(neg) > abs(pos) * 1.5:
        score4 = -0.25
    elif 2 * abs(neg) < abs(pos):
        score4 = 0.5
    elif 1.5 * abs(neg) < abs(pos):
        score4 = 0.25
    else:
        score4 = 0

    # summations of scores
    return score1 + score2 + score3 + score4


def exp_coff(num):
    x = np.arange(1, num + 1)
    return 1 / x ** 0.5
