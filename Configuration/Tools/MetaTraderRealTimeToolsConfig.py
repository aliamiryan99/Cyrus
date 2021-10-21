
from MetaTraderChartTool.BasicChartTools import BasicChartTools
import copy


class ChartConfig:

    time_frame = "H1"
    date_format = '%Y.%m.%d %H:%M'
    candles = 200
    tools_set = ['PivotPoints', 'VolumeBar']
    tool_name = 'VolumeBar'

    def __init__(self, chart_tool: BasicChartTools, data, tool_name):

        data = copy.deepcopy(data)
        if tool_name == "PivotPoints":
            from MetaTraderChartTool.RealTimeTools.PivotPoints import PivotPoints
            extremum_window = 5
            extremum_mode = 1

            self.tool = PivotPoints(chart_tool, data, extremum_window, extremum_mode)

        if tool_name == "VolumeBar":
            from MetaTraderChartTool.RealTimeTools.VolumeBarIndicator import VolumeBarIndicator

            vb_time_frame_cnt = 5*12*24

            self.tool = VolumeBarIndicator(chart_tool, data, vb_time_frame_cnt)
