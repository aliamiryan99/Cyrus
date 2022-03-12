

def detect_trend(max_ext, min_ext, up_price, down_price):
    bullish_start_trends = []
    bearish_start_trends = []
    state = 0
    i, j = 1, 1
    while i < len(max_ext) and j < len(min_ext):
        if max_ext[i] < min_ext[j]:
            if state != 1 and up_price[max_ext[i]] > up_price[max_ext[i-1]]:
                bullish_start_trends.append(max_ext[i])
                state = 1
            i += 1
        else:
            if state != -1 and down_price[min_ext[j]] < down_price[min_ext[j-1]]:
                bearish_start_trends.append(min_ext[j])
                state = -1
            j += 1

    return bullish_start_trends, bearish_start_trends
