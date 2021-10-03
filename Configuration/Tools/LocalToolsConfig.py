

class ChartConfig:

    symbol = "XAUUSD"
    time_frame = "H4"
    date_format = "%d.%m.%Y %H:%M:%S.%f"
    start_date = "01.04.2017 00:00:00.000"
    end_date = "01.03.2021 00:00:00.000"
    holidays_show = False
    secondary_fig_height = 300
    visualizer_set = ['Divergence', 'Harmonic', 'Impulse', 'SupportResistance', 'Indicator', 'MinMax', 'Regression',
                      'Channel']
    visualizer = 'Indicator'

    with_back_test = True
    backtest = ["H4", "H4", "M1", "Ichimoku", "Role7 XAUUSD H4"]

    def __init__(self, data, visualizer):

        if visualizer == 'Divergence':
            from Visualization.DivergenceVisualizer import DivergenceVisualizer
            heikin_data_level = 0
            extremum_window = 12
            asymmetric_extremum_window = 3
            asymmetric_alpha = 20
            hidden_divergence_check_window = 30
            upper_line_tr = 0.90
            # ('RSI: Window'), ('Stochastic: Window, Smooth1, Smooth2'), ('KDJ: WindowK, WindowD'),
            # ('MACD: WindowSlow, WindowFast'), ('AMA: Window, WindowSF')
            indicator_params = {'Name': 'AMA', 'Window': 14, 'WindowSF': 6}

            self.visualizer = DivergenceVisualizer(data, heikin_data_level, indicator_params, extremum_window,
                                                   asymmetric_extremum_window, asymmetric_alpha,
                                                   hidden_divergence_check_window, upper_line_tr)
        elif visualizer == 'Harmonic':
            from Visualization.HarmonicsVisualizer import HarmonicVisualizer
            harmonic_list = ['Gartley', 'Butterfly', 'Bat', 'Crab', 'Shark', 'Cypher', 'FiveZero', 'ThreeDrives',
                             'ExpandingFlag', 'ABCD', 'Inverse', 'All']
            name = 'Butterfly'
            extremum_window = 6
            time_range = 5
            price_range_alpha = 1

            self.visualizer = HarmonicVisualizer(ChartConfig.symbol, ChartConfig.time_frame, data, extremum_window, time_range,
                                                 price_range_alpha, name)
        elif visualizer == 'Impulse':
            from Visualization.ImpulseVisualizer import ImpulseVisualizer
            extremum_mode = 2  # 1 : High Low, 2 : Top Bottom
            extremum_window = 1
            candle_num_th = 3
            fib_enable = True

            self.visualizer = ImpulseVisualizer(data, extremum_mode, extremum_window, candle_num_th, fib_enable)
        elif visualizer == 'SupportResistance':
            from Visualization.SupportResistanceVisualizer import SupportResistanceVisualizer
            extremum_mode = 2  # 1 : High Low, 2 : Top Bottom
            extremum_window = 4
            num_sections = 10

            self.visualizer = SupportResistanceVisualizer(data, extremum_mode, extremum_window, num_sections)
        elif visualizer == 'Indicator':
            from Visualization.IndicatorVisualizer import IndicatorVisualizer
            indicator_names = []
            heikin_data_level = 0
            extremum_enable = False
            extremum_window = 2
            extremum_mode = 1
            ma_enable = False
            ma_list = [{'ma_type': 'EMA', 'price_type': 'Close', 'window': 14, 'color': '#2364d1', 'width': 1}]
            ichimoku_enable = True
            tenkan = 9
            kijun = 26

            self.visualizer = IndicatorVisualizer(data, indicator_names, heikin_data_level, extremum_enable,
                                                  extremum_window, extremum_mode, ma_enable, ma_list, ichimoku_enable,
                                                  tenkan, kijun)
        elif visualizer == 'MinMax':
            from Visualization.MinMaxVisualizer import MinMaxVisualizer
            extremum_window = 1
            extremum_mode = 1

            self.visualizer = MinMaxVisualizer(data, extremum_window, extremum_mode)
        elif visualizer == 'Regression':
            from Visualization.RegressionVisualizer import RegressionVisualizer
            extremum_window = 3
            extremum_mode = 1

            self.visualizer = RegressionVisualizer(data, extremum_window, extremum_mode)
        elif visualizer == "Channel":
            from Visualization.ChannelsVisualizer import ChannelsVisualizer
            extremum_window_start = 2
            extremum_window_end = 20
            extremum_window_step = 5
            extremum_mode = 1
            check_window = 4
            alpha = 0.1
            extend_number = 50

            self.visualizer = ChannelsVisualizer(data, extremum_window_start, extremum_window_end, extremum_window_step, extremum_mode,
                                 check_window, alpha, extend_number)