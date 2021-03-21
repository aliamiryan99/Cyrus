import numpy as np

def divergence_predict(a, b, low, high, indicator, local_min_price_left, local_min_price_right, local_max_price_left, local_max_price_right,
                       local_min_indicator_left, local_min_indicator_right, local_max_indicator_left, local_max_indicator_right, hidden_divergence_check_window,
                        pip_difference, upper_line_tr):
    # --- bullish divergence
    trend_direction = 1
    down_direction = 0
    [idx1, val1] = divergence_calculation(b, low, indicator, local_min_price_left, local_min_price_right, local_min_indicator_left,
                              local_min_indicator_right, hidden_divergence_check_window, down_direction, trend_direction,
                              pip_difference, upper_line_tr)

    trend_direction = 1
    down_direction = 1
    [idx2, val2] = divergence_calculation(b, low, indicator, local_min_price_left, local_min_price_right, local_min_indicator_left,
                              local_min_indicator_right, hidden_divergence_check_window, down_direction, trend_direction,
                              pip_difference, upper_line_tr)

    # --- bearish divergence
    trend_direction = 0
    down_direction = 0
    [idx3, val3] = divergence_calculation(a, high, indicator, local_max_price_left, local_max_price_right, local_max_indicator_left,
                              local_max_indicator_right, hidden_divergence_check_window, down_direction, trend_direction,
                              pip_difference, upper_line_tr)

    trend_direction = 0
    down_direction = 1
    [idx4, val4] = divergence_calculation(a, high, indicator, local_max_price_left, local_max_price_right, local_max_indicator_left,
                              local_max_indicator_right, hidden_divergence_check_window, down_direction, trend_direction,
                              pip_difference, upper_line_tr)

    if idx1[-1] == len(a) - 1 or idx2[-1] == len(a) - 1:
        return 1
    elif idx3[-1] == len(a) - 1 or idx4[-1] == len(a) - 1:
        return -1
    else:
        return 0


def divergence_calculation(ab, price, indicator, local_extremum_price_left, local_extremum_price_right,
                       local_extremum_indicator_left, local_extremum_indicator_right, hidden_divergence_check_window,
                       down_direction, trend_direction, pip_difference, upper_line_tr):

    idx = []
    val = []
    localExtremumRng = range(0)
    for i in range(len(local_extremum_price_left)):
        # check existance of window number of local extremum of left local extrumum candles
        tmp = np.nonzero(local_extremum_price_right > local_extremum_price_left(i))[0]
        if len(tmp) != 0:
            tmp = tmp[0]
            if tmp + hidden_divergence_check_window <= len(local_extremum_price_right):
                localExtremumRng = range(tmp,tmp + hidden_divergence_check_window + 1)
            else:
                localExtremumRng = range(tmp, len(local_extremum_price_right + 1))
            isCondToSerach = True
        else:
            isCondToSerach = False

        for j in localExtremumRng:
            # check the local min price of left is lower than right
            if trend_direction:
                # the Bullish Divergence
                if down_direction:
                    if isCondToSerach and (price[local_extremum_price_left[i]] - price[local_extremum_price_right[j]]) > pip_difference:
                        isPriceHasDiff = True
                    else:
                        isPriceHasDiff = False
                else:
                    if isCondToSerach and (price[local_extremum_price_right[j]] - price[local_extremum_price_left[i]]) > pip_difference:
                        isPriceHasDiff = True
                    else:
                        isPriceHasDiff = False
            else:
                # the Bearish Divergence
                if down_direction:
                    if isCondToSerach and (price[local_extremum_price_left[i]] - price[local_extremum_price_right[j]]) > pip_difference:
                        isPriceHasDiff = True
                    else:
                        isPriceHasDiff = False
                else:
                    if isCondToSerach and (price[local_extremum_price_right[j]] - price[local_extremum_price_left[i]]) > pip_difference:
                        isPriceHasDiff = True
                    else:
                        isPriceHasDiff = False


            # draw the line between two local min to see all of candles are above the line
            if isPriceHasDiff:
                x = np.array([local_extremum_price_left[i], local_extremum_price_right[j]])
                y = price(x)
                p = np.polyfit(x, y, 1)
                l = np.polyval(p, np.arange(x[0],x[1]))

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
                p = np.polyfit(Xindc,indicator(Xindc),1)
                l = np.polyval(p, np.arange(Xindc[0],Xindc[1]))
                # the Bullish Divergence
                if trend_direction:
                    if down_direction:
                        if sum(indicator[Xindc[0]: Xindc[1]] > l) > upper_line_tr * l.size and indicator[Xindc[0]] < indicator[Xindc[1]]:
                            isIndicatorHasALLCond = True
                        else:
                            isIndicatorHasALLCond = False
                    else:
                        if sum(indicator[Xindc[0]: Xindc[1]] > l) > upper_line_tr * l.size and indicator[Xindc[0]] > indicator[Xindc[1]]:
                            isIndicatorHasALLCond = True
                        else:
                            isIndicatorHasALLCond = False

                # the Bearish Divergence
                else:
                    if down_direction:
                        if sum(indicator[Xindc[0]: Xindc[1]] < l) > upper_line_tr * l.size and indicator[Xindc[0]] < indicator[Xindc[1]]:
                            isIndicatorHasALLCond = True
                        else:
                            isIndicatorHasALLCond = False
                    else:
                        if sum(indicator[Xindc[0]: Xindc[1]] < l) > upper_line_tr * l.size and indicator(Xindc[0]) > indicator(Xindc[1]):
                            isIndicatorHasALLCond = True
                        else:
                            isIndicatorHasALLCond = False
            else:
                isIndicatorHasALLCond = False

            if isPriceHasALLCond and isIndicatorHasALLCond:
                idx.append(np.array([x, Xindc]))
                val.append(np.array([price[x], indicator[Xindc]]))
    return idx, val

