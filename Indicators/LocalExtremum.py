def localExtremum(data, win):
    localMin = [0] * len(data)
    localMax = [0] * len(data)

    for i in range(0, len(data)):
        lb = i - win    # lower Band
        if lb < 0:
            lb = 0
        up = i + win+1  # Upper Band
        if up >= len(data):
            up = len(data)
        if data[i]['low'] <=  min([d['low'] for d in data[lb: up]]):
            localMin[i] = i

        if data[i]['high'] >= max([d['high'] for d in data[lb: up]]):
            localMax[i] = i

    localMax = list(filter(lambda num: num != 0, localMax))
    localMin = list(filter(lambda num: num != 0, localMin))

    return [localMin, localMax]






