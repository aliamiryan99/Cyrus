

def get_impulses(data, local_min, local_max):
    up_impulse = []
    j = 1
    start_index = 1
    while local_max[start_index] < local_min[0]:
        start_index += 1
    for i in range(start_index, len(local_max)):
        while local_min[j] < local_max[i]:
            j += 1
            if j >= len(local_min):
                break
        if j >= len(local_min):
            break

        if local_min[j-1] > local_max[i-1] and data[local_max[i]]['High'] > data[local_max[i-1]]['High']:
            up_impulse.append([local_min[j-1], local_max[i]])

    down_impulse = []
    j = 1
    start_index = 1
    while local_min[start_index] < local_max[0]:
        start_index += 1
    for i in range(1, len(local_min)):
        while local_max[j] < local_min[i]:
            j += 1
            if j >= len(local_max):
                break
        if j >= len(local_max):
            break
        if local_max[j - 1] > local_min[i - 1] and data[local_min[i]]['Low'] < data[local_min[i - 1]]['Low']:
            down_impulse.append([local_max[j - 1], local_min[i]])

    return up_impulse, down_impulse
