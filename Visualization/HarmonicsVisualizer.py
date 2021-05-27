from AlgorithmTools.LocalExtermums import *
from ta.momentum import *

from AlgorithmPackages.HarmonicPattern.HarmonicDetection import harmonic_pattern
from AlgorithmPackages.HarmonicPattern.HarmonicFilter import filter_results

from Visualization.BaseChart import *


class HarmonicVisualizer:

    def __init__(self, symbol, time_frame, data, extremum_window, time_range, price_range_alpha, harmonic_name):
        self.data = data

        self.symbol = symbol
        self.time_frame = time_frame
        self.extremum_window = extremum_window
        self.time_range = time_range
        self.price_range_alpha = price_range_alpha
        self.harmonic_name = harmonic_name

        self.open = np.array([d['Open'] for d in self.data])
        self.high = np.array([d['High'] for d in self.data])
        self.low = np.array([d['Low'] for d in self.data])
        self.close = np.array([d['Close'] for d in self.data])

        self.top = np.c_[self.open, self.close].max(1)
        self.bottom = np.c_[self.open, self.close].min(1)
        self.middle = np.c_[self.open, self.close].mean(1)

        self.price_range = self.price_range_alpha * (self.high - self.low).mean()

        self.local_min_price, self.local_max_price = get_local_extermums(self.data, extremum_window, 1)

        self.local_min_price_area, self.local_max_price_area = \
            get_local_extremum_area(data, self.local_min_price, self.local_max_price, self.time_range, self.price_range)

        self.bullish_result = harmonic_pattern(self.high, self.low, self.middle, self.local_min_price_area,
                                               self.local_max_price_area, self.harmonic_name, "Bullish", True)
        self.bearish_result = harmonic_pattern(self.high, self.low, self.middle, self.local_min_price_area,
                                               self.local_max_price_area, self.harmonic_name, "Bearish", True)

        self.bullish_result = filter_results(self.high, self.low, self.bullish_result, self.middle, self.harmonic_name,
                                             "Bullish")
        self.bearish_result = filter_results(self.high, self.low, self.bearish_result, self.middle, self.harmonic_name,
                                             "Bearish")

    def draw(self, fig, height):
        data_df = pd.DataFrame(self.data)

        fig.circle(self.local_max_price, data_df.High[self.local_max_price], size=8, color="red")
        fig.circle(self.local_min_price, data_df.Low[self.local_min_price], size=8, color="blue")

        fig.circle(self.local_max_price_area, data_df.High[self.local_max_price_area], size=4, color="red")
        fig.circle(self.local_min_price_area, data_df.Low[self.local_min_price_area], size=4, color="blue")
        width = 2
        alpha = 0.1
        for result in self.bullish_result:
            if self.harmonic_name == 'ABCD':

                fig.line([result[1], result[2]], [result[6], result[7]], color='blue', width=width)
                fig.line([result[2], result[3]], [result[7], result[8]], color='blue', width=width)
                fig.line([result[3], result[4]], [result[8], result[9]], color='blue', width=width)
                fig.line([result[1], result[3]], [result[6], result[8]], color='blue', width=int(width / 2),
                         line_dash='dotted')
                fig.line([result[2], result[4]], [result[7], result[9]], color='blue', width=int(width / 2),
                         line_dash='dotted')
            else:
                fig.patch([result[0], result[1], result[2]], [result[5], result[6], result[7]], alpha=alpha,
                          color="blue")
                fig.patch([result[2], result[3], result[4]], [result[7], result[8], result[9]], alpha=alpha,
                          color="blue")

        for result in self.bearish_result:
            if self.harmonic_name == 'ABCD':
                fig.line([result[1], result[2]], [result[6], result[7]], color='red', width=width)
                fig.line([result[2], result[3]], [result[7], result[8]], color='red', width=width)
                fig.line([result[3], result[4]], [result[8], result[9]], color='red', width=width)
                fig.line([result[1], result[3]], [result[6], result[8]], color='red', width=int(width / 2),
                         line_dash='dotted')
                fig.line([result[2], result[4]], [result[7], result[9]], color='red', width=int(width / 2),
                         line_dash='dotted')
            else:
                fig.patch([result[0], result[1], result[2]], [result[5], result[6], result[7]], alpha=alpha,
                          color="red")
                fig.patch([result[2], result[3], result[4]], [result[7], result[8], result[9]], alpha=alpha,
                          color="red")

        show(fig)





