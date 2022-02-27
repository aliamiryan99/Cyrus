

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


def is_inside(pre_candle, new_candle):
    if pre_candle['Close'] < pre_candle['Open']:
        if new_candle['Open'] < new_candle['Close'] and new_candle['Close'] < pre_candle['Open'] and new_candle['High'] < pre_candle['High'] and new_candle['Low'] > pre_candle['Low']:
            return 1
    else:
        if new_candle['Open'] > new_candle['Close'] and new_candle['Close'] > pre_candle['Open'] and new_candle['High'] < pre_candle['High'] and new_candle['Low'] > pre_candle['Low']:
            return -1
    return 0


def get_candlesticks(data):
    detected_list = []
    for i in range(1, len(data)):
        type_list = []
        direction_list = []
        if is_doji(data[i]):
            type_list.append("Doji")
            direction_list.append(0)
        if is_hammer(data[i]):
            type_list.append("Hammer")
            direction_list.append(0)
        if is_invert_hammer(data[i]):
            type_list.append("IHammer")
            direction_list.append(0)
        if is_engulfing(data[i-1], data[i]) != 0:
            type_list.append("Engulf")
            direction_list.append(is_engulfing(data[i-1], data[i]))
        if is_inside(data[i-1], data[i]) != 0:
            type_list.append("Inside")
            direction_list.append(is_inside(data[i-1], data[i]))
        if len(type_list) != 0:
            detected_list.append({'Type': type_list, 'Index': i, 'Time': data[i]['Time'], 'Price': data[i]['Low'], 'Directions': direction_list})
    return detected_list
