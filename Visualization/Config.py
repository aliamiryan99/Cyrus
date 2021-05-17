

class Config:

    symbol = "USDJPY"
    time_frame = "H1"
    date_format = "%d.%m.%Y %H:%M:%S.%f"
    start_date = "01.01.2020 00:00:00.000"
    end_date = "01.01.2021 00:00:00.000"
    holidays_show = False
    secondary_fig_height = 200

    # visualizer_set : ['divergence', 'harmonic', 'impulse', 'support_resistance']
    visualizer = 'impulse'

    def __init__(self, data, visualizer):
        # # Visualizers Parameters
        # Divergence
        self.divergence_heikin_data_level = 0
        self.divergence_extremum_window = 5
        self.divergence_asymmetric_extremum_window = 3
        self.divergence_asymmetric_alpha = 20
        self.divergence_indicator_name = 'kdj'      # 'rsi', 'stochastic', 'kdj'

        # Harmonic
        harmonic_list = ['Gartley', 'Butterfly', 'Bat', 'Crab', 'Shark', 'Cypher', 'FiveZero', 'ThreeDrives',
                         'ExpandingFlag', 'ABCD', 'Inverse', 'All']
        self.harmonic_name = 'Butterfly'
        self.harmonic_extremum_window = 6
        self.harmonic_time_range = 5
        self.harmonic_price_range_alpha = 1

        # Impulse
        self.impulse_extremum_mode = 2   # 1 : High Low, 2 : Top Bottom
        self.impulse_extremum_window = 1
        self.impulse_num_th = 1
        self.impulse_fib_enable = True

        # Support Resistance
        self.s_r_extremum_mode = 2      # 1 : High Low, 2 : Top Bottom
        self.s_r_extremum_window = 4
        self.s_r_num_sections = 30

        if visualizer == 'divergence':
            from Visualization.DivergenceVisualizer import DivergenceVisualizer
            self.visualizer = DivergenceVisualizer(data, self.divergence_heikin_data_level, self.divergence_indicator_name, self.divergence_extremum_window, self.divergence_asymmetric_extremum_window, self.divergence_asymmetric_alpha)
        elif visualizer == 'harmonic':
            from Visualization.HarmonicsVisualizer import HarmonicVisualizer
            self.visualizer = HarmonicVisualizer(Config.symbol, Config.time_frame, data, self.harmonic_extremum_window, self.harmonic_time_range, self.harmonic_price_range_alpha, self.harmonic_name)
        elif visualizer == 'impulse':
            from Visualization.ImpulseVisualizer import ImpulseVisualizer
            self.visualizer = ImpulseVisualizer(data, self.impulse_extremum_mode, self.impulse_extremum_window, self.impulse_num_th, self.impulse_fib_enable)
        elif visualizer == 'support_resistance':
            from Visualization.SupportResistanceVisualizer import SupportResistanceVisualizer
            self.visualizer = SupportResistanceVisualizer(data,self.s_r_extremum_mode, self.s_r_extremum_window, self.s_r_num_sections)
