

def get_bottom_top(data):
    top_candle = []
    bottom_candle = []

    for i in range(0, len(data)):
        # store the top/bottom value of all candles
        if data[i]['Open'] > data[i]['Close']:
            top_candle.append(data[i]['Open'])
            bottom_candle.append(data[i]['Close'])
        else:
            top_candle.append(data[i]['Close'])
            bottom_candle.append(data[i]['Open'])
    return bottom_candle, top_candle


def get_body_mean(data, window):
    body_mean = 0
    for i in range(1, window+1):
        body_mean += abs(data[-i]['Open'] - data[-1]['Close']) / window
    return body_mean

