
from Converters.Tools import *
import copy


def aggregate_data(histories, time_frame):
    old_id = get_time_id(histories[0]['Time'], time_frame)
    new_history = [copy.deepcopy(histories[0])]
    for i in range(1, len(histories)):
        new_id = get_time_id(histories[i]['Time'], time_frame)
        if new_id != old_id:
            new_history.append(copy.deepcopy(histories[i]))
            old_id = new_id
        else:
            if new_history[-1]['Volume'] == 0 and histories[i]['Volume'] != 0:
                new_history[-1] = copy.deepcopy(histories[i])
                pass
            else:
                new_history[-1]['High'] = max(new_history[-1]['High'], histories[i]['High'])
                new_history[-1]['Low'] = min(new_history[-1]['Low'], histories[i]['Low'])
                new_history[-1]['Close'] = histories[i]['Close']
                new_history[-1]['Volume'] += histories[i]['Volume']
    return new_history
