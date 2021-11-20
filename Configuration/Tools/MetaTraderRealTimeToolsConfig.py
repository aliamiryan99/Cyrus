
from MetaTraderChartTool.BasicChartTools import BasicChartTools
import copy


class ChartConfig:

    time_frame = "M30"
    date_format = '%Y.%m.%d %H:%M'
    candles = 2000
    tools_set = ['PivotPoints', 'VolumeBar', 'Channel', "Elliot", "SRLines"]
    tool_name = 'Elliot'

    def __init__(self, chart_tool: BasicChartTools, data, symbol, tool_name):

        data = copy.deepcopy(data)
        if tool_name == "PivotPoints":
            from MetaTraderChartTool.RealTimeTools.PivotPoints import PivotPoints
            extremum_window = 5
            extremum_mode = 1

            self.tool = PivotPoints(chart_tool, data, extremum_window, extremum_mode)

        if tool_name == "VolumeBar":
            from MetaTraderChartTool.RealTimeTools.VolumeBarIndicator import VolumeBarIndicator

            window_size = 15
            prediction_multiplayer = 4

            vb_h4_enable = True
            vb_h1_enable = False

            gp_enable = True

            save_data = False

            self.tool = VolumeBarIndicator(chart_tool, data, prediction_multiplayer, window_size, vb_h1_enable, vb_h4_enable, gp_enable, save_data)

        if tool_name == "Channel":
            from MetaTraderChartTool.RealTimeTools.Channels import Channel

            window = 300

            extremum_window_start = 1
            extremum_window_end = 20
            extremum_window_step = 5
            extremum_mode = 1
            check_window = 3
            alpha = 0.05
            extend_number = 40
            type = 'monotone'  # 'betweenness' , 'monotone'

            self.tool = Channel(chart_tool, data, window, extremum_window_start, extremum_window_end,
                                extremum_window_step, extremum_mode, check_window, alpha, extend_number, type)

        if tool_name == "Elliot":
            from MetaTraderChartTool.RealTimeTools.Elliot import Elliot

            price_type = "neo"
            neo_time_frame = "H4"
            past_check_num = 5
            window = 128

            self.tool = Elliot(chart_tool, data, price_type, self.time_frame, neo_time_frame, past_check_num, window)

        if tool_name == "SRLines":
            from MetaTraderChartTool.RealTimeTools.SR import SR

            tf2 = "M30"
            tf3 = 'H1'

            mode = "OSR"

            self.tool = SR(chart_tool, data, symbol, self.time_frame, tf2, tf3, mode)
