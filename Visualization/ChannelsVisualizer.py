
from AlgorithmTools.Channels import get_channels

from Visualization.Tools import *
from Visualization.BaseChart import *


class ChannelsVisualizer:

    def __init__(self, data, extremum_window_start, extremum_window_end, extremum_window_step, extremum_mode, check_window, alpha, extend_number):
        self.data = data
        self.extend_number = extend_number

        self.up_channels, self.down_channels = get_channels(data, extremum_window_start, extremum_window_end,
                                                            extremum_window_step, extremum_mode, check_window, alpha)

    def draw(self, fig, height):

            for up_channel in self.up_channels:
                x, y = [up_channel['UpLine']['x'][0], up_channel['UpLine']['x'][1]], [up_channel['UpLine']['y'][0], up_channel['UpLine']['y'][1]]
                fig.line(x, y, color='blue', width=1)
                x, y = [up_channel['DownLine']['x'][0], up_channel['DownLine']['x'][1]], [up_channel['DownLine']['y'][0], up_channel['DownLine']['y'][1]]
                fig.line(x, y, color='blue', width=1)
                x_left = max(min(up_channel['UpLine']['x'][0], up_channel['DownLine']['x'][0])-self.extend_number, 0)
                x, y = [x_left, up_channel['UpLine']['x'][0]], [np.polyval(up_channel['UpLine']['line'], x_left), up_channel['UpLine']['y'][0]]
                fig.line(x, y, color='blue', width=1, line_dash="dotted")
                x, y = [x_left, up_channel['DownLine']['x'][0]], [np.polyval(up_channel['DownLine']['line'], x_left), up_channel['DownLine']['y'][0]]
                fig.line(x, y, color='blue', width=1, line_dash="dotted")
                x_right = min(max(up_channel['UpLine']['x'][1], up_channel['DownLine']['x'][1]) + self.extend_number, len(self.data)-1)
                x, y = [up_channel['UpLine']['x'][1], x_right], [up_channel['UpLine']['y'][1], np.polyval(up_channel['UpLine']['line'], x_right)]
                fig.line(x, y, color='blue', width=1, line_dash="dotted")
                x, y = [up_channel['DownLine']['x'][1], x_right], [up_channel['DownLine']['y'][1], np.polyval(up_channel['DownLine']['line'], x_right)]
                fig.line(x, y, color='blue', width=1, line_dash="dotted")

            for down_channel in self.down_channels:
                x, y = [down_channel['UpLine']['x'][0], down_channel['UpLine']['x'][1]], [down_channel['UpLine']['y'][0], down_channel['UpLine']['y'][1]]
                fig.line(x, y, color='red', width=1)
                x, y = [down_channel['DownLine']['x'][0], down_channel['DownLine']['x'][1]], [down_channel['DownLine']['y'][0], down_channel['DownLine']['y'][1]]
                fig.line(x, y, color='red', width=1)
                x_left = max(min(down_channel['UpLine']['x'][0], down_channel['DownLine']['x'][0])-self.extend_number, 0)
                x, y = [x_left, down_channel['UpLine']['x'][0]], [np.polyval(down_channel['UpLine']['line'], x_left), down_channel['UpLine']['y'][0]]
                fig.line(x, y, color='red', width=1, line_dash="dotted")
                x, y = [x_left, down_channel['DownLine']['x'][0]], [np.polyval(down_channel['DownLine']['line'], x_left), down_channel['DownLine']['y'][0]]
                fig.line(x, y, color='red', width=1, line_dash="dotted")
                x_right = min(max(down_channel['UpLine']['x'][1], down_channel['DownLine']['x'][1]) + self.extend_number, len(self.data)-1)
                x, y = [down_channel['UpLine']['x'][1], x_right], [down_channel['UpLine']['y'][1], np.polyval(down_channel['UpLine']['line'], x_right)]
                fig.line(x, y, color='red', width=1, line_dash="dotted")
                x, y = [down_channel['DownLine']['x'][1], x_right], [down_channel['DownLine']['y'][1], np.polyval(down_channel['DownLine']['line'], x_right)]
                fig.line(x, y, color='red', width=1, line_dash="dotted")

            show(fig)

