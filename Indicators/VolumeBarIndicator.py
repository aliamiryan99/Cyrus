
import numpy as np


class VolumeBar:

    def __init__(self, vb_time_frame_cnt):
        self.vb_time_frame_cnt = vb_time_frame_cnt
        self.buffer_data = {'Time': [], 'Bid': np.array([]), 'Ask': np.array([])}
        self.total_data = []
        self.cum_value = 0

    def update(self, tick, last_week_volume, is_new_week):

        self.buffer_data['Time'].append(tick['Time'])
        self.buffer_data['Ask'] = np.append(self.buffer_data['Ask'], [tick['Ask']])
        self.buffer_data['Bid'] = np.append(self.buffer_data['Bid'], [tick['Bid']])
        thr = last_week_volume / self.vb_time_frame_cnt

        if self.cum_value == int(thr) or is_new_week:

            price_value = ((self.buffer_data['Ask'] + self.buffer_data['Bid'])/2)
            time_value = self.buffer_data['Time'][0]
            open_value = price_value[0]
            high_value = np.max(price_value)
            low_value = np.min(price_value)
            close_value = price_value[-1]
            WAP = sum(price_value)/len(price_value)

            self.total_data.append({'Time': time_value, 'Open': open_value, 'High': high_value, 'Low': low_value,
                                    'Close': close_value, 'WAP': WAP, 'Volume': self.cum_value})

            print(self.total_data)

            self.cum_value = 0
            self.buffer_data = {'Time': [], 'Bid': np.array([]), 'Ask': np.array([])}

        else:
            self.cum_value += 1

