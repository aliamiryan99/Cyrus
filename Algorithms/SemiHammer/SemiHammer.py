

def semi_hammer_detect(window, detect_mode, alpha):       # detect mode : 1, ...

    body_length = []
    total_length = []
    for data in window:
        body_length.append(abs(data['Close'] - data['Open']))
        total_length.append(abs(data['High'] - data['Low']))

    win_size = len(window)
    top_candle = [0] * win_size
    bottom_candle = [0] * win_size

    for i in range(0, win_size):
        # store the top/bottom value of all candles
        if window[i]['Open'] > window[i]['Close']:
            top_candle[i] = window[i]['Open']
            bottom_candle[i] = window[i]['Close']
        else:
            top_candle[i] = window[i]['Close']
            bottom_candle[i] = window[i]['Open']

    if detect_mode == 1:
        if bottom_candle[-1] - window[-1]['Low'] > alpha * abs(window[-1]['Close'] - window[-1]['Open']):
            if window[-2]['Close'] < window[-2]['Open']:
                return 1

        if window[-1]['High'] - top_candle[-1] > alpha * abs(window[-1]['Close'] - window[-1]['Open']):
            if window[-2]['Close'] > window[-2]['Open']:
                return -1

    return 0

