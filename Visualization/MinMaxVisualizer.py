
from AlgorithmTools.LocalExtermums import *
from AlgorithmTools.HeikinCandle import HeikinConverter
from AlgorithmPackages.Divergence.DivergencePkg import divergence_calculation

from AlgorithmPackages.MinMaxTrend import MinMaxTrend

from Visualization.Tools import *
from Visualization.BaseChart import *


class MinMaxVisualizer:

    def __init__(self, data, extremum_window, extremum_mode):
        self.data = data

        self.open = np.array([d['Open'] for d in self.data])
        self.high = np.array([d['High'] for d in self.data])
        self.low = np.array([d['Low'] for d in self.data])
        self.close = np.array([d['Close'] for d in self.data])

        self.top = np.c_[self.open, self.close].max(1)
        self.bottom = np.c_[self.open, self.close].min(1)

        self.local_min_price, self.local_max_price = get_local_extermums(self.data, extremum_window, extremum_mode)

        self.x_up_trend, self.y_up_trend, self.x_down_trend, self.y_down_trend, self.x_extend_inc, self.y_extend_inc,\
            self.x_extend_dec, self.y_extend_dec, self.sell_idx, self.sell, self.buy_idx, self.buy = \
            MinMaxTrend.min_max_trend_detect(self.open, self.high, self.low, self.close, self.top, self.bottom,
                                             self.local_min_price, self.local_max_price, True)

    def draw(self, fig, height):

        fig.circle(self.buy_idx, self.buy, size=4, color="blue")
        fig.circle(self.sell_idx, self.sell, size=4, color="red")

        for i in range(len(self.x_up_trend)):
            x, y = self.x_up_trend[i], self.y_up_trend[i]
            x_ext, y_ext = self.x_extend_inc[i], self.y_extend_inc[i]
            fig.line(x, y, color='blue', width=1)
            if x_ext is not 0:
                fig.line([x_ext[0], x_ext[-1]], [y_ext[0], y_ext[-1]], color='blue', width=1, line_dash="dotted")

        for i in range(len(self.x_down_trend)):
            x, y = self.x_down_trend[i], self.y_down_trend[i]
            x_ext, y_ext = self.x_extend_dec[i], self.y_extend_dec[i]
            fig.line(x, y, color='red', width=1)
            if x_ext is not 0:
                fig.line([x_ext[0], x_ext[-1]], [y_ext[0], y_ext[-1]], color='red', width=1, line_dash="dotted")

        show(fig)





