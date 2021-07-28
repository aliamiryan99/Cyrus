

class ChartConfig:

    time_frame = "H4"
    date_format = '%Y.%m.%d %H:%M'
    candles = 4000
    secondary_fig_height = 300
    tools_set = ['PivotPoints', "SupportResistance"]
    tool_name = 'PivotPoints'

    def __init__(self, data, tool_name):

        if tool_name == "PivotPoints":
            from MetaTraderChartTool.Tools.PivotPoints import PivotPoints
            extremum_window = 20
            extremum_mode = 1
            self.tool = PivotPoints(data, extremum_window, extremum_mode)
        if tool_name == "SupportResistance":
            from MetaTraderChartTool.Tools.SupportResistance import SupportResistance
            extremum_window = 20
            extremum_mode = 1
            sections = 20
            extremum_show = False
            self.tool = SupportResistance(data, extremum_window, extremum_mode, sections, extremum_show)


