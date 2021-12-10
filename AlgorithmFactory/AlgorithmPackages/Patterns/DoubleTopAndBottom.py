
from AlgorithmFactory.AlgorithmTools.LocalExtermums import get_local_extermums
from AlgorithmFactory.AlgorithmTools.LocalExtermums import find_next_extremum
from AlgorithmFactory.AlgorithmTools.CandleTools import get_body_mean
from AlgorithmFactory.AlgorithmPackages.Patterns.Tools import *


def get_all_double_top_bottom_scales(data, scales, coefficient):
    body_mean = get_body_mean(data, len(data))
    double_tops_detected = {}
    double_bottom_detected = {}
    for scale in scales:
        tr = body_mean * (scale / coefficient)
        min_extremum, max_extremum = get_local_extermums(data, scale, 1)
        double_tops_detected[scale] = get_double_tops(data, max_extremum, min_extremum, tr)
        double_bottom_detected[scale] = get_double_bottoms(data, min_extremum, max_extremum, tr)
    return double_bottom_detected, double_tops_detected


def get_double_tops(data, max_extremums, min_extremums, tr):
    detected_patterns = []
    for i in range(2, len(max_extremums)):
        if abs(data[max_extremums[i]]['High'] - data[max_extremums[i-1]]['High']) < tr:
            second_min = min_extremums[find_next_extremum(min_extremums, max_extremums[i-1])]
            second_min = find_min(data, max_extremums[i-1], max_extremums[i]) if second_min > max_extremums[i] else second_min
            first_min = min_extremums[max(0, find_next_extremum(min_extremums, max_extremums[i-1])-1)]
            line_tr = data[second_min]['Low'] * 2 - data[max_extremums[i - 1]]['High']
            first_min = max(find_min_with_condition(data, max_extremums[i-2], max_extremums[i-1], line_tr), first_min)
            third_min = min_extremums[find_next_extremum(min_extremums, max_extremums[i])]
            third_min = third_min if third_min > max_extremums[i] else len(data)-1
            third_index = len(data)-1 if i == len(max_extremums)-1 else max_extremums[i+1]
            third_min = min(find_min_with_condition(data, max_extremums[i], third_index, line_tr), third_min)

            detected_patterns.append([{'Time': data[first_min]['Time'], 'Price': data[first_min]['Low']},
                                     {'Time': data[max_extremums[i-1]]['Time'], 'Price': data[max_extremums[i-1]]['High']},
                                     {'Time': data[second_min]['Time'], 'Price': data[second_min]['Low']},
                                     {'Time': data[max_extremums[i]]['Time'], 'Price': data[max_extremums[i]]['High']},
                                     {'Time': data[third_min]['Time'], 'Price': data[third_min]['Low']}])
    return detected_patterns


def get_double_bottoms(data, min_extremums, max_extremums, tr):
    detected_patterns = []
    for i in range(2, len(min_extremums)):
        if abs(data[min_extremums[i]]['Low'] - data[min_extremums[i - 1]]['Low']) < tr:
            second_max = max_extremums[find_next_extremum(max_extremums, min_extremums[i - 1])]
            second_max = find_max(data, min_extremums[i - 1], min_extremums[i]) if second_max > min_extremums[i] else second_max
            first_max = max_extremums[max(0, find_next_extremum(max_extremums, min_extremums[i - 1]) - 1)]
            line_tr = data[second_max]['High'] * 2 - data[min_extremums[i-1]]['Low']
            first_max = max(find_max_with_condition(data, min_extremums[i - 2], min_extremums[i - 1], line_tr), first_max)
            third_max = max_extremums[find_next_extremum(max_extremums, min_extremums[i])]
            third_max = third_max if third_max > min_extremums[i] else len(data)-1
            third_index = len(data) - 1 if i == len(min_extremums) - 1 else min_extremums[i + 1]
            third_max = min(find_max_with_condition(data, min_extremums[i], third_index, line_tr), third_max)

            detected_patterns.append([{'Time': data[first_max]['Time'], 'Price': data[first_max]['High']},
                                     {'Time': data[min_extremums[i-1]]['Time'], 'Price': data[min_extremums[i-1]]['Low']},
                                     {'Time': data[second_max]['Time'], 'Price': data[second_max]['High']},
                                     {'Time': data[min_extremums[i]]['Time'], 'Price': data[min_extremums[i]]['Low']},
                                     {'Time': data[third_max]['Time'], 'Price': data[third_max]['High']}])
    return detected_patterns


