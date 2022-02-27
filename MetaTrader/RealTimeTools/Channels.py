from MetaTrader.MetaTraderBase import MetaTraderBase
from MetaTrader.RealTimeTools.RealTimeTool import RealTimeTool

from AlgorithmFactory.AlgorithmTools.LocalExtermums import *


from AlgorithmFactory.AlgorithmTools.Channels import get_channels
from AlgorithmFactory.AlgorithmTools.ParallelChannels import get_parallel_channels


class Channel(RealTimeTool):

    def __init__(self, chart_tool: MetaTraderBase, data, symbol, window, extremum_window_start, extremum_window_end,
                 extremum_window_step, extremum_mode, check_window, alpha, beta, convergence, divergence, extend_multiplier, type, telegram):
        super().__init__(chart_tool, data)

        self.telegram_channel_name = "@polaris_channels"

        self.window = window
        self.symbol = symbol
        self.extend_multiplier = extend_multiplier
        self.extremum_window_start = extremum_window_start
        self.extremum_window_end = extremum_window_end
        self.extremum_window_step = extremum_window_step
        self.extremum_mode = extremum_mode
        self.check_window = check_window
        self.alpha = alpha
        self.beta = beta
        self.type = type
        self.convergence = convergence
        self.divergence = divergence
        self.telegram = telegram

        self.last_up_channel_date = None
        self.last_down_channel_date = None

        self.last_up_channel = None
        self.last_down_channel = None

        self.up_counter = -1
        self.down_counter = -1

        self.ray = 0
        self.width = 2
        self.up_color = "80,197,133"
        self.down_color = "255,36,36"
        self.extend_style = self.chart_tool.EnumStyle.DashDotDot
        self.extend_width = 1
        self.last_channel_type = 0

        self.caclulate()
        self.draw()
        if self.last_up_channel_date is None:
            self.last_up_channel_date = self.data[-1]['Time']
        if self.last_down_channel_date is None:
            self.last_down_channel_date = self.data[-1]['Time']

        if self.telegram:
            self.chart_tool.clear()

        self.data = self.data[-self.window:]

        self.chart_tool.set_speed(1000)
        self.chart_tool.set_candle_start_delay(10)

    def on_tick(self, time, bid, ask):
        pass

    def on_data(self, candle):

        self.caclulate()
        self.draw()
        self.update_last_channel()

        self.data.pop(0)
        self.data.append(candle)

    def caclulate(self):
        if self.type == 'monotone':
            self.up_channels, self.down_channels = get_channels(self.data, self.extremum_window_start, self.extremum_window_end,
                                                                self.extremum_window_step, self.extremum_mode, self.check_window,
                                                                self.alpha, self.beta, self.convergence, self.divergence, 2)
        elif self.type == 'betweenness':
            self.up_channels, self.down_channels = get_parallel_channels(self.data, self.extremum_window_start,
                                                                         self.extremum_window_end, self.extremum_window_step,
                                                                         self.extremum_mode, self.check_window, self.alpha, self.beta)

    def draw(self):
        # # Up Channel
        if len(self.up_channels) > 0:
            self.up_counter, self.last_up_channel, self.last_up_channel_date, new_channel = \
                self.draw_channel("UpChannel", self.up_channels, self.up_counter, self.last_up_channel_date, self.last_up_channel, self.up_color)
            if self.telegram and new_channel:
                self.last_channel_type = 1
                self.take_photo("Up Channel", self.up_counter, self.last_up_channel)

        # # Down Channel
        if len(self.down_channels) > 0:
            self.down_counter, self.last_down_channel, self.last_down_channel_date, new_channel = \
                self.draw_channel("DownChannel", self.down_channels, self.down_counter, self.last_down_channel_date, self.last_down_channel, self.down_color)
            if self.telegram and new_channel:
                self.last_channel_type = -1
                self.take_photo("Down Channel", self.down_counter, self.last_down_channel)

    def take_photo(self, name, counter, last_channel):
        self.chart_tool.set_speed(0.01)
        if last_channel is not None:
            scale = self.calculate_scale(last_channel)
            self.chart_tool.set_scale(self.symbol, scale)

        self.chart_tool.take_screen_shot(f"{self.symbol}_{name}{counter}", self.symbol)
        self.chart_tool.send_telegram_photo(f"{self.chart_tool.screen_shots_directory}/{self.symbol}_{name}{counter}.png",
                                            self.telegram_channel_name)
        self.chart_tool.send_telegram_message(f"{name} Detected\nSymbol : {self.symbol}"
                                              f"\nTime : {self.data[-1]['Time']}\nScale : {last_channel['Window']}",
                                              self.telegram_channel_name)
        self.chart_tool.set_speed(1000)

    def calculate_scale(self, last_channel):
        bars = (len(self.data) - min(last_channel['UpLine']['x'][0], last_channel['DownLine']['x'][0])) * 2
        if bars < 33:
            scale = 5
        elif bars < 68:
            scale = 4
        elif bars < 138:
            scale = 3
        elif bars < 279:
            scale = 2
        elif bars < 560:
            scale = 1
        else:
            scale = 0
        print(f"{bars} - {scale}")
        return scale

    def update_last_channel(self):
        if self.last_up_channel != None:
            self.update_channel_index(self.last_up_channel)
            if (self.data[-1]['Time'] - self.data[-2]['Time']) > (self.data[-2]['Time'] - self.data[-4]['Time']) and self.last_up_channel['UpLine']['Time'][1] > self.data[0]['Time']:
                if self.telegram and self.last_channel_type != 1:
                    return
                self.chart_tool.delete([f"UpChannel_DownLine_RightExtend{self.up_counter}", f"UpChannel_UpLine_RightExtend{self.up_counter}"])

                extend_number = self.get_extend_number(self.last_up_channel)
                x_right = max(self.last_up_channel['UpLine']['x'][1],
                              self.last_up_channel['DownLine']['x'][1]) + extend_number
                up_line = np.polyfit([self.last_up_channel['UpLine']['x'][0], self.last_up_channel['UpLine']['x'][1]],
                                     [self.last_up_channel['UpLine']['y'][0], self.last_up_channel['UpLine']['y'][1]], 1)
                down_line = np.polyfit([self.last_up_channel['DownLine']['x'][0], self.last_up_channel['DownLine']['x'][1]],
                                     [self.last_up_channel['DownLine']['y'][0], self.last_up_channel['DownLine']['y'][1]], 1)
                y1 = np.polyval(up_line, x_right)
                y2 = np.polyval(down_line, x_right)

                if x_right < len(self.data):
                    t2 = self.data[x_right]['Time']
                else:
                    t2 = self.data[-1]['Time'] + (self.data[-2]['Time'] - self.data[-3]['Time']) * (x_right - len(self.data) + 1)

                t1_up = self.last_up_channel['UpLine']['Time'][1]
                t1_down = self.last_up_channel['DownLine']['Time'][1]

                self.chart_tool.trend_line([f"UpChannel_DownLine_RightExtend{self.up_counter}", f"UpChannel_UpLine_RightExtend{self.up_counter}"],
                                           [t1_down, t1_up], [self.last_up_channel['DownLine']['y'][1], self.last_up_channel['UpLine']['y'][1]],
                                           [t2, t2], [y2, y1], color=self.up_color,
                                               ray=self.ray, style=self.extend_style, width=self.extend_width)

        if self.last_down_channel != None:
            self.update_channel_index(self.last_down_channel)
            if (self.data[-1]['Time'] - self.data[-2]['Time']) > (self.data[-2]['Time'] - self.data[-4]['Time']) and self.last_down_channel['UpLine']['Time'][1] > self.data[0]['Time']:
                if self.telegram and self.last_channel_type != -1:
                    return
                self.chart_tool.delete([f"DownChannel_DownLine_RightExtend{self.down_counter}", f"DownChannel_UpLine_RightExtend{self.down_counter}"])
                extend_number = self.get_extend_number(self.last_down_channel)
                x_right = max(self.last_down_channel['UpLine']['x'][1],
                              self.last_down_channel['DownLine']['x'][1]) + extend_number
                up_line = np.polyfit([self.last_down_channel['UpLine']['x'][0], self.last_down_channel['UpLine']['x'][1]],
                                     [self.last_down_channel['UpLine']['y'][0], self.last_down_channel['UpLine']['y'][1]],1)
                down_line = np.polyfit([self.last_down_channel['DownLine']['x'][0], self.last_down_channel['DownLine']['x'][1]],
                                        [self.last_down_channel['DownLine']['y'][0], self.last_down_channel['DownLine']['y'][1]], 1)
                y1 = np.polyval(up_line, x_right)
                y2 = np.polyval(down_line, x_right)

                if x_right < len(self.data):
                    t2 = self.data[x_right]['Time']
                else:
                    t2 = self.data[-1]['Time'] + (self.data[-2]['Time'] - self.data[-3]['Time']) * (x_right - len(self.data) + 1)

                t1_up = self.last_down_channel['UpLine']['Time'][1]
                t1_down = self.last_down_channel['DownLine']['Time'][1]

                self.chart_tool.trend_line([f"DownChannel_DownLine_RightExtend{self.down_counter}", f"DownChannel_UpLine_RightExtend{self.down_counter}"],
                                       [t1_down, t1_up], [self.last_down_channel['DownLine']['y'][1], self.last_down_channel['UpLine']['y'][1]],
                                       [t2, t2], [y2, y1], color=self.down_color,
                                           ray=self.ray, style=self.extend_style, width=self.extend_width)

    def draw_channel(self, name, channels, counter, last_channel_date, last_channel, color):

        new_channel = False
        names_up, times1_up, prices1_up, times2_up, prices2_up = [], [], [], [], []
        names_down, times1_down, prices1_down, times2_down, prices2_down = [], [], [], [], []
        if last_channel_date is not None:
            new_channel_time = self.data[max(channels[-1]['UpLine']['x'][1],
                                                         channels[-1]['DownLine']['x'][1])]['Time']
            if last_channel_date < new_channel_time and self.data[-channels[-1]['Window']-2]['Time'] < new_channel_time:
                if last_channel is None or not self.is_similar(channels[-1], last_channel):
                    # Main line
                    if self.telegram:
                        self.chart_tool.clear()
                    new_channel = True
                    last_channel = channels[-1]
                    counter += 1
                    self.add_main_channel(name, channels, counter, -1, names_up, times1_up,
                                          prices1_up, times2_up, prices2_up,
                                          names_down, times1_down, prices1_down, times2_down, prices2_down)
                    self.draw_lines(names_up, times1_up, prices1_up, times2_up, prices2_up, names_down, times1_down,
                                    prices1_down, times2_down, prices2_down, color, self.ray, width=self.width)
                    # Left Extended
                    names_up, times1_up, prices1_up, times2_up, prices2_up = [], [], [], [], []
                    names_down, times1_down, prices1_down, times2_down, prices2_down = [], [], [], [], []
                    self.add_left_extend_channel(name, channels, counter, -1, names_up, times1_up,
                                                 prices1_up, times2_up, prices2_up,
                                                 names_down, times1_down, prices1_down, times2_down, prices2_down)
                    self.draw_lines(names_up, times1_up, prices1_up, times2_up, prices2_up, names_down, times1_down,
                                    prices1_down, times2_down, prices2_down, color, self.ray, self.extend_width, self.extend_style)
                    #RightExtended
                    names_up, times1_up, prices1_up, times2_up, prices2_up = [], [], [], [], []
                    names_down, times1_down, prices1_down, times2_down, prices2_down = [], [], [], [], []
                    self.add_right_extend_channel(name, channels, counter, -1, names_up, times1_up,
                                                  prices1_up, times2_up, prices2_up,
                                                  names_down, times1_down, prices1_down, times2_down, prices2_down)
                    self.draw_lines(names_up, times1_up, prices1_up, times2_up, prices2_up, names_down, times1_down,
                                    prices1_down, times2_down, prices2_down, color, self.ray, self.extend_width, self.extend_style)

                    last_channel_date = self.data[max(channels[-1]['UpLine']['x'][1],
                                                      channels[-1]['DownLine']['x'][1])]['Time']
        else:
            # Main Lines
            for i in range(len(channels)):
                self.add_main_channel(name, channels, i, i, names_up, times1_up, prices1_up, times2_up,
                                      prices2_up,
                                      names_down, times1_down, prices1_down, times2_down, prices2_down)
                counter += 1
            self.draw_lines(names_up, times1_up, prices1_up, times2_up, prices2_up, names_down, times1_down,
                            prices1_down, times2_down, prices2_down, color, self.ray, width=self.width)
            # Left Extended
            names_up, times1_up, prices1_up, times2_up, prices2_up = [], [], [], [], []
            names_down, times1_down, prices1_down, times2_down, prices2_down = [], [], [], [], []
            for i in range(len(channels)):
                if last_channel_date is not None:
                    continue
                self.add_left_extend_channel(name, channels, i, i, names_up, times1_up, prices1_up,
                                             times2_up, prices2_up,
                                             names_down, times1_down, prices1_down, times2_down, prices2_down)
            self.draw_lines(names_up, times1_up, prices1_up, times2_up, prices2_up, names_down, times1_down,
                            prices1_down, times2_down, prices2_down, color, self.ray, self.extend_width, self.extend_style)
            # Right Extended
            names_up, times1_up, prices1_up, times2_up, prices2_up = [], [], [], [], []
            names_down, times1_down, prices1_down, times2_down, prices2_down = [], [], [], [], []
            for i in range(len(channels)):
                if last_channel_date is not None:
                    continue
                self.add_right_extend_channel(name, channels, i, i, names_up, times1_up, prices1_up,
                                              times2_up, prices2_up,
                                              names_down, times1_down, prices1_down, times2_down, prices2_down)
            self.draw_lines(names_up, times1_up, prices1_up, times2_up, prices2_up, names_down, times1_down,
                            prices1_down, times2_down, prices2_down, color, self.ray, self.extend_width, self.extend_style)

            last_channel_date = self.data[max(channels[-1]['UpLine']['x'][1],
                                                      channels[-1]['DownLine']['x'][1])]['Time']

        return counter, last_channel, last_channel_date, new_channel

    def add_main_channel(self, name, channels, id, index, names_up, times1_up, prices1_up, times2_up, prices2_up, names_down,
                         times1_down, prices1_down, times2_down, prices2_down):
        self.append_line(f"{name}_UpLine{id}_{channels[index]['Window']}", channels[index]['UpLine']['x'][0],
                         channels[index]['UpLine']['x'][1], channels[index]['UpLine']['y'][0],
                         channels[index]['UpLine']['y'][1], names_up, times1_up, prices1_up, times2_up,
                         prices2_up)
        self.append_line(f"{name}_DownLine{id}_{channels[index]['Window']}", channels[index]['DownLine']['x'][0], channels[index]['DownLine']['x'][1],
                         channels[index]['DownLine']['y'][0], channels[index]['DownLine']['y'][1], names_down, times1_down,
                         prices1_down, times2_down, prices2_down)

    def add_left_extend_channel(self, name, channels, id, index, names_up, times1_up, prices1_up, times2_up, prices2_up, names_down,
                         times1_down, prices1_down, times2_down, prices2_down):
        extend_number = self.get_extend_number(channels[index])
        x_left = max(min(channels[index]['UpLine']['x'][0],
                         channels[index]['DownLine']['x'][0]) - (extend_number // 2), 0)
        y1 = np.polyval(channels[index]['UpLine']['line'], x_left)
        y2 = np.polyval(channels[index]['DownLine']['line'], x_left)
        self.append_line(f"{name}_UpLine_LeftExtend{id}", x_left, channels[index]['UpLine']['x'][0], y1,
                         channels[index]['UpLine']['y'][0], names_up, times1_up, prices1_up, times2_up,
                         prices2_up)
        self.append_line(f"{name}_DownLine_LeftExtend{id}", x_left, channels[index]['DownLine']['x'][0], y2,
                         channels[index]['DownLine']['y'][0], names_down, times1_down, prices1_down, times2_down,
                         prices2_down)

    def add_right_extend_channel(self, name, channels, id, index, names_up, times1_up, prices1_up, times2_up, prices2_up, names_down,
                         times1_down, prices1_down, times2_down, prices2_down):
        extend_number = self.get_extend_number(channels[index])
        x_right = max(channels[index]['UpLine']['x'][1],
                      channels[index]['DownLine']['x'][1]) + extend_number
        y1 = np.polyval(channels[index]['UpLine']['line'], x_right)
        y2 = np.polyval(channels[index]['DownLine']['line'], x_right)
        t1 = self.data[channels[index]['UpLine']['x'][1]]['Time']
        if x_right < len(self.data):
            t2 = self.data[x_right]['Time']
        else:
            t2 = self.data[-1]['Time'] + (self.data[-1]['Time'] - self.data[-2]['Time']) * (
                    x_right - len(self.data) + 1)
        self.append_line2(f"{name}_UpLine_RightExtend{id}", t1, t2,
                          channels[index]['UpLine']['y'][1], y1, names_up, times1_up, prices1_up, times2_up,
                          prices2_up)
        t1 = self.data[channels[index]['DownLine']['x'][1]]['Time']
        self.append_line2(f"{name}_DownLine_RightExtend{id}", t1, t2,
                          channels[index]['DownLine']['y'][1], y2, names_down, times1_down, prices1_down,
                          times2_down, prices2_down)

    def draw_lines(self, names_up, times1_up, prices1_up, times2_up, prices2_up, names_down, times1_down, prices1_down,
                   times2_down, prices2_down, color, ray, width, style=0):
        if len(names_up) > 0:
            self.chart_tool.trend_line(names_up, times1_up, prices1_up, times2_up, prices2_up, color=color,
                                       ray=ray, width=width, style=style)
        if len(names_down) > 0:
            self.chart_tool.trend_line(names_down, times1_down, prices1_down, times2_down, prices2_down,
                                       color=color, ray=ray, width=width, style=style)

    def get_extend_number(self,channel):
        return int((max(channel['UpLine']['x'][1], channel['DownLine']['x'][1]) -
                             min(channel['UpLine']['x'][0],
                                 channel['DownLine']['x'][0])) * self.extend_multiplier)

    @staticmethod
    def update_channel_index(channel):
        channel['UpLine']['x'][1] -= 1
        channel['DownLine']['x'][1] -= 1
        channel['UpLine']['x'][0] -= 1
        channel['DownLine']['x'][0] -= 1

    @staticmethod
    def is_similar(channel1, channel2):
        if abs(max(channel2['UpLine']['x'][1], channel2['DownLine']['x'][1]) - max(channel1['UpLine']['x'][1], channel1['DownLine']['x'][1])) < min(channel1['Window'], channel2['Window']):
            return True
        return False

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