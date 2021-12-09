

class ChartConfig:

    auto_time_frame = True
    time_frame = "W1"
    date_format = '%Y.%m.%d %H:%M'
    auto_candles = False
    candles = 5000
    tools_set = ['PivotPoints', "SupportResistance", "Impulse", "MinMax", "Channels", "Elliot", "Harmonics",
                 "RangeRegion", "SRLevels"]
    tool_name = 'Impulse'

    def __init__(self, symbol, data, tool_name, params=None):

        if tool_name == "PivotPoints":
            from MetaTraderChartTool.Tools.PivotPoints import PivotPoints
            extremum_window = 10
            extremum_mode = 1

            self.tool = PivotPoints(data, extremum_window, extremum_mode)
        if tool_name == "SupportResistance":
            from MetaTraderChartTool.Tools.SupportResistance import SupportResistance
            extremum_window = 40
            extremum_mode = 1
            sections = 8
            extremum_show = False

            self.tool = SupportResistance(data, extremum_window, extremum_mode, sections, extremum_show)
        if tool_name == "Impulse":
            from MetaTraderChartTool.Tools.Impulse import Impulse
            extremum_window = 40
            extremum_mode = 1
            candles_tr = 2
            extremum_show = True

            self.tool = Impulse(data, extremum_window, extremum_mode, candles_tr, extremum_show)
        if tool_name == "MinMax":
            from MetaTraderChartTool.Tools.MinMax import MinMax
            extremum_window = 5
            extremum_mode = 1
            extremum_show = True

            self.tool = MinMax(data, extremum_window, extremum_mode, extremum_show)

        if tool_name == "Channels":
            from MetaTraderChartTool.Tools.Channels import Channels
            extremum_window_start = 1
            extremum_window_end = 20
            extremum_window_step = 5
            extremum_mode = 1
            check_window = 3
            alpha = 0.05
            extend_number = 30
            type = 'monotone'   # 'betweenness' , 'monotone'

            self.tool = Channels(data, extremum_window_start, extremum_window_end, extremum_window_step, extremum_mode,
                                 check_window, alpha, extend_number, type)

        if tool_name == "Elliot":
            from MetaTraderChartTool.Tools.Elliot import Elliot

            wave4_enable = True
            wave5_enable = False
            inside_flat_zigzag_wc = False
            post_prediction_enable = False

            price_type = "neo"
            neo_time_frame = "H4"

            self.tool = Elliot(data, wave4_enable, wave5_enable, inside_flat_zigzag_wc, post_prediction_enable,
                               price_type, self.time_frame, neo_time_frame)

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
            save_result = True

            self.tool = Harmonics(data, extremum_window, time_range, price_range_alpha, name, alpha, beta, fibo_tolerance, pattern_direction, harmonic_list, save_result)
        if tool_name == "Indicator":
            from MetaTraderChartTool.Tools.Indicator import Indicator

            self.tool = Indicator(data)

        if tool_name == "RangeRegion":
            from MetaTraderChartTool.Tools.RangeRegion import RangeRegion
            range_candle_threshold = 3
            up_timeframe = "D1"
            stop_target_margin = 50
            candle_breakout_threshold = 1
            max_candles = 1000

            type1_enable = True
            type2_enable = True

            one_stop_in_region = False

            fib_enable = False

            if params is not None:
                range_candle_threshold = params['RangeCandleThreshold']
                up_timeframe = params['UpTimeFrame']
                stop_target_margin = params['StopTargetMargin']
                candle_breakout_threshold = params['CandlesBreakoutThreshold']
                max_candles = params['MaxCandles']
                type1_enable = params['Type1Enable']
                type2_enable = params['Type2Enable']
                one_stop_in_region = params['OneStopInRegion']
                fib_enable = params['FibEnable']

            self.tool = RangeRegion(symbol, data, range_candle_threshold, up_timeframe, stop_target_margin,
                                    type1_enable, type2_enable, one_stop_in_region, candle_breakout_threshold,
                                    max_candles, fib_enable)

        if tool_name == "SRLevels":
            from MetaTraderChartTool.Tools.SR import SR

            static_leverage_degree = 7
            tf2 = "M30"
            tf3 = 'H1'

            mode = "Static"

            self.tool = SR(data, symbol, self.time_frame, tf2, tf3, mode)
