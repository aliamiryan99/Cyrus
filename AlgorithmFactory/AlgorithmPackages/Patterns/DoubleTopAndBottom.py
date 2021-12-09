

def get_double_tops(data, max_extremums, tr):
    pattern_detected = []
    for i in range(2, len(max_extremums)):
        if abs(data[max_extremums[i]]['High'] - data[max_extremums[i-1]]['High']) < tr:
            first_min = find_min(data, max_extremums[i-2], max_extremums[i-1])
            second_min = find_min(data, max_extremums[i-1], max_extremums[i])
            third_index = len(data)-1 if i == len(max_extremums)-1 else max_extremums[i+1]
            third_min = find_min(data, max_extremums[i], third_index)

            pattern_detected.append([{'Time': data[first_min]['Time'], 'Price': data[first_min]['Low']},
                                     {'Time': data[max_extremums[i-1]]['Time'], 'Price': data[max_extremums[i-1]]['High']},
                                     {'Time': data[second_min]['Time'], 'Price': data[second_min]['Low']},
                                     {'Time': data[max_extremums[i]]['Time'], 'Price': data[max_extremums[i]]['High']},
                                     {'Time': data[third_min]['Time'], 'Price': data[third_min]['Low']}])
    return pattern_detected


def get_double_bottoms(data, min_extremums, tr):
    pattern_detected = []
    for i in range(2, len(min_extremums)):
        if abs(data[min_extremums[i]]['Low'] - data[min_extremums[i - 1]]['Low']) < tr:
            first_max = find_max(data, min_extremums[i - 2], min_extremums[i - 1])
            second_max = find_max(data, min_extremums[i - 1], min_extremums[i])
            third_index = len(data) - 1 if i == len(min_extremums) - 1 else min_extremums[i + 1]
            third_max = find_max(data, min_extremums[i], third_index)

            pattern_detected.append([{'Time': data[first_max]['Time'], 'Price': data[first_max]['High']},
                                     {'Time': data[min_extremums[i-1]]['Time'], 'Price': data[min_extremums[i-1]]['Low']},
                                     {'Time': data[second_max]['Time'], 'Price': data[second_max]['High']},
                                     {'Time': data[min_extremums[i]]['Time'], 'Price': data[min_extremums[i]]['Low']},
                                     {'Time': data[third_max]['Time'], 'Price': data[third_max]['High']}])
    return pattern_detected


def find_min(data, start, end):
    min = start+1
    for i in range(start+1, end-1):
        if data[i]['Low'] < data[min]['Low']:
            min = i
    return min


def find_max(data, start, end):
    max = start+1
    for i in range(start+1, end-1):
        if data[i]['High'] > data[max]['High']:
            max = i
    return max