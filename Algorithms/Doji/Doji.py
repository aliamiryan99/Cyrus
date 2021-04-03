

def doji_detect(window, win, detect_mode, candle_mode):

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

    if candle_mode == 1:
        max_body = body_length[-2]
        min_body = body_length[-2]
        for i in range(3, win + 2):
            max_body = max(body_length[-i], max_body)
            min_body = min(body_length[-i], min_body)
    elif candle_mode == -1:
        max_body = total_length[-2]
        min_body = total_length[-2]
        for i in range(3, win + 2):
            max_body = max(total_length[-i], max_body)
            min_body = min(total_length[-i], min_body)
    detection = 0

    if detect_mode == 1:       # High, Low
        cnt = 0
        for i in range(1, win+1):
            if window[-i]['High'] < window[-i-1]['High']:
                cnt += 1
        if cnt == win:
            detection = 1
        cnt = 0
        for i in range(1, win+1):
            if window[-i]['Low'] > window[-i-1]['Low']:
                cnt += 1
        if cnt == win:
            detection = -1
    elif detect_mode == 2:     # Top, Bottom
        cnt = 0
        for i in range(1, win + 1):
            if top_candle[-i] < top_candle[-i - 1]:
                cnt += 1
        if cnt == win:
            detection = 1
        cnt = 0
        for i in range(1, win + 1):
            if bottom_candle[-i] > bottom_candle[-i - 1]:
                cnt += 1
        if cnt == win:
            detection = -1
    elif detect_mode == 3:     # Last Candle
        if body_length[-2] >= max_body:
            if window[-2]['Close'] < window[-2]['Open']:
                detection = 1
            else:
                detection = -1

    if candle_mode == 1:   # body mode
        if body_length[-1] <= min_body:
            return detection

    if candle_mode == 2:   # total mode
        if total_length[-1] <= min_body:
            return detection

    return 0

