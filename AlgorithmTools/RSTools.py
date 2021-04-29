import numpy as np


def get_diff_matrix(data, local_max):
    local_max_value = data[local_max]
    local_max_value_sorted = np.sort(local_max_value)
    local_max_value_diff = np.append([np.inf], np.diff(local_max_value_sorted))
    d_type = [('index', int), ('value', float)]
    matrix_list = []
    for i in range(len(local_max)):
        matrix_list.append((local_max[i], local_max_value[i]))
    local_max_matrix = np.array(matrix_list, dtype=d_type)
    local_max_matrix_sorted = np.sort(local_max_matrix, order='value')

    d_type = [('index', int), ('index_2', int), ('value', float), ('diff', float)]
    matrix_list = []
    for i in range(len(local_max_matrix_sorted)):
        pre_index = -1
        if i > 0:
            pre_index = local_max_matrix_sorted[i-1][0]
        matrix_list.append((local_max_matrix_sorted[i][0], local_max_matrix_sorted[i-1][0], local_max_matrix_sorted[i][1], local_max_value_diff[i]))
    local_max_matrix_diff_sorted = np.sort(np.array(matrix_list, dtype=d_type), order=['diff'])
    return local_max_matrix_diff_sorted




