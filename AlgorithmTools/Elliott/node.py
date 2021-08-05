import numpy as np
from AlgorithmTools.Elliott.utility import intermediates_signal
import pandas as pd
import copy


class Node:
    def build_node(self, df, price='mean', offset=0, length=None, step=None, timeframe="W1", date=None):
        mark = []
        if price == 'close':
            df['Price'] = df.Close
        elif price == 'mean':
            df['Price'] = df.apply(lambda row: 0.5 * (row.High + row.Low), axis=1)
        elif price == 'neo':
            df = aggregate_data(df.to_dict("Records"), timeframe)
            df = pd.DataFrame.from_dict(df)
            # df = df.set_index('Time')
            if date is not None:
                df = df[df.index >= date]
            signal = np.empty(len(df))
            signal[:] = np.nan
            for i in range(0, len(df) - step, step):
                max_idx = np.argmax(df.High[i:i + step])
                min_idx = np.argmin(df.Low[i:i + step])
                if max_idx < min_idx:
                    signal[i + int(.25 * step)] = df.High[i + max_idx]
                    signal[i + int(.75 * step)] = df.Low[i + min_idx]
                else:
                    signal[i + int(.25 * step)] = df.Low[i + min_idx]
                    signal[i + int(.75 * step)] = df.High[i + max_idx]

                mark.append(i + int(.25 * step))
                mark.append(i + int(.75 * step))

            signal = intermediates_signal(signal, mark)
            signal[0:mark[0]] = signal[mark[0]]
            signal[mark[-1]:] = signal[mark[-1]]
            df['Price'] = signal.tolist()

        return df, mark


def get_time_id(time, time_frame):
    identifier = time.day
    if time_frame == "mon1":
        identifier = time.month
    if time_frame == "W1":
        identifier = time.isocalendar()[1]
    if time_frame == "H12":
        identifier = time.day * 2 + time.hour // 12
    if time_frame == "H4":
        identifier = time.day * 6 + time.hour // 4
    if time_frame == "H1":
        identifier = time.day * 24 + time.hour
    if time_frame == "M30":
        identifier = time.hour * 2 + time.minute // 30
    if time_frame == "M15":
        identifier = time.hour * 4 + time.minute // 15
    if time_frame == "M5":
        identifier = time.hour * 12 + time.minute // 5
    if time_frame == "M1":
        identifier = time.hour * 60 + time.minute
    return identifier


def aggregate_data(histories, time_frame):
    old_id = get_time_id(histories[0]['Time'], time_frame)
    new_history = []
    new_history.append(copy.deepcopy(histories[0]))
    for i in range(1, len(histories)):
        new_id = get_time_id(histories[i]['Time'], time_frame)
        if new_id != old_id:
            new_history.append(copy.deepcopy(histories[i]))
            old_id = new_id
        else:
            if new_history[-1]['Volume'] == 0:
                new_history[-1] = copy.deepcopy(histories[i])
            else:
                new_history[-1]['High'] = max(new_history[-1]['High'], histories[i]['High'])
                new_history[-1]['Low'] = min(new_history[-1]['Low'], histories[i]['Low'])
                new_history[-1]['Close'] = histories[i]['Close']
                new_history[-1]['Volume'] += histories[i]['Volume']
    return new_history
