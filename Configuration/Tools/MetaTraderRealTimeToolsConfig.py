
from MetaTrader.MetaTraderBase import MetaTraderBase
import copy


class ChartConfig:

    auto_time_frame = True
    time_frame = "M5"
    date_format = '%Y.%m.%d %H:%M'
    candles = 5000
    tools_set = ['PivotPoints', 'VolumeBar', 'Channel', "Elliot", "SRLines", "Harmonics", "CandleStick", "Pattern",
                 "MinMaxTrend", "SupplyAndDemand"]
    tool_name = 'SupplyAndDemand'

    def __init__(self, chart_tool: MetaTraderBase, data, symbol, tool_name, params=None):

        self.telegram_enable = False
        self.trade_enable = False

        data = copy.deepcopy(data)
        if tool_name == "PivotPoints":
            from MetaTrader.RealTimeTools.PivotPoints import PivotPoints
            extremum_window = 30
            extremum_mode = 1

            self.tool = PivotPoints(chart_tool, data, extremum_window, extremum_mode)

        if tool_name == "VolumeBar":
            from MetaTrader.RealTimeTools.VolumeBarIndicator import VolumeBarIndicator

            window_size = 15
            prediction_multiplayer = 4

            vb_h4_enable = False
            vb_h1_enable = True
            gp_enable = False
            save_data = False

            self.tool = VolumeBarIndicator(chart_tool, data, prediction_multiplayer, window_size, vb_h1_enable, vb_h4_enable, gp_enable, save_data)

        if tool_name == "Channel":
            from MetaTrader.RealTimeTools.Channels import Channel

            window = 300

            extremum_window_start = 2
            extremum_window_end = 30
            extremum_window_step = 4
            extremum_mode = 1
            check_window = 3
            alpha = 0.1
            beta = 0
            extend_multiplier = 0.6
            convergence = True
            divergence = False
            type = 'monotone'  # 'betweenness' , 'monotone'

            if params is not None:
                window = params['Window']
                extremum_window_start = params['ExtWindowStart']
                extremum_window_end = params['ExtWindowEnd']
                extremum_window_step = params['ExtWindowStep']
                extremum_mode = params['ExtMode']
                check_window = params['CheckWindow']
                alpha = params['Alpha']
                beta = params['Beta']
                extend_multiplier = params['ExtendMultiplier']
                convergence = params['Convergence']
                divergence = params['Divergence']
                type = params['Type']  # 'betweenness' , 'monotone'

            self.tool = Channel(chart_tool, data, symbol, window, extremum_window_start, extremum_window_end,
                                extremum_window_step, extremum_mode, check_window, alpha, beta, convergence, divergence, extend_multiplier, type, self.telegram_enable)

        if tool_name == "Elliot":
            from MetaTrader.RealTimeTools.Elliot import Elliot

            wave4_enable = False
            wave5_enable = False
            inside_flat_zigzag_wc = False
            post_prediction_enable = False

            price_type = "neo"
            neo_time_frame = "W1"
            past_check_num = 5
            window = 128
            statistic_window = 15

            self.tool = Elliot(chart_tool, data, symbol, wave4_enable, wave5_enable, inside_flat_zigzag_wc, post_prediction_enable,
                               price_type, self.time_frame, neo_time_frame, past_check_num, window, statistic_window, self.trade_enable)

        if tool_name == "SRLines":
            from MetaTrader.RealTimeTools.SR import SR

            static_leverage_degree = 7
            tf2 = "M30"
            tf3 = 'H1'

            mode = "OSR"
            osr_second_time_frame = "H4"

            with_area = False
            base_area = 250

            window = 2000

            self.tool = SR(chart_tool, data, symbol, static_leverage_degree, self.time_frame, tf2, tf3, mode, window,
                           with_area, base_area, osr_second_time_frame)

        if tool_name == "CandleStick":
            from MetaTrader.RealTimeTools.CandleStick import CandleStick

            candle_type = "Doji"   # Doji , Hammer , InvertHammer , Engulfing, SimpleIdea

            filter_direction = 0    # 1:buy , -1:sell , 0 : all

            self.tool = CandleStick(chart_tool, data, symbol, candle_type, filter_direction, self.trade_enable, self.telegram_enable)

        if tool_name == "Pattern":
            from MetaTrader.RealTimeTools.Patterns import Pattern

            pattern_type = "DoubleTopAndBottom"    # DoubleTopAndBottom , HeadAndShoulder

            double_top_bottom_coefficient = 20
            scales = [10]
            window = 200

            self.tool = Pattern(chart_tool, data, pattern_type, double_top_bottom_coefficient, scales, window)

        if tool_name == "MinMaxTrend":
            from MetaTrader.RealTimeTools.MinMaxTrend import MinMaxTrendTool

            extremum_window = 4
            extremum_mode = 1
            extremum_show = True

            self.tool = MinMaxTrendTool(chart_tool, data, symbol, extremum_window, extremum_mode, extremum_show, self.trade_enable, self.telegram_enable)

        if tool_name == "SupplyAndDemand":
            from MetaTrader.RealTimeTools.SupplyAndDemand import SupplyAndDemand

            tr = 1
            minimum_candles = 3
            tr2 = 2
            minimum_candles2 = 1
            swing_filter = True
            fresh_window = 100
            atr_window = 99

            risk = 3

            risk_free_enable = False
            touch_trade_enable = True
            candlestick_enable = True

            self.tool = SupplyAndDemand(chart_tool, data, symbol, tr, minimum_candles, tr2, minimum_candles2,
                                        swing_filter, fresh_window, atr_window, risk, risk_free_enable, touch_trade_enable, candlestick_enable)

        if tool_name == "Harmonics":
            from MetaTrader.RealTimeTools.Harmonics import Harmonics

            fresh_window = 200

            pattern_direction = 'both'  # bullish, bearish, both
            harmonic_list = ['Gartley', 'Butterfly', 'Bat', 'Crab', 'Shark', 'Cypher', 'FiveZero', 'ThreeDrives',
                             'ExpandingFlag']
            name = 'All'
            fibo_tolerance = 0.15  # percentage of Fibonacci tolerance
            extremum_window = 20
            time_range = 5
            price_range_alpha = 1
            alpha = 0.8
            beta = 0.25
            save_result = True

            extremum_mode = "window"
            neo_time_frame = "H4"

            is_save_statistical_result = False

            self.tool = Harmonics(chart_tool, data, symbol, extremum_window, time_range, price_range_alpha, name, alpha,
                                  beta, fibo_tolerance, pattern_direction, harmonic_list, save_result, self.time_frame,
                                  neo_time_frame, extremum_mode, is_save_statistical_result, fresh_window)
