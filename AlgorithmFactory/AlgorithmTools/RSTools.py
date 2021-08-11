from AlgorithmFactory.AlgorithmTools.CandleTools import *


def get_support_resistance_lines(data, local_extremum, local_extremum_value):
    s_r_matrix = []

    bottom_candle, top_candle = get_bottom_top(data)
    for i in range(len(local_extremum)):
        value = local_extremum_value[i]
        shadow_hit, body_hit = 0, 0
        for j in range(len(data)):
            if data[j]['Low'] <= value <= data[j]['High']:
                if bottom_candle[j] < value < top_candle[j]:
                    body_hit += 1
                else:
                    shadow_hit += 1
        s_r_matrix.append((local_extremum[i], value, shadow_hit, body_hit))

    d_type = [('index', int), ('value', float), ('shadow_hit', int), ('body_hit', int)]
    return np.sort(np.array(s_r_matrix, dtype=d_type), order=['shadow_hit', 'body_hit'])[::-1]


def get_diff_matrix(price, local_extremum):
    local_extremum_value = price[local_extremum]
    local_extremum_value_sorted = np.sort(local_extremum_value)
    local_extremum_value_diff = np.append([np.inf], np.diff(local_extremum_value_sorted))
    d_type = [('index', int), ('value', float)]
    matrix_list = []
    for i in range(len(local_extremum)):
        matrix_list.append((local_extremum[i], local_extremum_value[i]))
    local_extremum_matrix = np.array(matrix_list, dtype=d_type)
    local_extremum_matrix_sorted = np.sort(local_extremum_matrix, order='value')

    d_type = [('index', int), ('index_2', int), ('value', float), ('diff', float)]
    matrix_list = []
    for i in range(len(local_extremum_matrix_sorted)):
        pre_index = -1
        if i > 0:
            pre_index = local_extremum_matrix_sorted[i - 1][0]
        matrix_list.append((local_extremum_matrix_sorted[i][0], local_extremum_matrix_sorted[i - 1][0], local_extremum_matrix_sorted[i][1], local_extremum_value_diff[i]))
    local_extremum_matrix_diff_sorted = np.sort(np.array(matrix_list, dtype=d_type), order=['diff'])
    return local_extremum_matrix_diff_sorted




