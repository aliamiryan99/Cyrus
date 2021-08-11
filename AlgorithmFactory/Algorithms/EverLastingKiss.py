
from AlgorithmFactory.AlgorithmTools.Channels import get_channels
import numpy as np


class EverLastingKiss:

    def __init__(self, symbol, data_history, extremum_start_window, extremum_end_window, extremum_window_step, extremum_mode, check_window, alpha, beta):
        # Data window, moving average window
        self.symbol = symbol
        self.data_window = data_history

        self.extremum_start_window = extremum_start_window
        self.extremum_end_window = extremum_end_window
        self.extremum_window_step = extremum_window_step
        self.extremum_mode = extremum_mode
        self.check_window = check_window
        self.alpha = alpha
        self.beta = beta

    def on_tick(self):
        return 0, 0

    def on_data(self, candle, cash):

        up_channels, down_channels = get_channels(self.data_window, self.extremum_start_window,
                                                  self.extremum_end_window, self.extremum_window_step,
                                                  self.extremum_mode, self.check_window, self.alpha)

        signal = 0
        i = 1
        while i < len(down_channels):
            if self.is_channel_in_range(down_channels[-i]):
                if self.is_down_kissing(down_channels[i]):
                    signal = 1
            else:
                break
            i += 1

        i = 1
        while i < len(up_channels):
            if self.is_channel_in_range(up_channels[-i]):
                if self.is_down_kissing(up_channels[i]):
                    signal = -1
            else:
                break
            i += 1

        self.data_window.pop(0)
        self.data_window.append(candle)
        return signal, self.data_window[-1]['Open']

    def is_channel_in_range(self, channel):
        x_right = max(channel['UpLine']['x'][1], channel['DownLine']['x'][1])

        if (len(self.data_window) - x_right) < channel['Window'] * (self.beta+1):
            return True
        return False

    def is_down_kissing(self, channel):
        x_right, y_right = channel['DownLine']['x'][1], channel['DownLine']['y'][1]
        last_max = x_right
        for i in range(x_right, len(self.data_window)):
            if self.data_window[i]['High'] > self.data_window[last_max]['High']:
                last_max = i
        last_min = last_max
        for i in range(len(self.data_window)):
            if self.data_window[i]['Low'] < self.data_window[last_min]['Low']:
                last_min = i

        if self.data_window[last_max]['High'] > np.polyval(channel['UpLine']['line'], last_max) and \
                self.data_window[last_min]['Low'] < np.polyval(channel['UpLine']['line'], last_min) and \
                self.data_window[-1]['Close'] > np.polyval(channel['UpLine']['line'], len(self.data_window)-1) and \
                self.data_window[-2]['Close'] < np.polyval(channel['UpLine']['line'], len(self.data_window)-2):
            return True

        return False


    def is_up_kissing(self, channel):
        x_right, y_right = channel['UpLine']['x'][1], channel['UpLine']['y'][1]
        last_min = x_right
        for i in range(x_right, len(self.data_window)):
            if self.data_window[i]['Low'] > self.data_window[last_min]['Low']:
                last_min = i
        last_max = last_min
        for i in range(len(self.data_window)):
            if self.data_window[i]['High'] < self.data_window[last_max]['High']:
                last_max = i

        if self.data_window[last_min]['Low'] < np.polyval(channel['DownLine']['line'], last_min) and \
                self.data_window[last_max]['High'] > np.polyval(channel['DownLine']['line'], last_max) and \
                self.data_window[-1]['Close'] < np.polyval(channel['DownLine']['line'], len(self.data_window) - 1) and \
                self.data_window[-2]['Close'] > np.polyval(channel['DownLine']['line'], len(self.data_window) - 2):
            return True

        return False
