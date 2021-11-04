
from MetaTraderChartTool.BasicChartTools import BasicChartTools
import copy


class ChartConfig:

    time_frame = "H1"
    date_format = '%Y.%m.%d %H:%M'
    candles = 2000
    tools_set = ['PivotPoints', 'VolumeBar', 'Channel']
    tool_name = 'Channel'

    def __init__(self, chart_tool: BasicChartTools, data, tool_name):

        data = copy.deepcopy(data)
        if tool_name == "PivotPoints":
            from MetaTraderChartTool.RealTimeTools.PivotPoints import PivotPoints
            extremum_window = 5
            extremum_mode = 1

            self.tool = PivotPoints(chart_tool, data, extremum_window, extremum_mode)

        if tool_name == "VolumeBar":
            from MetaTraderChartTool.RealTimeTools.VolumeBarIndicator import VolumeBarIndicator

            window_size = 15
            prediction_multiplayer = 2

            vb_h4_enable = False
            vb_h1_enable = True

            gp_enable = True

            self.tool = VolumeBarIndicator(chart_tool, data, prediction_multiplayer, window_size, vb_h1_enable, vb_h4_enable, gp_enable)

        if tool_name == "Channel":
            from MetaTraderChartTool.RealTimeTools.Channels import Channel

            window = 300

            extremum_window_start = 2
            extremum_window_end = 3
            extremum_window_step = 1
            extremum_mode = 1
            check_window = 4
            alpha = 0.1
            extend_number = 50
            type = 'parallel'  # 'parallel' , 'monotone'

            self.tool = Channel(chart_tool, data, window, extremum_window_start, extremum_window_end,
                                extremum_window_step, extremum_mode, check_window, alpha, extend_number, type)
