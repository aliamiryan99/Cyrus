

def get_impulses(data, local_min, local_max, num_th):
    up_impulse = []
    j = 0
    start_index = 1
    while local_max[start_index] < local_min[0]:
        start_index += 1
    for i in range(start_index, len(local_max)):
        while local_min[j] < local_max[i]:
            j += 1
            if j >= len(local_min):
                break
        j -= 1
        pre_i = i-1

        while j+1 == len(local_min) or local_max[i] <= local_min[j+1]:
            i += 1
            if i >= len(local_max) or data[local_max[i]]['High'] < data[local_max[i-1]]['High']:
                break
        i -= 1

        if local_min[j] >= local_max[pre_i]:
            while i == 0 or local_min[j] >= local_max[pre_i]:
                j -= 1
                if j < 0 or data[local_min[j+1]]['Low'] < data[local_min[j]]['Low']:
                    break
            j += 1

        if local_min[j] >= local_max[pre_i] and data[local_max[i]]['High'] > data[local_max[pre_i]]['High']:
            if local_max[i] - local_min[j] >= num_th + 1:
                up_impulse.append([local_min[j], local_max[i]])

    down_impulse = []
    j = 0
    start_index = 1
    while local_min[start_index] < local_max[0]:
        start_index += 1
    for i in range(1, len(local_min)):
        while local_max[j] < local_min[i]:
            j += 1
            if j >= len(local_max):
                break
        j -= 1
        pre_i = i-1

        while j+1 == len(local_max) or local_min[i] <= local_max[j+1]:
            i += 1
            if i >= len(local_min) or data[local_min[i]]['Low'] > data[local_min[i-1]]['Low']:
                break
        i -= 1

        if local_max[j] >= local_min[pre_i]:
            while i == 0 or local_max[j] >= local_min[pre_i]:
                j -= 1
                if j < 0 or data[local_max[j]]['High'] > data[local_max[j - 1]]['High']:
                    break
            j += 1

        if local_max[j] >= local_min[pre_i] and data[local_min[i]]['Low'] < data[local_min[pre_i]]['Low']:
            if local_min[i] - local_max[j] >= num_th + 1:
                down_impulse.append([local_max[j], local_min[i]])

    return up_impulse, down_impulse



