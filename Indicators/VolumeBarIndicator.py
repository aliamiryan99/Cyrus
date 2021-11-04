
import numpy as np
import datetime


class VolumeBar:

    def __init__(self, vb_time_frame_cnt):
        self.vb_time_frame_cnt = vb_time_frame_cnt
        self.buffer_data = {'Time': [], 'Bid': np.array([]), 'Ask': np.array([])}
        self.base_time = None
        self.base_diff = None
        self.total_data = []
        self.cum_value = 0

    def update(self, tick, last_week_volume, is_new_week):

        self.buffer_data['Time'].append(tick['Time'])
        self.buffer_data['Ask'] = np.append(self.buffer_data['Ask'], [tick['Ask']])
        self.buffer_data['Bid'] = np.append(self.buffer_data['Bid'], [tick['Bid']])
        thr = last_week_volume / self.vb_time_frame_cnt

        if self.cum_value == int(thr) or is_new_week:

            price_value = ((self.buffer_data['Ask'] + self.buffer_data['Bid'])/2)
            time_value = self.buffer_data['Time'][-1]
            start_time = self.buffer_data['Time'][0]
            middle_time = self.buffer_data['Time'][len(self.buffer_data['Time'])//2]
            open_value = price_value[0]
            high_value = np.max(price_value)
            low_value = np.min(price_value)
            close_value = price_value[-1]
            WAP = sum(price_value)/len(price_value)

            if self.base_time is not None:
                if self.base_diff is None:
                    self.base_diff = (time_value - self.base_time) / 2
                x = self.get_candle_x_center(time_value, self.total_data[-1]['Time'])
            else:
                self.base_time = time_value
                x = 0

            self.total_data.append({'StartTime': start_time, 'MiddleTime': middle_time, 'Time': time_value,
                                    'Open': open_value, 'High': high_value, 'Low': low_value,
                                    'Close': close_value, 'WAP': WAP, 'Volume': self.cum_value, 'CandleXCenter': x})


            print(self.total_data[-1])

            self.cum_value = 0
            self.buffer_data = {'Time': [], 'Bid': np.array([]), 'Ask': np.array([])}

        else:
            self.cum_value += 1

    def get_candle_x_center(self, time, pre_time):
        time_diff = (time - pre_time)/2

        x = ((time - self.base_time) - (time_diff - self.base_diff)).total_seconds() / 3600
        return x

    def get_time_of_candle_x_center(self, candle_x_cneter):
        seconds = (candle_x_cneter * 3600)
        hours = seconds // 3600
        minutes = (seconds - seconds // 3600) // 60
        seconds = seconds % 60
        hours_added = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
        new_time = self.base_time + hours_added
        return new_time
