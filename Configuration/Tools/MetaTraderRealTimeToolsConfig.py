
from MetaTraderChartTool.BasicChartTools import BasicChartTools
import copy


class ChartConfig:

    time_frame = "M15"
    date_format = '%Y.%m.%d %H:%M'
    candles = 100
    tools_set = ['PivotPoints']
    tool_name = 'PivotPoints'

    def __init__(self, chart_tool: BasicChartTools, data, tool_name):

        data = copy.deepcopy(data)
        if tool_name == "PivotPoints":
            from MetaTraderChartTool.RealTimeTools.PivotPoints import PivotPoints
            extremum_window = 5
            extremum_mode = 1

            self.tool = PivotPoints(chart_tool, data, extremum_window, extremum_mode)
