from Visualization.Visualizer import Visualizer
from AlgorithmFactory.AlgorithmTools.LocalExtermums import *

from AlgorithmFactory.AlgorithmTools import RSTools, CandleTools

from Visualization.BaseChart import *


class SupportResistanceVisualizer(Visualizer):

    def __init__(self, data, extremum_mode, extremum_window, num_section):
        self.data = data

        self.extremum_mode = extremum_mode
        self.extremum_window = extremum_window
        self.num_section = num_section
        self.sections_filed = [False] * self.num_section

        self.open = np.array([d['Open'] for d in self.data])
        self.high = np.array([d['High'] for d in self.data])
        self.low = np.array([d['Low'] for d in self.data])
        self.close = np.array([d['Close'] for d in self.data])
        self.bottom, self.top = CandleTools.get_bottom_top(self.data)

        self.global_max_price = self.high.max()
        self.global_min_price = self.low.min()

        self.local_min_price, self.local_max_price = get_local_extermums(self.data, extremum_window, extremum_mode)
        local_min_value, local_max_value = self.bottom[self.local_min_price], self.top[self.local_max_price]
        local_extremum = np.array((self.local_min_price.tolist() + self.local_max_price.tolist()))
        local_extremum_value = np.array(local_min_value.tolist() + local_max_value.tolist())
        self.r_s_matrix = RSTools.get_support_resistance_lines(self.data, local_extremum, local_extremum_value)

    def draw(self, fig, height):
        data_df = pd.DataFrame(self.data)

        fig.circle(self.local_max_price, data_df.High[self.local_max_price], size=4, color="red")
        fig.circle(self.local_min_price, data_df.Low[self.local_min_price], size=4, color="blue")

        for r_s in self.r_s_matrix:
            value = r_s[1]
            section = int(((value - self.global_min_price) / (self.global_max_price - self.global_min_price))
                                 * self.num_section)
            if section == self.num_section:
                section -= 1
            if not self.sections_filed[section]:
                if value > self.data[-1]['Close']:
                    fig.line(x=[0, r_s[0]], y=[value, value], line_color='#1243b1', line_width=2)
                    fig.line(x=[r_s[0], len(self.data)], y=[value, value], line_color='#1243b1', line_width=2,
                             line_dash="dotted")
                else:
                    fig.line(x=[0, r_s[0]], y=[value, value], line_color='#f24341', line_width=2)
                    fig.line(x=[r_s[0], len(self.data)], y=[value, value], line_color='#f24341', line_width=2,
                             line_dash="dotted")
                self.sections_filed[section] = True

        show(fig)





