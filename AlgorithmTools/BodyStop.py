
def get_body_mean(data, last_local_min, last_local_max):
    sum_body_size_local_min = 0
    for i in range(last_local_min, len(data)):
        if data[i]['Volume'] != 0:
            sum_body_size_local_min += abs(data[i]['Close'] - data[i]['Open'])
    mean_body_size_local_min = sum_body_size_local_min / (len(data) - last_local_min + 1)

    sum_body_size_local_max = 0
    for i in range(last_local_max, len(data)):
        if data[i]['Volume'] != 0:
            sum_body_size_local_max += abs(data[i]['Close'] - data[i]['Open'])
    mean_body_size_local_max = sum_body_size_local_max / (len(data) - last_local_max + 1)

    return mean_body_size_local_min, mean_body_size_local_max
