

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


def find_min_with_condition(data, start, end, tr):
    min = start + 1
    for i in range(start+1, end - 1):
        if data[i]['Low'] >= tr:
            min = i
            break
    else:
        for i in range(start + 1, end - 1):
            if data[i]['Low'] > data[min]['Low']:
                min = i
        return min
    for i in range(start + 1, end - 1):
        if tr <= data[i]['Low'] < data[min]['Low']:
            min = i
    return min


def find_max_with_condition(data, start, end, tr):
    max = start + 1
    for i in range(start+1, end - 1):
        if data[i]['High'] <= tr:
            max = i
            break
    else:
        for i in range(start + 1, end - 1):
            if data[i]['High'] < data[max]['High']:
                max = i
        return max
    for i in range(start + 1, end - 1):
        if data[max]['High'] < data[i]['High'] <= tr:
            max = i
    return max