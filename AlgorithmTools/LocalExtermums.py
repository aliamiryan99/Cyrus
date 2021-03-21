import numpy as np

def get_local_extermums(data, window):
    Open = np.array([d['Open'] for d in data])
    High = np.array([d['High'] for d in data])
    Low = np.array([d['Low'] for d in data])

    localMin = [0] * len(data)
    localMax = [0] * len(data)

    for i in range(window, len(Open) - window):
        if Low[i] <= Low[i - window:i + window].min():
            localMin[i] = i
        if High[i] >= High[i - window:i + window].max():
            localMax[i] = i

    localMax = np.array(list(filter(lambda num: num != 0, localMax)))
    localMin = np.array(list(filter(lambda num: num != 0, localMin)))

    return localMin, localMax

def get_local_extermums_asymetric(data, window, alpha):
    Open = np.array([d['Open'] for d in data])
    High = np.array([d['High'] for d in data])
    Low = np.array([d['Low'] for d in data])

    localMin = [0] * len(data)
    localMax = [0] * len(data)

    up_window = max(round(window/alpha), 1)
    for i in range(window, len(Open) - window):
        if Low[i] <= Low[i - window:i + up_window].min():
            localMin[i] = i
        if High[i] >= High[i - window:i + up_window].max():
            localMax[i] = i

    localMax = np.array(list(filter(lambda num: num != 0, localMax)))
    localMin = np.array(list(filter(lambda num: num != 0, localMin)))

    return localMin, localMax

def get_last_local_extermum(data, window):
    localMin, localMax = get_local_extermums(data, window)
    return localMin[-1], localMax[-1]