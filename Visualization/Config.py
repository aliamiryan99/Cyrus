

class Config:

    symbol = "GBPUSD"
    time_frame = "H1"
    date_format = "%d.%m.%Y %H:%M:%S.%f"
    start_date = "01.01.2020 00:00:00.000"
    end_date = "01.01.2021 00:00:00.000"
    holidays_show = False
    secondary_fig_height = 200

    visualizer_set = ['divergence', 'harmonic', 'impulse', 'support_resistance', 'indicator']
    visualizer = 'indicator'

    def __init__(self, data, visualizer):

        if visualizer == 'divergence':
            from Visualization.DivergenceVisualizer import DivergenceVisualizer
            heikin_data_level = 0
            extremum_window = 5
            asymmetric_extremum_window = 3
            asymmetric_alpha = 20
            indicator_name = 'rsi'  # 'rsi', 'stochastic', 'kdj'

            self.visualizer = DivergenceVisualizer(data, heikin_data_level, indicator_name, extremum_window,
                                                   asymmetric_extremum_window, asymmetric_alpha)
        elif visualizer == 'harmonic':
            from Visualization.HarmonicsVisualizer import HarmonicVisualizer
            harmonic_list = ['Gartley', 'Butterfly', 'Bat', 'Crab', 'Shark', 'Cypher', 'FiveZero', 'ThreeDrives',
                             'ExpandingFlag', 'ABCD', 'Inverse', 'All']
            name = 'Inverse'
            extremum_window = 6
            time_range = 5
            price_range_alpha = 1

            self.visualizer = HarmonicVisualizer(Config.symbol, Config.time_frame, data, extremum_window, time_range,
                                                 price_range_alpha, name)
        elif visualizer == 'impulse':
            from Visualization.ImpulseVisualizer import ImpulseVisualizer
            extremum_mode = 2  # 1 : High Low, 2 : Top Bottom
            extremum_window = 1
            num_th = 1
            fib_enable = True

            self.visualizer = ImpulseVisualizer(data, extremum_mode, extremum_window, num_th, fib_enable)
        elif visualizer == 'support_resistance':
            from Visualization.SupportResistanceVisualizer import SupportResistanceVisualizer
            extremum_mode = 2  # 1 : High Low, 2 : Top Bottom
            extremum_window = 4
            num_sections = 20

            self.visualizer = SupportResistanceVisualizer(data, extremum_mode, extremum_window, num_sections)
        elif visualizer == 'indicator':
            from Visualization.IndicatorVisualizer import IndicatorVisualizer
            indicator_names = ['rsi']
            heikin_data_level = 0
            extremum_enable = False
            extremum_window = 2
            extremum_mode = 1

            self.visualizer = IndicatorVisualizer(data, indicator_names, heikin_data_level, extremum_enable,
                                                  extremum_window, extremum_mode)
