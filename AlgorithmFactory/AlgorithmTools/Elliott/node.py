import numpy as np
from AlgorithmFactory.AlgorithmTools.Elliott.utility import intermediates_signal
import pandas as pd
import copy


class Node:    
    def build_node(self, df, price='mean', offset=0, length=None, step=None, candle_timeframe="W1", date=None, neo_timeframe=None, add_missing_candle=False):    
        mark = []
        if price == 'close':
            df['Price'] = df.Close
        elif price == 'mean':
            df['Price'] = df.apply(lambda row: 0.5 * (row.High + row.Low), axis=1)
        elif price == 'neo':            
            df = aggregate_data(df.to_dict("Records"), candle_timeframe, neo_timeframe)
            df = pd.DataFrame.from_dict(df)
            # df = df.set_index('Time')
            if date is not None:
                df = df[df['Time'] >= date]
            signal = np.empty(len(df))
            signal[:] = np.nan
            if neo_timeframe is not None:
                step_list = config_step(df, candle_timeframe, neo_timeframe, add_missing_candle)
                i = 0
                step_list_size = len(step_list) - 1 if add_missing_candle else len(step_list) 
                for cnt in range(step_list_size):
                    step = step_list[cnt]                    
                    max_idx = np.argmax(df.High[i:i+step])
                    min_idx = np.argmin(df.Low[i:i+step])
                    if max_idx < min_idx:
                        signal[i+int(.25*step)] = df.High[i+max_idx]
                        signal[i+int(.75*step)] = df.Low[i+min_idx]
                    else:
                        signal[i+int(.25*step)] = df.Low[i+min_idx]
                        signal[i+int(.75*step)] = df.High[i+max_idx]
                
                    mark.append(i+int(.25*step))
                    mark.append(i+int(.75*step))
                    i += step
    
                # signal[mark[-1]:] = signal[mark[-1]]
                #for example for D1 to M1 steps are not equal..so we take mean of them
                tempstep = int(np.ceil(np.mean(step_list)))
                last_step1 = int(.25*tempstep)
                last_step2 = int(.75*tempstep)
                rem = len(signal) - i
                if rem <= last_step1:
                    signal[mark[-1]:] = signal[mark[-1]]

                elif rem <= last_step2:
                    max_idx = np.argmax(df.High[i:i+rem])
                    min_idx = np.argmin(df.Low[i:i+rem])
                    if max_idx < min_idx:
                        signal[i+int(.25*tempstep)] = df.High[i+max_idx]
                    else:
                        signal[i+int(.25*tempstep)] = df.Low[i+min_idx]

                    mark.append(i+int(.25*tempstep))

                elif rem > last_step2:
                    max_idx = np.argmax(df.High[i:i+rem])
                    min_idx = np.argmin(df.Low[i:i+rem])
                    if max_idx < min_idx:
                        signal[i+int(.25*tempstep)] = df.High[i+max_idx]
                        signal[i+int(.75*tempstep)] = df.Low[i+min_idx]
                    else:
                        signal[i+int(.25*tempstep)] = df.Low[i+min_idx]
                        signal[i+int(.75*tempstep)] = df.High[i+max_idx]

                    mark.append(i+int(.25*tempstep))
                    mark.append(i+int(.75*tempstep))

                signal = intermediates_signal(signal, mark)
                signal[0:mark[0]] = signal[mark[0]]
                signal[mark[-1]:] = signal[mark[-1]]

                df['Price'] = signal.tolist()
            else:
                for i in range(0, len(df)-step, step):
                    max_idx = np.argmax(df.High[i:i+step])
                    min_idx = np.argmin(df.Low[i:i+step])
                    if max_idx < min_idx:
                        signal[i+int(.25*step)] = df.High[i+max_idx]
                        signal[i+int(.75*step)] = df.Low[i+min_idx]
                    else:
                        signal[i+int(.25*step)] = df.Low[i+min_idx]
                        signal[i+int(.75*step)] = df.High[i+max_idx]
                
                    mark.append(i+int(.25*step))
                    mark.append(i+int(.75*step))

                signal = intermediates_signal(signal, mark)
                signal[0:mark[0]] = signal[mark[0]]
                signal[mark[-1]:] = signal[mark[-1]]
                df['Price'] = signal.tolist()

        return df,mark


def config_step(df, candle_time_frame, neo_time_frame, add_missing_candle=False):
    time_conv = {"M1":1,"M5":5,"M15":15,"M30":30,"H1":60,"H4":240,"H12":720,"D1":1440}
    ratio = 1

    if add_missing_candle:

        if neo_time_frame in time_conv and candle_time_frame in time_conv:
            ratio = int(time_conv[neo_time_frame] / time_conv[candle_time_frame])
            step_list = [ratio for i in range(0, len(df)-ratio, ratio)]
            return step_list
        elif candle_time_frame in time_conv:
            ratio = int(time_conv["D1"] / time_conv[candle_time_frame])

        old_id = get_time_id(df['Time'][0], neo_time_frame)    
        step_list = []
        if neo_time_frame == "mon1":
            step_list.append(df['Time'][0].daysinmonth * ratio)
            for i in range(1, len(df)):
                new_id = get_time_id(df['Time'][i], neo_time_frame)
                if new_id != old_id:
                    step_list.append(df['Time'][i].daysinmonth * ratio)
                    old_id = new_id
            return step_list
        elif neo_time_frame == "W1":
            pass


    else:    
        old_id = get_time_id(df['Time'][0], neo_time_frame)    
        step_list = []
        count = 0
        for i in range(1, len(df)):
            new_id = get_time_id(df['Time'][i], neo_time_frame)
            count += 1
            if new_id != old_id:
                step_list.append(count)
                count = 0
                old_id = new_id
                            
        return step_list


def get_time_id(time, time_frame):
    identifier = time.day
    if time_frame == "mon1":
        identifier = time.month
    elif time_frame == "W1":
        identifier = time.isocalendar()[1]
    elif time_frame == "H12":
        identifier = time.day * 2 + time.hour // 12
    elif time_frame == "H4":
        identifier = time.day * 6 + time.hour // 4
    elif time_frame == "H1":
        identifier = time.day * 24 + time.hour
    elif time_frame == "M30":
        identifier = time.hour * 2 + time.minute // 30
    elif time_frame == "M15":
        identifier = time.hour * 4 + time.minute // 15
    elif time_frame == "M5":
        identifier = time.hour * 12 + time.minute // 5
    elif time_frame == "M1":
        identifier = time.hour * 60 + time.minute
    return identifier


def next_time(cur_time, time_frame):
    if time_frame == "mon1":
        return cur_time + pd.Timedelta(days=cur_time.daysinmonth)
    if time_frame == "D1":
        return cur_time + pd.Timedelta(days=1)
    if time_frame == "W1":
        return cur_time + pd.Timedelta(weeks=1)
    if time_frame == "H12":
        return cur_time + pd.Timedelta(hours=12)
    if time_frame == "H4":
        return cur_time + pd.Timedelta(hours=4)
    if time_frame == "H1":
        return cur_time + pd.Timedelta(hours=1)
    if time_frame == "M30":
        return cur_time + pd.Timedelta(minutes=30)
    if time_frame == "M15":
        return cur_time + pd.Timedelta(minutes=15)
    if time_frame == "M5":
        return cur_time + pd.Timedelta(minutes=5)
    if time_frame == "M1":
        return cur_time + pd.Timedelta(minutes=1)


def aggregate_data(histories, candle_timeframe, neo_timeframe, add_missing_candle=False):
    old_id = get_time_id(histories[0]['Time'], candle_timeframe)
    new_history = []
    new_history.append(copy.deepcopy(histories[0]))

    next_date = next_time(histories[0]['Time'], candle_timeframe)

    for i in range(1, len(histories)):
        new_id = get_time_id(histories[i]['Time'], candle_timeframe)
        if new_id != old_id:

            if add_missing_candle:
                while histories[i]['Time'] > next_date : # fill missing data based on last candle
                    new_history.append(copy.deepcopy(histories[i]))
                    new_history[-1]['Time'] = next_date
                    next_date = next_time(next_date, candle_timeframe)
                next_date = next_time(next_date, candle_timeframe)

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
    
    # if neo_timeframe == "D1" or neo_timeframe == "mon1":
    #     index = 0
    #     while new_history[index]['Time'].day != 1:
    #         index += 1
    #     new_history = new_history[index:]
    return new_history


# DEBUG = False
# def csv_to_df(csv_files: list, date_format='%d.%m.%Y %H:%M:%S.%f'):
#     """
#     Get a list of csv files, load them and parse date column(s)...
#     Returns:
#         a list of pandas data-frames.
#     """
#     data_frames = []
#     parse_date = lambda x: pd.datetime.strptime(x, date_format)
#     if DEBUG:
#         print('\nLoading csv data:')
#     for f in csv_files:
#         try:
#             df = pd.read_csv(f)
#         except:
#             df = pd.read_excel(f)

#         if 'Date' in df.columns:
#             df.rename(columns={'Date': 'GMT'}, inplace=True)
#         if 'Gmt time' in df.columns:
#             df.rename(columns={'Gmt time': 'GMT'}, inplace=True)
#         if 'GMT' in df.columns:
#             try:
#                 df['GMT'] = pd.to_datetime(df['GMT'], format=date_format)
#             except:
#                 df['GMT'] = pd.to_datetime(df['GMT'], format='%d.%m.%Y %H:%M:%S.%f')
#         df = df.sort_values(['GMT'])
#         df = df.reset_index()
#         data_frames.append(df)
#         if DEBUG:
#             print(f'  {f}')
#     if DEBUG:
#         print()
#     return data_frames


