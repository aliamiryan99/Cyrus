from MetaTrader.MetaTraderBase import MetaTraderBase
from MetaTrader.RealTimeTools.RealTimeTool import RealTimeTool

from AlgorithmFactory.AlgorithmTools.LocalExtermums import *
from AlgorithmFactory.AlgorithmPackages.Trend.TrendChannelDetection import *

from Configuration.Trade.OnlineConfig import Config

import copy


class TrendChannels(RealTimeTool):

    def __init__(self, chart_tool: MetaTraderBase, data, symbol, consecutive_ext_num, window_left, window_right, mode, extremum_show):
        super().__init__(chart_tool, data)

        self.chart_tool.set_speed(1000)
        self.chart_tool.set_candle_start_delay(3)

        self.consecutive_ext_num = consecutive_ext_num
        self.window = window_left
        self.window_right = window_right
        self.mode = mode
        self.extremum_show = extremum_show

        self.bull_color = "50,50,250"
        self.bear_color = "250,50,50"

        open, high, low, close = get_ohlc(data)

        times = [row['Time'] for row in self.data]

        self.local_min, self.local_max = get_local_extermums_asymetric(self.data, window_left, window_right, mode)

        self.y_scale = 10 ** (Config.symbols_pip[symbol]-1) / ((max(high)-min(low)) * 10 ** (Config.symbols_pip[symbol]-1) / 1500)
        print(self.y_scale)

        bull_channels, bear_channels = detect_trend_channels(self.local_max, self.local_min, times, high, low, consecutive_ext_num, self.y_scale)

        # Save Last Channels
        self.last_bull_channel = bull_channels[-1]
        self.last_bear_channel = bear_channels[-1]

        self.bull_channel_id = 1
        self.bear_channel_id = 1
        self.draw_channels(bull_channels, "Bull", self.bull_color)
        self.draw_channels(bear_channels, "Bear", self.bear_color)

        self.last_local_min, self.last_local_max = self.local_min[-1], self.local_max[-1]
        self.last_min_id, self.last_max_id = 1, 1
        self.last_min_delete, self.last_max_delete = 1, 1

        if self.extremum_show:
            self.draw_local_extremum(self.local_min, self.local_max)

        window = 1000
        self.data = self.data[-window:]

        self.update_local_ext_indices(len(data)- window)

        self.last_local_min, self.last_local_max = self.local_min[-1], self.local_max[-1]

    def on_tick(self, time, bid, ask):
        pass

    def on_data(self, candle):
        self.data.pop(0)

        print(self.chart_tool.get_equity())

        # Recalculate Extremums
        self.local_min, self.local_max = update_local_extremum_list(self.data, self.local_min, self.local_max, self.window, self.mode, asymetric=True, extremum_window_right=self.window_right)
        self.last_local_min, self.last_local_max = self.last_local_min-1, self.last_local_max-1
        # Recalculate Channels
        open, high, low, close = get_ohlc(self.data)
        times = [row['Time'] for row in self.data]
        bull_channels, bear_channels = detect_trend_channels(self.local_max, self.local_min, times, high, low, self.consecutive_ext_num, self.y_scale)

        if len(bear_channels) == 0:
            bear_channels.append(self.last_bear_channel)
        if len(bull_channels) == 0:
            bull_channels.append(self.last_bull_channel)

        self.redraw_channel(bull_channels[-1], bear_channels[-1])
        if self.extremum_show:
            self.redraw_extremums()
        self.data.append(candle)

    def redraw_channel(self, bull_channel, bear_channel):
        if bull_channel['DownLine']['StartTime'] == self.last_bull_channel['DownLine']['StartTime']:
            if bull_channel['UpLine']['EndTime'] > self.last_bull_channel['UpLine']['EndTime']:
                self.bull_channel_id -= 1
                self.delete_channel("Bull", self.bull_channel_id)
                self.draw_channels([bull_channel], "Bull", self.bull_color)
                self.last_bull_channel = bull_channel
        else:
            if bull_channel['UpLine']['EndTime'] != self.last_bull_channel['UpLine']['EndTime']:
                self.draw_channels([bull_channel], "Bull", self.bull_color)
                self.last_bull_channel = bull_channel

        if bear_channel['UpLine']['StartTime'] == self.last_bear_channel['UpLine']['StartTime']:
            if bear_channel['DownLine']['EndTime'] > self.last_bear_channel['DownLine']['EndTime']:
                self.bear_channel_id -= 1
                self.delete_channel("Bear", self.bear_channel_id)
                self.draw_channels([bear_channel], "Bear", self.bear_color)
                self.last_bear_channel = bear_channel
        else:
            if bear_channel['DownLine']['EndTime'] != self.last_bear_channel['DownLine']['EndTime']:
                self.draw_channels([bear_channel], "Bear", self.bear_color)
                self.last_bear_channel = bear_channel

    def delete_channel(self, type, id):
        names = [f"{type}Channel MidLine {id}", f"{type}Channel UpLine {id}", f"{type}Channel DownLine {id}",
                 f"{type}Channel InfoTxt {id}"]
        self.chart_tool.delete(names)

    def redraw_extremums(self):
        if self.local_min[-1] != self.last_local_min:
            self.draw_local_extremum([self.local_min[-1]], [])
            self.last_local_min = self.local_min[-1]
            print(f"Local Min Time {self.data[self.local_min[-1]]['Time']}")
        if self.local_max[-1] != self.last_local_max:
            self.draw_local_extremum([], [self.local_max[-1]])
            self.last_local_max = self.local_max[-1]
            print(f"Local Max Time {self.data[self.local_max[-1]]['Time']}")

    def correct_end_of_week(self, candle):
        if candle['Time'] - self.data[-1]['Time'] > max(self.data[-1]['Time'] - self.data[-2]['Time'],
                                                        self.data[-2]['Time'] - self.data[-3]['Time']):
            if self.last_bull_channel['DownLine']['EndTime'] > self.data[-1]['Time']:
                self.last_bull_channel['DownLine']['EndTime'] += (candle['Time'] - self.data[-1]['Time']) -\
                                                                 (self.data[-1]['Time'] - self.data[-2]['Time'])
                self.bull_channel_id -= 1
                self.delete_channel("Bull", self.bull_channel_id)
                self.draw_channels([self.last_bull_channel], "Bull", self.bull_color)
            if self.last_bear_channel['UpLine']['EndTime'] > self.data[-1]['Time']:
                self.last_bear_channel['UpLine']['EndTime'] += (candle['Time'] - self.data[-1]['Time']) -\
                                                               (self.data[-1]['Time'] - self.data[-2]['Time'])
                self.bear_channel_id -= 1
                self.delete_channel("Bear", self.bear_channel_id)
                self.draw_channels([self.last_bear_channel], "Bear", self.bear_color)

    def draw_channels(self, channels, type, color):
        mid_names, mid_s_time, mid_e_time, mid_s_price, mid_e_price = [], [], [], [], []
        up_names, up_s_time, up_e_time, up_s_price, up_e_price = [], [], [], [], []
        down_names, down_s_time, down_e_time, down_s_price, down_e_price = [], [], [], [], []
        names_err, text_err, time_err, price_err = [], [], [], []
        anchor = self.chart_tool.EnumAnchor.Bottom
        for i in range(len(channels)):
            if type == "Bull":
                channel_id = self.bull_channel_id
            else:
                channel_id = self.bear_channel_id
            # # Mid line
            mid_names.append(f"{type}Channel MidLine {channel_id}")
            mid_s_time.append(channels[i]['MidLine']['StartTime'])
            mid_s_price.append(channels[i]['MidLine']['StartPrice'])
            mid_e_time.append(channels[i]['MidLine']['EndTime'])
            mid_e_price.append(channels[i]['MidLine']['EndPrice'])
            # Up line
            up_names.append(f"{type}Channel UpLine {channel_id}")
            up_s_time.append(channels[i]['UpLine']['StartTime'])
            up_s_price.append(channels[i]['UpLine']['StartPrice'])
            up_e_time.append(channels[i]['UpLine']['EndTime'])
            up_e_price.append(channels[i]['UpLine']['EndPrice'])
            # Donw Line
            down_names.append(f"{type}Channel DownLine {channel_id}")
            down_s_time.append(channels[i]['DownLine']['StartTime'])
            down_s_price.append(channels[i]['DownLine']['StartPrice'])
            down_e_time.append(channels[i]['DownLine']['EndTime'])
            down_e_price.append(channels[i]['DownLine']['EndPrice'])
            # Error Text
            names_err.append(f"{type}Channel InfoTxt {channel_id}")
            text_err.append(f"Slope:{channels[i]['Info']['Slope']},TN:{channels[i]['Info']['TopNears']},"
                            f"DN:{channels[i]['Info']['DownNears']}")
            if type == "Bull":
                time_err.append(channels[i]['UpLine']['EndTime'])
                price_err.append(channels[i]['UpLine']['EndPrice'])
                self.bull_channel_id += 1
            elif type == "Bear":
                time_err.append(channels[i]['DownLine']['EndTime'])
                price_err.append(channels[i]['DownLine']['EndPrice'])
                self.bear_channel_id += 1
                anchor = self.chart_tool.EnumAnchor.Top

        self.chart_tool.trend_line(mid_names, mid_s_time, mid_s_price, mid_e_time, mid_e_price, style=self.chart_tool.EnumStyle.DashDotDot)
        self.chart_tool.trend_line(up_names, up_s_time, up_s_price, up_e_time, up_e_price, color=color)
        self.chart_tool.trend_line(down_names, down_s_time, down_s_price, down_e_time, down_e_price, color=color)
        self.chart_tool.text(names_err, time_err, price_err, text_err, font_size=8, anchor=anchor)

    def draw_local_extremum(self, local_min, local_max):

        if len(local_min) != 0:
            times1, prices1, texts1, names1 = [], [], [], []
            for i in range(len(local_min)):
                times1.append(self.data[local_min[i]]['Time'])
                prices1.append(self.data[local_min[i]]['Low'])
                texts1.append(self.data[local_min[i]]['Low'])
                names1.append(f"LocalMinPython{self.last_min_id}")
                self.last_min_id += 1
            self.chart_tool.arrow_up(names1, times1, prices1, anchor=self.chart_tool.EnumArrowAnchor.Top, color="12,83,211")
        if len(local_max) != 0:
            times2, prices2, texts2, names2 = [], [], [], []
            for i in range(len(local_max)):
                times2.append(self.data[local_max[i]]['Time'])
                prices2.append(self.data[local_max[i]]['High'])
                texts2.append(self.data[local_max[i]]['High'])
                names2.append(f"LocalMaxPython{self.last_max_id}")
                self.last_max_id += 1
            self.chart_tool.arrow_down(names2, times2, prices2, anchor=self.chart_tool.EnumArrowAnchor.Bottom, color="211,83,12")

    def update_local_ext_indices(self, diff_index):
        i = 0
        while i < (len(self.local_min)):
            self.local_min[i] = self.local_min[i] - diff_index
            if self.local_min[i] < 0:
                self.local_min = np.delete(self.local_min, [i])
                i -= 1
            i += 1
        i = 0
        while i < (len(self.local_max)):
            self.local_max[i] = self.local_max[i] - diff_index
            if self.local_max[i] < 0:
                self.local_max = np.delete(self.local_max, [i])
                i -= 1
            i += 1