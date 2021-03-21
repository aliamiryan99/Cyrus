def index_date(data, date):
    start = 0
    end = len(data) - 1
    if date < data.iloc[start]['Time'] or date > data.iloc[end]['Time']:
        return -1
    i = 0
    while start <= end:
        i = int((start + end) / 2)
        if data.iloc[i]['Time'] == date:
            return i
        elif data.iloc[i]['Time'] < date:
            start = i + 1
        elif data.iloc[i]['Time'] > date:
            end = i - 1
    if data.iloc[i]['Time'] <= date:
        return i
    else:
        return i-1

def index_date_v2(data, date):
    start = 0
    end = len(data) - 1
    if date < data[start]['Time'] or date > data[end]['Time']:
        return -1
    i = 0
    while start <= end:
        i = int((start + end) / 2)
        if data[i]['Time'] == date:
            return i
        elif data[i]['Time'] < date:
            start = i + 1
        elif data[i]['Time'] > date:
            end = i - 1
    if data[i]['Time'] <= date:
        return i
    else:
        return i - 1