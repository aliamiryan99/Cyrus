
from MetaTraderChartTool.Tools.Tool import Tool
from MetaTraderChartTool.BasicChartTools import BasicChartTools
from AlgorithmFactory.AlgorithmTools.LocalExtermums import *

from AlgorithmFactory.AlgorithmTools.Channels import get_channels


class Channels(Tool):

    def __init__(self, data, extremum_window_start, extremum_window_end, extremum_window_step, extremum_mode, check_window, alpha, extend_number):
        super().__init__(data)
        self.extend_number = extend_number

        self.up_channels, self.down_channels = get_channels(data, extremum_window_start, extremum_window_end, extremum_window_step, extremum_mode, check_window, alpha)

    def draw(self, chart_tool: BasicChartTools):

        ray = 0
        width = 1
        up_color = "12,50,250"
        down_color = "220,50,12"
        extend_style = chart_tool.EnumStyle.Dot

        # # Main Up Channel
        names_up, times1_up, prices1_up, times2_up, prices2_up = [], [], [], [], []
        names_down, times1_down, prices1_down, times2_down, prices2_down = [], [], [], [], []
        for i in range(len(self.up_channels)):
            self.append_line(f"UpChannel_UpLine{i}", self.up_channels[i]['UpLine']['x'][0],
                             self.up_channels[i]['UpLine']['x'][1], self.up_channels[i]['UpLine']['y'][0],
                             self.up_channels[i]['UpLine']['y'][1], names_up, times1_up, prices1_up, times2_up,
                             prices2_up)
            self.append_line(f"UpChannel_DownLine{i}", self.up_channels[i]['DownLine']['x'][0],
                             self.up_channels[i]['DownLine']['x'][1], self.up_channels[i]['DownLine']['y'][0],
                             self.up_channels[i]['DownLine']['y'][1], names_down, times1_down, prices1_down, times2_down,
                             prices2_down)

        chart_tool.trend_line(names_up, times1_up, prices1_up, times2_up, prices2_up, color=up_color, width=width,
                              ray=ray)
        chart_tool.trend_line(names_down, times1_down, prices1_down, times2_down, prices2_down, color=up_color,
                              width=width, ray=ray)

        # Left Extend Up Channel
        names_up, times1_up, prices1_up, times2_up, prices2_up = [], [], [], [], []
        names_down, times1_down, prices1_down, times2_down, prices2_down = [], [], [], [], []
        for i in range(len(self.up_channels)):
            x_left = max(min(self.up_channels[i]['UpLine']['x'][0], self.up_channels[i]['DownLine']['x'][0]) - self.extend_number, 0)
            y1 = np.polyval(self.up_channels[i]['UpLine']['line'], x_left)
            y2 = np.polyval(self.up_channels[i]['DownLine']['line'], x_left)
            self.append_line(f"UpChannel_UpLine_LeftExtend{i}", x_left, self.up_channels[i]['UpLine']['x'][0], y1,
                             self.up_channels[i]['UpLine']['y'][0], names_up, times1_up, prices1_up, times2_up,
                             prices2_up)
            self.append_line(f"UpChannel_DownLine_LeftExtend{i}", x_left, self.up_channels[i]['DownLine']['x'][0], y2,
                             self.up_channels[i]['DownLine']['y'][0], names_down, times1_down, prices1_down,
                             times2_down, prices2_down)

        chart_tool.trend_line(names_up, times1_up, prices1_up, times2_up, prices2_up, color=up_color,
                              ray=ray, style=extend_style)
        chart_tool.trend_line(names_down, times1_down, prices1_down, times2_down, prices2_down, color=up_color,
                              ray=ray, style=extend_style)

        # Right Extend Up Channel
        names_up, times1_up, prices1_up, times2_up, prices2_up = [], [], [], [], []
        names_down, times1_down, prices1_down, times2_down, prices2_down = [], [], [], [], []
        for i in range(len(self.up_channels)):
            x_right = min(max(self.up_channels[i]['UpLine']['x'][1],
                         self.up_channels[i]['DownLine']['x'][1]) + self.extend_number, len(self.data)-1)
            y1 = np.polyval(self.up_channels[i]['UpLine']['line'], x_right)
            y2 = np.polyval(self.up_channels[i]['DownLine']['line'], x_right)
            self.append_line(f"UpChannel_UpLine_RightExtend{i}", self.up_channels[i]['UpLine']['x'][1], x_right,
                             self.up_channels[i]['UpLine']['y'][1], y1, names_up, times1_up, prices1_up, times2_up,
                             prices2_up)
            self.append_line(f"UpChannel_DownLine_RightExtend{i}", self.up_channels[i]['DownLine']['x'][1], x_right,
                             self.up_channels[i]['DownLine']['y'][1], y2, names_down, times1_down, prices1_down,
                             times2_down, prices2_down)

        chart_tool.trend_line(names_up, times1_up, prices1_up, times2_up, prices2_up, color=up_color,
                              ray=ray, style=extend_style)
        chart_tool.trend_line(names_down, times1_down, prices1_down, times2_down, prices2_down, color=up_color,
                              ray=ray, style=extend_style)

        # # Main Down Channel
        names_up, times1_up, prices1_up, times2_up, prices2_up = [], [], [], [], []
        names_down, times1_down, prices1_down, times2_down, prices2_down = [], [], [], [], []
        for i in range(len(self.down_channels)):
            self.append_line(f"DownChannel_UpLine{i}", self.down_channels[i]['UpLine']['x'][0],
                             self.down_channels[i]['UpLine']['x'][1], self.down_channels[i]['UpLine']['y'][0],
                             self.down_channels[i]['UpLine']['y'][1], names_up, times1_up, prices1_up, times2_up,
                             prices2_up)
            self.append_line(f"DownChannel_DownLine{i}", self.down_channels[i]['DownLine']['x'][0],
                             self.down_channels[i]['DownLine']['x'][1], self.down_channels[i]['DownLine']['y'][0],
                             self.down_channels[i]['DownLine']['y'][1], names_down, times1_down, prices1_down, times2_down,
                             prices2_down)

        chart_tool.trend_line(names_up, times1_up, prices1_up, times2_up, prices2_up, color=down_color,
                              width=width, ray=ray)
        chart_tool.trend_line(names_down, times1_down, prices1_down, times2_down, prices2_down, color=down_color,
                              width=width, ray=ray)

        # Left Extend Down Channel
        names_up, times1_up, prices1_up, times2_up, prices2_up = [], [], [], [], []
        names_down, times1_down, prices1_down, times2_down, prices2_down = [], [], [], [], []
        for i in range(len(self.down_channels)):
            x_left = max(min(self.down_channels[i]['UpLine']['x'][0],
                         self.down_channels[i]['DownLine']['x'][0]) - self.extend_number, 0)
            y1 = np.polyval(self.down_channels[i]['UpLine']['line'], x_left)
            y2 = np.polyval(self.down_channels[i]['DownLine']['line'], x_left)
            self.append_line(f"DownChannel_UpLine_LeftExtend{i}", x_left, self.down_channels[i]['UpLine']['x'][0], y1,
                             self.down_channels[i]['UpLine']['y'][0], names_up, times1_up, prices1_up, times2_up,
                             prices2_up)
            self.append_line(f"DownChannel_DownLine_LeftExtend{i}", x_left, self.down_channels[i]['DownLine']['x'][0], y2,
                             self.down_channels[i]['DownLine']['y'][0], names_down, times1_down, prices1_down,
                             times2_down, prices2_down)

        chart_tool.trend_line(names_up, times1_up, prices1_up, times2_up, prices2_up, color=down_color,
                              ray=ray, style=extend_style)
        chart_tool.trend_line(names_down, times1_down, prices1_down, times2_down, prices2_down, color=down_color,
                              width=width, ray=ray, style=extend_style)

        # Right Extend Down Channel
        names_up, times1_up, prices1_up, times2_up, prices2_up = [], [], [], [], []
        names_down, times1_down, prices1_down, times2_down, prices2_down = [], [], [], [], []
        for i in range(len(self.down_channels)):
            x_right = min(max(self.down_channels[i]['UpLine']['x'][1],
                          self.down_channels[i]['DownLine']['x'][1]) + self.extend_number, len(self.data)-1)
            y1 = np.polyval(self.down_channels[i]['UpLine']['line'], x_right)
            y2 = np.polyval(self.down_channels[i]['DownLine']['line'], x_right)
            self.append_line(f"DownChannel_UpLine_RightExtend{i}", self.down_channels[i]['UpLine']['x'][1], x_right,
                             self.down_channels[i]['UpLine']['y'][1], y1, names_up, times1_up, prices1_up, times2_up,
                             prices2_up)
            self.append_line(f"DownChannel_DownLine_RightExtend{i}", self.down_channels[i]['DownLine']['x'][1], x_right,
                             self.down_channels[i]['DownLine']['y'][1], y2, names_down, times1_down, prices1_down,
                             times2_down, prices2_down)

        chart_tool.trend_line(names_up, times1_up, prices1_up, times2_up, prices2_up, color=down_color,
                              ray=ray, style=extend_style)
        chart_tool.trend_line(names_down, times1_down, prices1_down, times2_down, prices2_down, color=down_color,
                              width=width, ray=ray, style=extend_style)

    def append_line(self, name, x1, x2, y1, y2, names, times1, prices1, times2, prices2):
        names.append(name)
        times1.append(self.data[x1]['Time'])
        prices1.append(y1)
        times2.append(self.data[x2]['Time'])
        prices2.append(y2)



