

class ChartConfig:

    auto_time_frame = True
    time_frame = "H4"
    date_format = '%Y.%m.%d %H:%M'
    auto_candles = True
    candles = 2000
    tools_set = ['PivotPoints', "SupportResistance", "Impulse", "MinMax", "Channels", "Elliot", "Harmonics",
                 "RangeRegion"]
    tool_name = 'RangeRegion'

    def __init__(self, symbol, data, tool_name):

        if tool_name == "PivotPoints":
            from MetaTraderChartTool.Tools.PivotPoints import PivotPoints
            extremum_window = 10
            extremum_mode = 1

            self.tool = PivotPoints(data, extremum_window, extremum_mode)
        if tool_name == "SupportResistance":
            from MetaTraderChartTool.Tools.SupportResistance import SupportResistance
            extremum_window = 40
            extremum_mode = 1
            sections = 5
            extremum_show = False

            self.tool = SupportResistance(data, extremum_window, extremum_mode, sections, extremum_show)
        if tool_name == "Impulse":
            from MetaTraderChartTool.Tools.Impulse import Impulse
            extremum_window = 40
            extremum_mode = 1
            candles_tr = 2
            extremum_show = False

            self.tool = Impulse(data, extremum_window, extremum_mode, candles_tr, extremum_show)
        if tool_name == "MinMax":
            from MetaTraderChartTool.Tools.MinMax import MinMax
            extremum_window = 5
            extremum_mode = 1
            extremum_show = False

            self.tool = MinMax(data, extremum_window, extremum_mode, extremum_show)

        if tool_name == "Channels":
            from MetaTraderChartTool.Tools.Channels import Channels
            extremum_window_start = 2
            extremum_window_end = 3
            extremum_window_step = 1
            extremum_mode = 1
            check_window = 4
            alpha = 0.1
            extend_number = 50
            type = 'parallel'   # 'parallel' , 'monotone'

            self.tool = Channels(data, extremum_window_start, extremum_window_end, extremum_window_step, extremum_mode,
                                 check_window, alpha, extend_number, type)

        if tool_name == "Elliot":
            from MetaTraderChartTool.Tools.Elliot import Elliot

            self.tool = Elliot(data)

        if tool_name == "Harmonics":
            from MetaTraderChartTool.Tools.Harmonics import Harmonics

            pattern_direction = 'bearish'  # bullish, bearish, both
            harmonic_list = ['Gartley', 'Butterfly', 'Bat', 'Crab', 'Shark', 'Cypher', 'FiveZero', 'ThreeDrives',
                             'ExpandingFlag', 'ABCD', 'Inverse', 'All']
            name = 'Butterfly'
            fibo_tolerance = 0.2  # percentage of Fibonacci tolerance
            extremum_window = 6
            time_range = 5
            price_range_alpha = 1
            alpha = 0.8
            beta = 0.25
            save_result = False

            self.tool = Harmonics(data, extremum_window, time_range, price_range_alpha, name, alpha, beta, fibo_tolerance, pattern_direction, harmonic_list, save_result)
        if tool_name == "Indicator":
            from MetaTraderChartTool.Tools.Indicator import Indicator

            self.tool = Indicator(data)

        if tool_name == "RangeRegion":
            from MetaTraderChartTool.Tools.RangeRegion import RangeRegion
            range_candle_threshold = 3
            up_timeframe = "D1"

            self.tool = RangeRegion(symbol, data, range_candle_threshold, up_timeframe)
