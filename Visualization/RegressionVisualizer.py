
from AlgorithmTools.LocalExtermums import *

from AlgorithmPackages.RegressionLine import RegressionLine

from Visualization.Tools import *
from Visualization.BaseChart import *


class RegressionVisualizer:

    def __init__(self, data, extremum_window, extremum_mode):
        self.data = data

        self.open = np.array([d['Open'] for d in self.data])
        self.high = np.array([d['High'] for d in self.data])
        self.low = np.array([d['Low'] for d in self.data])
        self.close = np.array([d['Close'] for d in self.data])

        self.top = np.c_[self.open, self.close].max(1)
        self.bottom = np.c_[self.open, self.close].min(1)

        self.local_min, self.local_max = get_local_extermums(self.data, extremum_window, extremum_mode)

        self.x_up, self.y_up, self.x_ext_up, self.y_ext_up, self.x_buy, self.y_buy, self.x_down, self.y_down,\
            self.x_ext_down, self.y_ext_down, self.x_sell, self.y_sell = \
            RegressionLine.regression_line_detection(self.open, self.high, self.low, self.close, self.top, self.bottom,
                                                     self.local_min, self.local_max, True)

    def draw(self, fig, height):

        fig.circle(self.x_buy, self.y_buy, size=4, color="blue")
        fig.circle(self.x_sell, self.y_sell, size=4, color="red")

        for i in range(len(self.x_up[0])):
            x, y = [self.x_up[0][i], self.x_up[1][i]], [self.y_up[0][i], self.y_up[1][i]]
            x_ext, y_ext = [int(self.x_ext_up[0][i]), int(self.x_ext_up[1][i])], [self.y_ext_up[0][i], self.y_ext_up[1][i]]
            fig.line(x, y, color='blue', width=1)
            fig.line(x_ext, y_ext, color='blue', width=1, line_dash="dotted")

        for i in range(len(self.x_down[0])):
            x, y = [self.x_down[0][i], self.x_down[1][i]], [self.y_down[0][i], self.y_down[1][i]]
            x_ext, y_ext = [int(self.x_ext_down[0][i]), int(self.x_ext_down[1][i])], [self.y_ext_down[0][i], self.y_ext_down[1][i]]
            fig.line(x, y, color='red', width=1)
            fig.line(x_ext, y_ext, color='red', width=1, line_dash="dotted")

        show(fig)





