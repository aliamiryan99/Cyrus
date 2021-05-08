

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
