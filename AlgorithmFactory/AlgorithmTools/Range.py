
from AlgorithmFactory.AlgorithmTools.CandleTools import *


def detect_range_region(data, range_candle_threshold):

    open, high, low , close = get_ohlc(data)
    bottom, top = get_bottom_top(data)

    in_range_candles = 1
    top_region = high[0]
    bottom_region = low[0]

    results = []

    for i in range(1, len(data)):
        if in_range_candles < range_candle_threshold:
            if top[i] < high[i-1] and bottom[i] > low[i-1]:
                in_range_candles += 1
                if high[i] > top_region:
                    top_region = high[i]
                if low[i] < bottom_region:
                    bottom_region = low[i]
            else:
                in_range_candles = 1
                top_region = high[i]
                bottom_region = low[i]
        else:
            if top_region < close[i] or close[i] < bottom_region:
                results.append({'Start': i-in_range_candles, 'End': i, 'BottomRegion': bottom_region, 'TopRegion': top_region})
                in_range_candles = 1
                top_region = high[i]
                bottom_region = low[i]
            else:
                if i == len(data)-1:
                    results.append({'Start': i - in_range_candles, 'End': i, 'BottomRegion': bottom_region, 'TopRegion': top_region})
                in_range_candles += 1
    return results


def get_new_result_index(results, origin_data, target_data):
    new_results = []
    j = 0
    for i in range(len(results)):
        while target_data[j]['Time'] < origin_data[results[i]['Start']]['Time']:
            j += 1
        start = j
        while target_data[j]['Time'] < origin_data[results[i]['End']]['Time']:
            j += 1
        end = j
        new_results.append({'Start': start, 'End': end, 'BottomRegion': results[i]['BottomRegion'], 'TopRegion': results[i]['TopRegion']})
    return new_results


def get_breakouts(data, range_results):
    up_breaks = []
    down_breaks = []
    results_type = []
    marker_activation = False
    result_i = 0
    for i in range(len(data)):
        if result_i != len(range_results) and data[i]['Time'] >= data[range_results[result_i]['End']]['Time']:
            result_i += 1
            marker_activation = True
        if marker_activation:
            if data[i]['Close'] > range_results[result_i - 1]['TopRegion']:
                up_breaks.append(i)
                results_type.append('Up')
                marker_activation = False
            elif data[i]['Close'] < range_results[result_i - 1]['BottomRegion']:
                down_breaks.append(i)
                results_type.append('Down')
                marker_activation = False

    return up_breaks, down_breaks, results_type


def get_breakouts2(data, range_results):
    bottom, top = get_bottom_top(data)
    x = 0
    y = 0
    results = []
    for i in range(len(range_results)):
        break_out_type = 0
        break_out_direction = 0
        mono_result = range_results[i]
        for j in range(mono_result['Start'], mono_result['End']):
            if data[j]['Close'] > mono_result['TopRegion']:
                break_out_direction = 1
                break_out_type = 1
                x = j
                break
            elif data[j]['Close'] < mono_result['BottomRegion']:
                break_out_direction = -1
                break_out_type = 1
                x = j
                break
            elif data[j]['High'] > mono_result['TopRegion']:
                break_out_direction = 1
                break_out_type = 2
                x = j
                break
            elif data[j]['Low'] < mono_result['BottomRegion']:
                break_out_direction = -1
                break_out_type = 2
                x = j
                break
        if break_out_type == 0:
            results.append(None)
        elif break_out_type == 1:
            if break_out_direction == 1:
                start_price = data[x]['Low']
                for j in range(x, len(data)-1):
                    if data[j]['Close'] <= start_price:
                        x = j
                        start_price = data[j]['Close']
                        break
                if x > mono_result['End']:
                    results.append(None)
                    continue
                max_top, min_bottom = top[mono_result['Start']], bottom[mono_result['Start']]
                for j in range(mono_result['Start'], x + 1):
                    max_top = max(max_top, top[j])
                    min_bottom = min(min_bottom, bottom[j])
                stop_price = max_top
                target_price = min_bottom
                for j in range(x+1, len(data)-1):
                    if data[j]['Low'] <= target_price or data[j]['High'] >= stop_price:
                        y = j
                        break
                results.append({'X': x, 'Y': y, 'StartPrice': start_price, 'StopPrice': stop_price, 'TargetPrice': target_price})
            elif break_out_direction == -1:
                start_price = data[x]['High']
                for j in range(x, len(data)-1):
                    if data[j]['Close'] >= start_price:
                        x = j
                        start_price = data[j]['Close']
                        break
                if x > mono_result['End']:
                    results.append(None)
                    continue
                max_top, min_bottom = top[mono_result['Start']], bottom[mono_result['Start']]
                for j in range(mono_result['Start'], x + 1):
                    max_top = max(max_top, top[j])
                    min_bottom = min(min_bottom, bottom[j])
                stop_price = min_bottom
                target_price = max_top
                for j in range(x+1, len(data)-1):
                    if data[j]['High'] >= target_price or data[j]['Low'] <= stop_price:
                        y = j
                        break
                results.append({'X': x, 'Y': y, 'StartPrice': start_price, 'StopPrice': stop_price, 'TargetPrice': target_price})

        elif break_out_type == 2:
            if break_out_direction == 1:
                stop_price = data[x]['High']
                start_price = data[x]['Close']
                target_price = data[mono_result['Start']]['Low']
                for j in range(mono_result['Start'], x+1):
                    target_price = min(target_price, data[j]['Low'])

                for j in range(x+1, len(data)-1):
                    if data[j]['Low'] <= target_price or data[j]['High'] >= stop_price:
                        y = j
                        break
                results.append({'X': x, 'Y': y, 'StartPrice': start_price, 'StopPrice': stop_price, 'TargetPrice': target_price})
            elif break_out_direction == -1:
                stop_price = data[x]['Low']
                start_price = data[x]['Close']
                target_price = data[mono_result['Start']]['High']
                for j in range(mono_result['Start'], x + 1):
                    target_price = max(target_price, data[j]['High'])
                for j in range(x+1, len(data) - 1):
                    if data[j]['High'] >= target_price or data[j]['Low'] <= stop_price:
                        y = j
                        break
                results.append({'X': x, 'Y': y, 'StartPrice': start_price, 'StopPrice': stop_price, 'TargetPrice': target_price})
    return results


def get_proximal_region(data, results):
    bottom, top = get_bottom_top(data)
    for i in range(len(results)):
        max_top = top[results[i]['Start']]
        min_bottom = bottom[results[i]['End']]
        for j in range(results[i]['Start'], results[i]['End']+1):
            max_top = max(max_top, top[j])
            min_bottom = min(min_bottom, bottom[j])
        results[i]['ProximalTop'] = max_top
        results[i]['ProximalBottom'] = min_bottom
