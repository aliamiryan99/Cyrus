from Visualization.DivergenceVisualizer import DivergenceVisualizer
from Visualization.HarmonicsVisualizer import HarmonicVisualizer
from Visualization.ImpulseVisualizer import ImpulseVisualizer
from Visualization.SupportResistanceVisualizer import SupportResistanceVisualizer


class Config:

    name = "SupportResistance"
    symbol = "EURUSD"
    time_frame = "D"
    date_format = "%d.%m.%Y %H:%M:%S.%f"
    start_date = "01.01.2018 00:00:00.000"
    end_date = "08.03.2020 00:00:00.000"
    holidays_show = False
    secondary_fig_height = 200

    def __init__(self, data):
        # # Visualizers Parameters
        # Divergence
        self.divergence_heikin_data_level = 0
        self.divergence_extremum_window = 5
        self.divergence_asymmetric_extremum_window = 3
        self.divergence_asymmetric_alpha = 20
        self.divergence_indicator_name = 'kdj'      # 'rsi', 'stochastic', 'kdj'

        # Harmonic
        # Gartley Butterfly Bat Crab Shark Cypher FiveZero ThreeDrives ExpandingFlag ABCD Inverse All
        self.harmonic_name = 'Butterfly'
        self.harmonic_extremum_window = 6
        self.harmonic_time_range = 5
        self.harmonic_price_range_alpha = 1

        # Impulse
        self.impulse_extremum_window = 2

        # Support Resistance
        self.s_r_extremum_window = 10
        self.s_r_num_sections = 30

        #self.visualizer = DivergenceVisualizer(data, self.divergence_heikin_data_level, self.divergence_indicator_name, self.divergence_extremum_window, self.divergence_asymmetric_extremum_window, self.divergence_asymmetric_alpha)
        self.visualizer = HarmonicVisualizer(Config.symbol, Config.time_frame, data, self.harmonic_extremum_window, self.harmonic_time_range, self.harmonic_price_range_alpha, self.harmonic_name)
        #self.visualizer = ImpulseVisualizer(data, self.impulse_extremum_window)
        #self.visualizer = SupportResistanceVisualizer(data, self.s_r_extremum_window, self.s_r_num_sections)
