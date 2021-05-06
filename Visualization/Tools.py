import numpy as np


def get_min_max_indicator(indicators):
    values = np.array(indicators)

    min_indicator_value = np.min(values, axis=0)
    max_indicator_value = np.max(values, axis=0)

    return min_indicator_value, max_indicator_value