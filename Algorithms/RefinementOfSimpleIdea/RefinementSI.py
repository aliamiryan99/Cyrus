
def refinement_si(window, win_inc, win_dec, pivot, price_mode, alpha):
    # %% -------- find Top and ciel value of each candle
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

    price_up = [row['High'] for row in window]
    price_down = [row['Low'] for row in window]

    if price_mode == 2:
        price_up = top_candle
        price_down = bottom_candle


    # -- check the decreasing trend reversion
    cnt = 0
    for j in range(0, win_dec):
        if top_candle[-j - 2] <= top_candle[-j - 3] or window[-j - 2]['Close'] < window[-j - 2]['Open']:
            cnt += 1
    limit_price = price_up[-pivot-1]
    if price_mode == 3:
        limit_price = bottom_candle[-2] + (top_candle[-2] - bottom_candle[-2]) * alpha
    if cnt == win_dec and price_up[-1] > limit_price:
        return 1, limit_price

    # -- check the increasing trend reversion
    cnt = 0
    for j in range(0, win_inc):
        if bottom_candle[-j - 2] >= bottom_candle[-j - 3] or window[-j - 2]['Close'] > window[-j - 2]['Open']:
            cnt += 1
    limit_price = price_down[-pivot-1]
    if price_mode == 3:
        limit_price = top_candle[-2] - (top_candle[-2] - bottom_candle[-2]) * alpha
    if cnt == win_inc and price_down[-1] < limit_price:
        return -1, limit_price

    return 0, 0

