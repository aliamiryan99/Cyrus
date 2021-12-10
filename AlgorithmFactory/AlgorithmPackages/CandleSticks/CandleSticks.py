

def is_doji(candle, doji_coefficient=10):
    return abs(candle['Close'] - candle['Open']) * doji_coefficient < candle['High'] - candle['Low']


def is_hammer(candle, up_shadow_coefficient=0.5, down_shadow_coefficient=3):
    top = max(candle['Open'], candle['Close'])
    bottom = min(candle['Open'], candle['Close'])
    return (candle['High'] - top) * (1/up_shadow_coefficient) < abs(candle['Open'] - candle['Close']) < (bottom - candle['Low']) * (1/down_shadow_coefficient)


def is_invert_hammer(candle, up_shadow_coefficient=3, down_shadow_coefficient=0.5):
    top = max(candle['Open'], candle['Close'])
    bottom = min(candle['Open'], candle['Close'])
    return (bottom - candle['Low']) * (1 / down_shadow_coefficient) < abs(candle['Open'] - candle['Close']) < (candle['High'] - top) * (1 / up_shadow_coefficient)


def is_engulfing(pre_candle, new_candle):
    if pre_candle['Close'] < pre_candle['Open']:
        if new_candle['Close'] > pre_candle['Open'] and new_candle['High'] > pre_candle['High'] and new_candle['Low'] < pre_candle['Low']:
            return 1
    else:
        if new_candle['Close'] < pre_candle['Open'] and new_candle['High'] > pre_candle['High'] and new_candle['Low'] < pre_candle['Low']:
            return -1
    return 0


def get_candlesticks(data, type):
    detected_list = []
    for i in range(1, len(data)):
        if type == "Doji":
            if is_doji(data[i]):
                detected_list.append({'Time': data[i]['Time'], 'Price': data[i]['Low'], 'Direction': 1})
        elif type == "Hammer":
            if is_hammer(data[i]):
                detected_list.append({'Time': data[i]['Time'], 'Price': data[i]['Low'], 'Direction': 1})
        elif type == "InvertHammer":
            if is_invert_hammer(data[i]):
                detected_list.append({'Time': data[i]['Time'], 'Price': data[i]['Low'], 'Direction': 1})
        elif type == "Engulfing":
            if is_engulfing(data[i-1], data[i]) != 0:
                detected_list.append({'Time': data[i]['Time'], 'Price': data[i]['Low'], 'Direction': is_engulfing(data[i-1], data[i])})
    return detected_list
