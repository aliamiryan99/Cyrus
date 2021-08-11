

def candle_trend_detection(data, window_size):
    data_size = len(data)
    top_candle = [0] * data_size
    bottom_candle = [0] * data_size

    for i in range(0, data_size):
        if data[i]['Open'] > data[i]['Close']:
            top_candle[i] = data[i]['Open']
            bottom_candle[i] = data[i]['Close']
        else:
            top_candle[i] = data[i]['Close']
            bottom_candle[i] = data[i]['Open']

    # -- check the decreasing trend reversion
    cnt = 0
    for j in range(0, window_size):
        if (top_candle[- j - 1] <= top_candle[- j - 2]) or (data[- j - 1]['Open'] > data[- j - 1]['Close']):
            cnt += 1
    if cnt == window_size:
        return 1

    # -- check the increasing trend reversion
    cnt = 0
    for j in range(0, window_size):
        if (bottom_candle[- j - 1] >= bottom_candle[- j - 2]) or (data[- j - 1]['Open'] < data[- j - 1]['Close']):
            cnt += 1
    if cnt == window_size:  # it can be replaced by  topCnadle[-2] > topCnadle[-1]:
        return -1

    return 0

