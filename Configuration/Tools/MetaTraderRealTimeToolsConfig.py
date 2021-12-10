
from MetaTrader.MetaTraderBase import MetaTraderBase
import copy


class ChartConfig:

    auto_time_frame = True
    time_frame = "M15"
    date_format = '%Y.%m.%d %H:%M'
    candles = 5000
    tools_set = ['PivotPoints', 'VolumeBar', 'Channel', "Elliot", "SRLines", "CandleStick", "Pattern"]
    tool_name = 'CandleStick'

    def __init__(self, chart_tool: MetaTraderBase, data, symbol, tool_name, params=None):

        self.telegram = False

        data = copy.deepcopy(data)
        if tool_name == "PivotPoints":
            from MetaTraderChartTool.RealTimeTools.PivotPoints import PivotPoints
            extremum_window = 10
            extremum_mode = 1

            self.tool = PivotPoints(chart_tool, data, extremum_window, extremum_mode)

        if tool_name == "VolumeBar":
            from MetaTraderChartTool.RealTimeTools.VolumeBarIndicator import VolumeBarIndicator

            window_size = 15
            prediction_multiplayer = 4

            vb_h4_enable = False
            vb_h1_enable = True

            gp_enable = False

            save_data = False

            self.tool = VolumeBarIndicator(chart_tool, data, prediction_multiplayer, window_size, vb_h1_enable, vb_h4_enable, gp_enable, save_data)

        if tool_name == "Channel":
            from MetaTraderChartTool.RealTimeTools.Channels import Channel

            window = 300

            extremum_window_start = 1
            extremum_window_end = 30
            extremum_window_step = 6
            extremum_mode = 1
            check_window = 3
            alpha = 0.05
            extend_multiplier = 0.6
            type = 'monotone'  # 'betweenness' , 'monotone'

            if params is not None:
                window = params['Window']
                extremum_window_start = params['ExtWindowStart']
                extremum_window_end = params['ExtWindowEnd']
                extremum_window_step = params['ExtWindowStep']
                extremum_mode = params['ExtMode']
                check_window = params['CheckWindow']
                alpha = params['Alpha']
                extend_multiplier = params['ExtendMultiplier']
                type = params['Type']  # 'betweenness' , 'monotone'

            self.tool = Channel(chart_tool, data, symbol, window, extremum_window_start, extremum_window_end,
                                extremum_window_step, extremum_mode, check_window, alpha, extend_multiplier, type, self.telegram)

        if tool_name == "Elliot":
            from MetaTraderChartTool.RealTimeTools.Elliot import Elliot

            wave4_enable = True
            wave5_enable = False
            inside_flat_zigzag_wc = False
            post_prediction_enable = False

            price_type = "neo"
            neo_time_frame = "D1"
            past_check_num = 5
            window = 128

            self.tool = Elliot(chart_tool, data, wave4_enable, wave5_enable, inside_flat_zigzag_wc, post_prediction_enable,
                               price_type, self.time_frame, neo_time_frame, past_check_num, window)

        if tool_name == "SRLines":
            from MetaTraderChartTool.RealTimeTools.SR import SR

            static_leverage_degree = 7
            tf2 = "M30"
            tf3 = 'H1'

            mode = "Static"

            with_area = False
            base_area = 50

            window = 2000

            self.tool = SR(chart_tool, data, symbol, static_leverage_degree, self.time_frame, tf2, tf3, mode, window,
                           with_area, base_area)

        if tool_name == "CandleStick":
            from MetaTraderChartTool.RealTimeTools.CandleStick import CandleStick

            candle_type = "Engulfing"   # Doji , Hammer , InvertHammer , Engulfing

            self.tool = CandleStick(chart_tool, data, candle_type)

        if tool_name == "Pattern":
            from MetaTraderChartTool.RealTimeTools.Patterns import Pattern

            pattern_type = "HeadAndShoulder"    # DoubleTopAndBottom , HeadAndShoulder

            double_top_bottom_coefficient = 20
            scales = [5]

            self.tool = Pattern(chart_tool, data, pattern_type, double_top_bottom_coefficient, scales)