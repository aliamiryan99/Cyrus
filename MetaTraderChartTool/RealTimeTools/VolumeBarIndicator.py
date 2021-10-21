
from MetaTraderChartTool.BasicChartTools import BasicChartTools
from MetaTraderChartTool.RealTimeTools.RealTimeTool import RealTimeTool

from Indicators.VolumeBarIndicator import VolumeBar


class VolumeBarIndicator(RealTimeTool):

    def __init__(self, chart_tool: BasicChartTools, data, vb_time_frame_cnt):
        super().__init__(chart_tool, data)

        self.vb_time_frame_cnt = vb_time_frame_cnt

        self.volume_bar = VolumeBar(vb_time_frame_cnt)

        start_index, end_index = self.get_last_week_index(data)

        self.last_week_volume = 0
        for i in range(start_index, end_index):
            self.last_week_volume += data[i]['Volume']

        self.new_week = self.is_new_week(self.data[-1])

        self.new_week_volume = 0
        for i in range(len(self.data)-1, start_index+1, -1):
            self.new_week_volume += data[i]['Volume']

        self.volume_bars_size = len(self.volume_bar.total_data)

    def on_tick(self, time, bid, ask):
        tick = {'Time': time, 'Bid': bid, 'Ask': ask}
        self.new_week_volume += 1
        self.volume_bar.update(tick, self.last_week_volume, self.new_week)
        if self.new_week:
            self.new_week = False
        if len(self.volume_bar.total_data) != self.volume_bars_size and len(self.volume_bar.total_data) > 1:
            print("TrendLine")
            pre_vb = self.volume_bar.total_data[-2]
            vb = self.volume_bar.total_data[-1]
            self.volume_bars_size = len(self.volume_bar.total_data)
            self.chart_tool.trend_line([f"vb_{self.volume_bars_size}"], [pre_vb['Time']], [pre_vb['WAP']], [vb['Time']], [vb['WAP']])

    def on_data(self, candle):
        self.data.pop(0)

        self.new_week = self.is_new_week(candle)
        if self.new_week:
            self.last_week_volume = self.new_week_volume
            self.new_week_volume = 0

        self.data.append(candle)

    def get_last_week_index(self, data):
        last_week = -1
        end_last_week_index = -1
        start_last_week_index = -1
        current_week = data[-1]['Time'].isocalendar()[1]
        for i in range(len(data)-1, 0, -1):
            week = data[i]['Time'].isocalendar()[1]
            if week != current_week:
                last_week = week
                end_last_week_index = i
                break
        for i in range(end_last_week_index-1, 0, -1):
            week = data[i]['Time'].isocalendar()[1]
            if week != last_week:
                start_last_week_index = i+1

        return start_last_week_index, end_last_week_index

    def is_new_week(self, candle):
        current_week = candle['Time'].isocalendar()[1]
        pre_candle_week = self.data[-1]['Time'].isocalendar()[1]
        if current_week != pre_candle_week:
            return True
        return False
