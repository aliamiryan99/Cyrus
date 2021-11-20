from MetaTraderChartTool.BasicChartTools import BasicChartTools
from MetaTraderChartTool.RealTimeTools.RealTimeTool import RealTimeTool

from AlgorithmFactory.AlgorithmTools.LocalExtermums import *


from AlgorithmFactory.AlgorithmTools.Channels import get_channels
from AlgorithmFactory.AlgorithmTools.ParallelChannels import get_parallel_channels


class Channel(RealTimeTool):

    def __init__(self, chart_tool: BasicChartTools, data, window, extremum_window_start, extremum_window_end, extremum_window_step, extremum_mode, check_window, alpha, extend_number, type):
        super().__init__(chart_tool, data)

        self.window = window
        self.extend_number = extend_number
        self.extremum_window_start = extremum_window_start
        self.extremum_window_end = extremum_window_end
        self.extremum_window_step = extremum_window_step
        self.extremum_mode = extremum_mode
        self.check_window = check_window
        self.alpha = alpha
        self.extend_number = extend_number
        self.type = type

        self.last_up_channel_date = None
        self.last_down_channel_date = None

        self.last_up_channel = None
        self.last_down_channel = None

        self.up_counter = -1
        self.down_counter = -1

        self.ray = 0
        self.width = 1
        self.up_color = "12,50,250"
        self.down_color = "220,50,12"
        self.extend_style = self.chart_tool.EnumStyle.Dot

        self.draw_channel()

        self.data = self.data[-self.window:]

    def on_tick(self, time, bid, ask):
        pass

    def on_data(self, candle):
        self.draw_channel()
        self.update_last_channel()

        self.data.pop(0)
        self.data.append(candle)

    def draw_channel(self):
        if self.type == 'monotone':
            self.up_channels, self.down_channels = get_channels(self.data, self.extremum_window_start, self.extremum_window_end,
                                                                self.extremum_window_step, self.extremum_mode, self.check_window,
                                                                self.alpha)
        elif self.type == 'betweenness':
            self.up_channels, self.down_channels = get_parallel_channels(self.data, self.extremum_window_start,
                                                                         self.extremum_window_end, self.extremum_window_step,
                                                                         self.extremum_mode, self.check_window, self.alpha)

        ray = self.ray
        width = self.width
        up_color = self.up_color
        down_color = self.down_color
        extend_style = self.extend_style

        # # Main Up Channel
        if len(self.up_channels) > 0:
            names_up, times1_up, prices1_up, times2_up, prices2_up = [], [], [], [], []
            names_down, times1_down, prices1_down, times2_down, prices2_down = [], [], [], [], []
            self.last_up_channel = self.up_channels[-1]
            self.last_up_channel['UpLine']['Time'] = [self.data[self.last_up_channel['UpLine']['x'][0]]['Time'],
                                                      self.data[self.last_up_channel['UpLine']['x'][1]]['Time']]
            self.last_up_channel['DownLine']['Time'] = [self.data[self.last_up_channel['DownLine']['x'][0]]['Time'],
                                                        self.data[self.last_up_channel['DownLine']['x'][1]]['Time']]

            if self.last_up_channel_date is not None:
                if self.last_up_channel_date != self.data[self.up_channels[-1]['UpLine']['x'][0]]['Time']:
                    self.up_counter += 1
                    self.append_line(f"UpChannel_UpLine{self.up_counter}", self.up_channels[-1]['UpLine']['x'][0],
                                     self.up_channels[-1]['UpLine']['x'][1], self.up_channels[-1]['UpLine']['y'][0],
                                     self.up_channels[-1]['UpLine']['y'][1], names_up, times1_up, prices1_up, times2_up,
                                     prices2_up)
                    self.append_line(f"UpChannel_DownLine{self.up_counter}", self.up_channels[-1]['DownLine']['x'][0],
                                     self.up_channels[-1]['DownLine']['x'][1], self.up_channels[-1]['DownLine']['y'][0],
                                     self.up_channels[-1]['DownLine']['y'][1], names_down, times1_down, prices1_down,
                                     times2_down,
                                     prices2_down)
            else:
                for i in range(len(self.up_channels)):
                    self.append_line(f"UpChannel_UpLine{i}", self.up_channels[i]['UpLine']['x'][0],
                                     self.up_channels[i]['UpLine']['x'][1], self.up_channels[i]['UpLine']['y'][0],
                                     self.up_channels[i]['UpLine']['y'][1], names_up, times1_up, prices1_up, times2_up,
                                     prices2_up)
                    self.append_line(f"UpChannel_DownLine{i}", self.up_channels[i]['DownLine']['x'][0],
                                     self.up_channels[i]['DownLine']['x'][1], self.up_channels[i]['DownLine']['y'][0],
                                     self.up_channels[i]['DownLine']['y'][1], names_down, times1_down, prices1_down,
                                     times2_down,
                                     prices2_down)
                    self.up_counter += 1

            if len(names_up) > 0:
                self.chart_tool.trend_line(names_up, times1_up, prices1_up, times2_up, prices2_up, color=up_color, width=width,
                                      ray=ray)
            if len(names_down) > 0:
                self.chart_tool.trend_line(names_down, times1_down, prices1_down, times2_down, prices2_down, color=up_color,
                                      width=width, ray=ray)

            # Left Extend Up Channel

            names_up, times1_up, prices1_up, times2_up, prices2_up = [], [], [], [], []
            names_down, times1_down, prices1_down, times2_down, prices2_down = [], [], [], [], []

            if self.last_up_channel_date is not None:
                if self.last_up_channel_date != self.data[self.up_channels[-1]['UpLine']['x'][0]]['Time']:
                    x_left = max(min(self.up_channels[-1]['UpLine']['x'][0],
                                     self.up_channels[-1]['DownLine']['x'][0]) - self.extend_number, 0)
                    y1 = np.polyval(self.up_channels[-1]['UpLine']['line'], x_left)
                    y2 = np.polyval(self.up_channels[-1]['DownLine']['line'], x_left)
                    self.append_line(f"UpChannel_UpLine_LeftExtend{self.up_counter}", x_left, self.up_channels[-1]['UpLine']['x'][0], y1,
                                     self.up_channels[-1]['UpLine']['y'][0], names_up, times1_up, prices1_up, times2_up,
                                     prices2_up)
                    self.append_line(f"UpChannel_DownLine_LeftExtend{self.up_counter}", x_left, self.up_channels[-1]['DownLine']['x'][0],
                                     y2,
                                     self.up_channels[-1]['DownLine']['y'][0], names_down, times1_down, prices1_down,
                                     times2_down, prices2_down)
            else:
                for i in range(len(self.up_channels)):
                    if self.last_up_channel_date is not None:
                        continue
                    x_left = max(min(self.up_channels[i]['UpLine']['x'][0],
                                     self.up_channels[i]['DownLine']['x'][0]) - self.extend_number, 0)
                    y1 = np.polyval(self.up_channels[i]['UpLine']['line'], x_left)
                    y2 = np.polyval(self.up_channels[i]['DownLine']['line'], x_left)
                    self.append_line(f"UpChannel_UpLine_LeftExtend{i}", x_left, self.up_channels[i]['UpLine']['x'][0], y1,
                                     self.up_channels[i]['UpLine']['y'][0], names_up, times1_up, prices1_up, times2_up,
                                     prices2_up)
                    self.append_line(f"UpChannel_DownLine_LeftExtend{i}", x_left, self.up_channels[i]['DownLine']['x'][0], y2,
                                     self.up_channels[i]['DownLine']['y'][0], names_down, times1_down, prices1_down,
                                     times2_down, prices2_down)

            if len(names_up) > 0:
                self.chart_tool.trend_line(names_up, times1_up, prices1_up, times2_up, prices2_up, color=up_color,
                                      ray=ray, style=extend_style)
            if len(names_down) > 0:
                self.chart_tool.trend_line(names_down, times1_down, prices1_down, times2_down, prices2_down, color=up_color,
                                      ray=ray, style=extend_style)

            # Right Extend Up Channel
            names_up, times1_up, prices1_up, times2_up, prices2_up = [], [], [], [], []
            names_down, times1_down, prices1_down, times2_down, prices2_down = [], [], [], [], []
            if self.last_up_channel_date is not None:
                if self.last_up_channel_date != self.data[self.up_channels[-1]['UpLine']['x'][0]]['Time']:
                    x_right = max(self.up_channels[-1]['UpLine']['x'][1], self.up_channels[-1]['DownLine']['x'][1]) + self.extend_number
                    y1 = np.polyval(self.up_channels[-1]['UpLine']['line'], x_right)
                    y2 = np.polyval(self.up_channels[-1]['DownLine']['line'], x_right)
                    t1 = self.data[self.up_channels[-1]['UpLine']['x'][1]]['Time']
                    if x_right < len(self.data):
                        t2 = self.data[x_right]['Time']
                    else:
                        t2 = self.data[-1]['Time'] + (self.data[-1]['Time'] - self.data[-2]['Time']) * (
                                    x_right - len(self.data) + 1)
                    self.append_line2(f"UpChannel_UpLine_RightExtend{self.up_counter}", t1, t2,
                                      self.up_channels[-1]['UpLine']['y'][1], y1, names_up, times1_up, prices1_up, times2_up,
                                      prices2_up)
                    t1 = self.data[self.up_channels[-1]['DownLine']['x'][1]]['Time']
                    self.append_line2(f"UpChannel_DownLine_RightExtend{self.up_counter}", t1, t2,
                                      self.up_channels[-1]['DownLine']['y'][1], y2, names_down, times1_down, prices1_down,
                                      times2_down, prices2_down)
            else:
                for i in range(len(self.up_channels)):
                    if self.last_up_channel_date is not None:
                        continue
                    x_right = max(self.up_channels[i]['UpLine']['x'][1], self.up_channels[i]['DownLine']['x'][1]) + self.extend_number
                    y1 = np.polyval(self.up_channels[i]['UpLine']['line'], x_right)
                    y2 = np.polyval(self.up_channels[i]['DownLine']['line'], x_right)
                    t1 = self.data[self.up_channels[i]['UpLine']['x'][1]]['Time']
                    if x_right < len(self.data):
                        t2 = self.data[x_right]['Time']
                    else:
                        t2 = self.data[-1]['Time'] + (self.data[-1]['Time'] - self.data[-2]['Time'])*(x_right - len(self.data) + 1)
                    self.append_line2(f"UpChannel_UpLine_RightExtend{i}", t1, t2,
                                     self.up_channels[i]['UpLine']['y'][1], y1, names_up, times1_up, prices1_up, times2_up,
                                     prices2_up)
                    t1 = self.data[self.up_channels[i]['DownLine']['x'][1]]['Time']
                    self.append_line2(f"UpChannel_DownLine_RightExtend{i}", t1, t2,
                                     self.up_channels[i]['DownLine']['y'][1], y2, names_down, times1_down, prices1_down,
                                     times2_down, prices2_down)

            if len(names_up) > 0:
                self.chart_tool.trend_line(names_up, times1_up, prices1_up, times2_up, prices2_up, color=up_color,
                                      ray=ray, style=extend_style)
            if len(names_down) > 0:
                self.chart_tool.trend_line(names_down, times1_down, prices1_down, times2_down, prices2_down, color=up_color,
                                      ray=ray, style=extend_style)

            self.last_up_channel_date = self.data[self.up_channels[-1]['UpLine']['x'][0]]['Time']

        # # Main Down Channel

        if len(self.down_channels) > 0:
            names_up, times1_up, prices1_up, times2_up, prices2_up = [], [], [], [], []
            names_down, times1_down, prices1_down, times2_down, prices2_down = [], [], [], [], []
            self.last_down_channel = self.down_channels[-1]
            self.last_down_channel['UpLine']['Time'] = [self.data[self.last_down_channel['UpLine']['x'][0]]['Time'],
                                                        self.data[self.last_down_channel['UpLine']['x'][1]]['Time']]
            self.last_down_channel['DownLine']['Time'] = [self.data[self.last_down_channel['DownLine']['x'][0]]['Time'],
                                                          self.data[self.last_down_channel['DownLine']['x'][1]]['Time']]

            if self.last_down_channel_date is not None:
                if self.last_down_channel_date != self.data[self.down_channels[-1]['UpLine']['x'][0]]['Time']:
                    self.down_counter += 1
                    self.append_line(f"DownChannel_UpLine{self.down_counter}", self.down_channels[-1]['UpLine']['x'][0],
                                     self.down_channels[-1]['UpLine']['x'][1], self.down_channels[-1]['UpLine']['y'][0],
                                     self.down_channels[-1]['UpLine']['y'][1], names_up, times1_up, prices1_up, times2_up,
                                     prices2_up)
                    self.append_line(f"DownChannel_DownLine{self.down_counter}", self.down_channels[-1]['DownLine']['x'][0],
                                     self.down_channels[-1]['DownLine']['x'][1], self.down_channels[-1]['DownLine']['y'][0],
                                     self.down_channels[-1]['DownLine']['y'][1], names_down, times1_down, prices1_down,
                                     times2_down, prices2_down)
            else:
                for i in range(len(self.down_channels)):
                    self.append_line(f"DownChannel_UpLine{i}", self.down_channels[i]['UpLine']['x'][0],
                                     self.down_channels[i]['UpLine']['x'][1], self.down_channels[i]['UpLine']['y'][0],
                                     self.down_channels[i]['UpLine']['y'][1], names_up, times1_up, prices1_up, times2_up,
                                     prices2_up)
                    self.append_line(f"DownChannel_DownLine{i}", self.down_channels[i]['DownLine']['x'][0],
                                     self.down_channels[i]['DownLine']['x'][1], self.down_channels[i]['DownLine']['y'][0],
                                     self.down_channels[i]['DownLine']['y'][1], names_down, times1_down, prices1_down,
                                     times2_down,
                                     prices2_down)
                    self.down_counter += 1


            if len(names_up) > 0:
                self.chart_tool.trend_line(names_up, times1_up, prices1_up, times2_up, prices2_up, color=down_color,
                                      width=width, ray=ray)
            if len(names_down) > 0:
                self.chart_tool.trend_line(names_down, times1_down, prices1_down, times2_down, prices2_down, color=down_color,
                                      width=width, ray=ray)

            # Left Extend Down Channel
            names_up, times1_up, prices1_up, times2_up, prices2_up = [], [], [], [], []
            names_down, times1_down, prices1_down, times2_down, prices2_down = [], [], [], [], []

            if self.last_down_channel_date is not None:
                if self.last_down_channel_date != self.data[self.down_channels[-1]['UpLine']['x'][0]]['Time']:
                    x_left = max(min(self.down_channels[-1]['UpLine']['x'][0],
                                     self.down_channels[-1]['DownLine']['x'][0]) - self.extend_number, 0)
                    y1 = np.polyval(self.down_channels[-1]['UpLine']['line'], x_left)
                    y2 = np.polyval(self.down_channels[-1]['DownLine']['line'], x_left)
                    self.append_line(f"DownChannel_UpLine_LeftExtend{self.down_counter}", x_left, self.down_channels[-1]['UpLine']['x'][0],
                                     y1,
                                     self.down_channels[-1]['UpLine']['y'][0], names_up, times1_up, prices1_up, times2_up,
                                     prices2_up)
                    self.append_line(f"DownChannel_DownLine_LeftExtend{self.down_counter}", x_left,
                                     self.down_channels[-1]['DownLine']['x'][0],
                                     y2,
                                     self.down_channels[-1]['DownLine']['y'][0], names_down, times1_down, prices1_down,
                                     times2_down, prices2_down)
            else:
                for i in range(len(self.down_channels)):
                    x_left = max(min(self.down_channels[i]['UpLine']['x'][0],
                                     self.down_channels[i]['DownLine']['x'][0]) - self.extend_number, 0)
                    y1 = np.polyval(self.down_channels[i]['UpLine']['line'], x_left)
                    y2 = np.polyval(self.down_channels[i]['DownLine']['line'], x_left)
                    self.append_line(f"DownChannel_UpLine_LeftExtend{i}", x_left, self.down_channels[i]['UpLine']['x'][0], y1,
                                     self.down_channels[i]['UpLine']['y'][0], names_up, times1_up, prices1_up, times2_up,
                                     prices2_up)
                    self.append_line(f"DownChannel_DownLine_LeftExtend{i}", x_left, self.down_channels[i]['DownLine']['x'][0],
                                     y2,
                                     self.down_channels[i]['DownLine']['y'][0], names_down, times1_down, prices1_down,
                                     times2_down, prices2_down)

            if len(names_up) > 0:
                self.chart_tool.trend_line(names_up, times1_up, prices1_up, times2_up, prices2_up, color=down_color,
                                      ray=ray, style=extend_style)
            if len(names_down) > 0:
                self.chart_tool.trend_line(names_down, times1_down, prices1_down, times2_down, prices2_down, color=down_color,
                                      width=width, ray=ray, style=extend_style)

            # Right Extend Down Channel
            names_up, times1_up, prices1_up, times2_up, prices2_up = [], [], [], [], []
            names_down, times1_down, prices1_down, times2_down, prices2_down = [], [], [], [], []

            if self.last_down_channel_date is not None:
                if self.last_down_channel_date != self.data[self.down_channels[-1]['UpLine']['x'][0]]['Time']:
                    x_right = max(self.down_channels[-1]['UpLine']['x'][1], self.down_channels[-1]['DownLine']['x'][1]) + self.extend_number
                    y1 = np.polyval(self.down_channels[-1]['UpLine']['line'], x_right)
                    y2 = np.polyval(self.down_channels[-1]['DownLine']['line'], x_right)
                    t1 = self.data[self.down_channels[-1]['UpLine']['x'][1]]['Time']
                    if x_right < len(self.data):
                        t2 = self.data[x_right]['Time']
                    else:
                        t2 = self.data[-1]['Time'] + (self.data[-1]['Time'] - self.data[-2]['Time']) * (
                                    x_right - len(self.data) + 1)
                    self.append_line2(f"DownChannel_UpLine_RightExtend{self.down_counter}", t1, t2,
                                      self.down_channels[-1]['UpLine']['y'][1], y1, names_up, times1_up, prices1_up,
                                      times2_up,
                                      prices2_up)
                    t1 = self.data[self.down_channels[-1]['DownLine']['x'][1]]['Time']
                    self.append_line2(f"DownChannel_DownLine_RightExtend{self.down_counter}", t1, t2,
                                      self.down_channels[-1]['DownLine']['y'][1], y2, names_down, times1_down, prices1_down,
                                      times2_down, prices2_down)
            else:
                for i in range(len(self.down_channels)):
                    x_right = min(max(self.down_channels[i]['UpLine']['x'][1],
                                      self.down_channels[i]['DownLine']['x'][1]) + self.extend_number, len(self.data) - 1)
                    y1 = np.polyval(self.down_channels[i]['UpLine']['line'], x_right)
                    y2 = np.polyval(self.down_channels[i]['DownLine']['line'], x_right)
                    t1 = self.data[self.down_channels[i]['UpLine']['x'][1]]['Time']
                    if x_right < len(self.data):
                        t2 = self.data[x_right]['Time']
                    else:
                        t2 = self.data[-1]['Time'] + (self.data[-1]['Time'] - self.data[-2]['Time'])*(x_right - len(self.data) + 1)
                    self.append_line2(f"DownChannel_UpLine_RightExtend{i}", t1, t2,
                                     self.down_channels[i]['UpLine']['y'][1], y1, names_up, times1_up, prices1_up, times2_up,
                                     prices2_up)
                    t1 = self.data[self.down_channels[i]['DownLine']['x'][1]]['Time']
                    self.append_line2(f"DownChannel_DownLine_RightExtend{i}", t1, t2,
                                     self.down_channels[i]['DownLine']['y'][1], y2, names_down, times1_down, prices1_down,
                                     times2_down, prices2_down)

            if len(names_up) > 0:
                self.chart_tool.trend_line(names_up, times1_up, prices1_up, times2_up, prices2_up, color=down_color,
                                      ray=ray, style=extend_style)
            if len(names_down) > 0:
                self.chart_tool.trend_line(names_down, times1_down, prices1_down, times2_down, prices2_down, color=down_color,
                                      width=width, ray=ray, style=extend_style)

            self.last_down_channel_date = self.data[self.down_channels[-1]['UpLine']['x'][0]]['Time']

    def append_line(self, name, x1, x2, y1, y2, names, times1, prices1, times2, prices2):
        names.append(name)
        times1.append(self.data[x1]['Time'])
        prices1.append(y1)
        times2.append(self.data[x2]['Time'])
        prices2.append(y2)

    def append_line2(self, name, time1, time2, y1, y2, names, times1, prices1, times2, prices2):
        names.append(name)
        times1.append(time1)
        prices1.append(y1)
        times2.append(time2)
        prices2.append(y2)

    def update_last_channel(self):
        if self.last_up_channel != None:
            self.last_up_channel['UpLine']['x'][1] -= 1
            self.last_up_channel['DownLine']['x'][1] -= 1
            if (self.data[-1]['Time'] - self.data[-2]['Time']) > (self.data[-2]['Time'] - self.data[-4]['Time']) and self.last_up_channel['UpLine']['Time'][1] > self.data[0]['Time']:
                self.chart_tool.delete([f"UpChannel_DownLine_RightExtend{self.up_counter}", f"UpChannel_UpLine_RightExtend{self.up_counter}"])

                x_right = max(self.last_up_channel['UpLine']['x'][1],
                              self.last_up_channel['DownLine']['x'][1]) + self.extend_number
                y1 = np.polyval(self.last_up_channel['UpLine']['line'], x_right)
                y2 = np.polyval(self.last_up_channel['DownLine']['line'], x_right)
                t1_up = self.last_up_channel['UpLine']['Time'][1]
                if x_right < len(self.data):
                    t2 = self.data[x_right]['Time']
                else:
                    t2 = self.data[-1]['Time'] + (self.data[-2]['Time'] - self.data[-3]['Time']) * (x_right - len(self.data) + 1)

                t1_down = self.last_up_channel['DownLine']['Time'][1]

                self.chart_tool.trend_line([f"UpChannel_DownLine_RightExtend{self.up_counter}", f"UpChannel_UpLine_RightExtend{self.up_counter}"],
                                           [t1_down, t1_up], [self.last_up_channel['DownLine']['y'][1], self.last_up_channel['UpLine']['y'][1]],
                                           [t2, t2], [y2, y1], color=self.up_color,
                                               ray=self.ray, style=self.extend_style)

        if self.last_down_channel != None:
            self.last_down_channel['UpLine']['x'][1] -= 1
            self.last_down_channel['DownLine']['x'][1] -= 1
            if (self.data[-1]['Time'] - self.data[-2]['Time']) > (self.data[-2]['Time'] - self.data[-4]['Time']) and self.last_down_channel['UpLine']['Time'][1] > self.data[0]['Time']:
                self.chart_tool.delete([f"DownChannel_DownLine_RightExtend{self.down_counter}", f"DownChannel_UpLine_RightExtend{self.down_counter}"])

                x_right = max(self.last_down_channel['UpLine']['x'][1],
                              self.last_down_channel['DownLine']['x'][1]) + self.extend_number
                y1 = np.polyval(self.last_down_channel['UpLine']['line'], x_right)
                y2 = np.polyval(self.last_down_channel['DownLine']['line'], x_right)
                t1_up = self.last_down_channel['UpLine']['Time'][1]
                if x_right < len(self.data):
                    t2 = self.data[x_right]['Time']
                else:
                    t2 = self.data[-1]['Time'] + (self.data[-2]['Time'] - self.data[-3]['Time']) * (
                            x_right - len(self.data) + 1)

                t1_down = self.last_down_channel['DownLine']['Time'][1]

                self.chart_tool.trend_line([f"DownChannel_DownLine_RightExtend{self.down_counter}", f"DownChannel_UpLine_RightExtend{self.down_counter}"],
                                       [t1_down, t1_up], [self.last_down_channel['DownLine']['y'][1], self.last_down_channel['UpLine']['y'][1]],
                                       [t2, t2], [y2, y1], color=self.down_color,
                                           ray=self.ray, style=self.extend_style)
