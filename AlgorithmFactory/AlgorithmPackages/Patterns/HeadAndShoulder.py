
from AlgorithmFactory.AlgorithmTools.LocalExtermums import get_local_extermums
from AlgorithmFactory.AlgorithmTools.LocalExtermums import find_next_extremum
from AlgorithmFactory.AlgorithmTools.CandleTools import get_body_mean
from AlgorithmFactory.AlgorithmPackages.Patterns.Tools import *


def get_all_head_and_shoulders(data, scales):
    body_mean = get_body_mean(data, len(data))
    double_tops_detected = {}
    double_bottom_detected = {}
    for scale in scales:
        tr = body_mean * (scale / 5)
        min_extremum, max_extremum = get_local_extermums(data, scale, 1)
        double_tops_detected[scale] = get_top_head_and_shoulders(data, max_extremum, min_extremum, tr)
        double_bottom_detected[scale] = get_bottom_head_and_shoulders(data, min_extremum, max_extremum, tr)
    return double_bottom_detected, double_tops_detected


def get_top_head_and_shoulders(data, max_extremums, min_extremums, tr):
    detected_patterns = []
    for i in range(2, len(max_extremums)):
        if data[max_extremums[i-2]]['High'] + tr < data[max_extremums[i-1]]['High'] and data[max_extremums[i]]['High'] + tr < data[max_extremums[i-1]]['High']:
            if data[max_extremums[i-1]]['High'] - max(data[max_extremums[i-2]]['High'] , data[max_extremums[i]]['High']) > abs(data[max_extremums[i-2]]['High'] - data[max_extremums[i]]['High']):

                first_min = find_min(data, max_extremums[i-2], max_extremums[i-1])
                second_min = find_min(data, max_extremums[i-1], max_extremums[i])

                line_tr = data[first_min]['Low']
                before_min = min_extremums[max(0, find_next_extremum(min_extremums, max_extremums[i-2])-1)]
                before_min = max(find_min_with_condition(data, max_extremums[max(0, i - 3)], max_extremums[i - 2], line_tr), before_min)

                line_tr = data[second_min]['Low']
                after_min = min_extremums[find_next_extremum(min_extremums, max_extremums[i])]
                after_min = after_min if after_min > max_extremums[i] else len(data) - 1
                after_index = len(data) - 1 if i == len(max_extremums) - 1 else max_extremums[i + 1]
                after_min = min(find_min_with_condition(data, max_extremums[i], after_index, line_tr), after_min)

                if data[max_extremums[i-1]]['High'] - max(data[max_extremums[i-2]]['High'] , data[max_extremums[i]]['High']) > abs(data[first_min]['Low'] - data[second_min]['Low']):

                    detected_patterns.append([{'Time': data[before_min]['Time'], 'Price': data[before_min]['Low']},
                                              {'Time': data[max_extremums[i-2]]['Time'], 'Price': data[max_extremums[i-2]]['High']},
                                             {'Time': data[first_min]['Time'], 'Price': data[first_min]['Low']},
                                             {'Time': data[max_extremums[i-1]]['Time'], 'Price': data[max_extremums[i-1]]['High']},
                                             {'Time': data[second_min]['Time'], 'Price': data[second_min]['Low']},
                                             {'Time': data[max_extremums[i]]['Time'], 'Price': data[max_extremums[i]]['High']},
                                             {'Time': data[after_min]['Time'], 'Price': data[after_min]['Low']}])
    return detected_patterns


def get_bottom_head_and_shoulders(data, min_extremums, max_extremums, tr):
    detected_patterns = []
    for i in range(2, len(min_extremums)):
        if data[min_extremums[i-2]]['Low'] - tr > data[min_extremums[i-1]]['Low'] and data[min_extremums[i]]['Low'] - tr > data[min_extremums[i-1]]['Low']:
            if abs(data[min_extremums[i-1]]['Low'] - min(data[min_extremums[i-2]]['Low'], data[min_extremums[i]]['Low'])) > abs(data[min_extremums[i-2]]['Low'] - data[min_extremums[i]]['Low']):

                first_max = find_max(data, min_extremums[i-2], min_extremums[i-1])
                second_max = find_max(data, min_extremums[i-1], min_extremums[i])

                line_tr = data[first_max]['High']
                before_max = max_extremums[max(0, find_next_extremum(max_extremums, min_extremums[i-2])-1)]
                before_max = max(find_max_with_condition(data, min_extremums[max(0, i - 3)], min_extremums[i - 2], line_tr), before_max)

                line_tr = data[second_max]['High']
                after_max = max_extremums[find_next_extremum(max_extremums, min_extremums[i])]
                after_max = after_max if after_max > min_extremums[i] else len(data) - 1
                after_index = len(data) - 1 if i == len(min_extremums) - 1 else min_extremums[i + 1]
                after_max = min(find_max_with_condition(data, min_extremums[i], after_index, line_tr), after_max)

                if abs(data[min_extremums[i-1]]['Low'] - min(data[min_extremums[i-2]]['Low'], data[min_extremums[i]]['Low'])) > abs(data[first_max]['High'] - data[second_max]['High']):

                    detected_patterns.append([{'Time': data[before_max]['Time'], 'Price': data[before_max]['High']},
                                              {'Time': data[min_extremums[i-2]]['Time'], 'Price': data[min_extremums[i-2]]['Low']},
                                             {'Time': data[first_max]['Time'], 'Price': data[first_max]['High']},
                                             {'Time': data[min_extremums[i-1]]['Time'], 'Price': data[min_extremums[i-1]]['Low']},
                                             {'Time': data[second_max]['Time'], 'Price': data[second_max]['High']},
                                             {'Time': data[min_extremums[i]]['Time'], 'Price': data[min_extremums[i]]['Low']},
                                             {'Time': data[after_max]['Time'], 'Price': data[after_max]['High']}])
    return detected_patterns
