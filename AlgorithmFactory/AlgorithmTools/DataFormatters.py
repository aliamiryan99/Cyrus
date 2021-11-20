import numpy as np


def dictionary_list_to_list_dictionary(data):
    keys = list(data[0].keys())
    changed_data = {key: [] for key in keys}
    for candle in data:
        for key in keys:
            changed_data[key].append(candle[key])
    for key in keys:
        changed_data[key] = np.array(changed_data[key])
    return changed_data
