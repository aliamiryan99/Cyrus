

class Config:

    symbol = "EURUSD"
    time_frame = "D"
    date_format = "%d.%m.%Y %H:%M:%S.%f"
    start_date = "01.02.2017 00:00:00.000"
    end_date = "08.08.2017 00:00:00.000"
    holidays_show = False
    secondary_fig_height = 400
    visualizer_set = ['Divergence', 'Harmonic', 'Impulse', 'SupportResistance', 'Indicator', 'MinMax', 'Regression']
    visualizer = 'Regression'

    def __init__(self, data, visualizer):

        if visualizer == 'Divergence':
            from Visualization.DivergenceVisualizer import DivergenceVisualizer
            heikin_data_level = 0
            extremum_window = 5
            asymmetric_extremum_window = 3
            asymmetric_alpha = 20
            indicator_name = 'macd'  # 'rsi', 'stochastic', 'kdj', 'macd'

            self.visualizer = DivergenceVisualizer(data, heikin_data_level, indicator_name, extremum_window,
                                                   asymmetric_extremum_window, asymmetric_alpha)
        elif visualizer == 'Harmonic':
            from Visualization.HarmonicsVisualizer import HarmonicVisualizer
            harmonic_list = ['Gartley', 'Butterfly', 'Bat', 'Crab', 'Shark', 'Cypher', 'FiveZero', 'ThreeDrives',
                             'ExpandingFlag', 'ABCD', 'Inverse', 'All']
            name = 'Butterfly'
            extremum_window = 6
            time_range = 5
            price_range_alpha = 1

            self.visualizer = HarmonicVisualizer(Config.symbol, Config.time_frame, data, extremum_window, time_range,
                                                 price_range_alpha, name)
        elif visualizer == 'Impulse':
            from Visualization.ImpulseVisualizer import ImpulseVisualizer
            extremum_mode = 2  # 1 : High Low, 2 : Top Bottom
            extremum_window = 1
            candle_num_th = 1
            fib_enable = True

            self.visualizer = ImpulseVisualizer(data, extremum_mode, extremum_window, candle_num_th, fib_enable)
        elif visualizer == 'SupportResistance':
            from Visualization.SupportResistanceVisualizer import SupportResistanceVisualizer
            extremum_mode = 2  # 1 : High Low, 2 : Top Bottom
            extremum_window = 4
            num_sections = 20

            self.visualizer = SupportResistanceVisualizer(data, extremum_mode, extremum_window, num_sections)
        elif visualizer == 'Indicator':
            from Visualization.IndicatorVisualizer import IndicatorVisualizer
            indicator_names = ['macd']
            heikin_data_level = 0
            extremum_enable = False
            extremum_window = 2
            extremum_mode = 1
            ma_enable = True
            ma_list = [{'ma_type': 'EMA', 'price_type': 'Close', 'window': 14, 'color': '#2364d1', 'width': 1}]

            self.visualizer = IndicatorVisualizer(data, indicator_names, heikin_data_level, extremum_enable,
                                                  extremum_window, extremum_mode, ma_enable, ma_list)
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