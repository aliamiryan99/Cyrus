
from AlgorithmTools.LocalExtermums import *

from AlgorithmTools import Impulse
from AlgorithmTools import FiboTools

from Visualization.BaseChart import *


class ImpulseVisualizer:

    def __init__(self, data, extremum_mode, extremum_window, num_th, fib_enable):
        self.data = data

        self.extremum_mode = extremum_mode
        self.extremum_window = extremum_window
        self.fib_enable = fib_enable

        self.local_min_price, self.local_max_price = get_local_extermums(self.data, extremum_window, extremum_mode)
        self.up_impulse, self.down_impulse = Impulse.get_impulses(self.data, self.local_min_price, self.local_max_price, num_th)

    def draw(self, fig, height):
        data_df = pd.DataFrame(self.data)

        fig.circle(self.local_max_price, data_df.High[self.local_max_price], size=5, color="red")
        fig.circle(self.local_min_price, data_df.Low[self.local_min_price], size=5, color="blue")

        for impulse in self.up_impulse:
            fig.patch([impulse[0], impulse[0], impulse[1], impulse[1]],
                      [self.data[impulse[0]]['Low'], self.data[impulse[1]]['High'], self.data[impulse[1]]['High'],
                       self.data[impulse[0]]['Low']], alpha=0.2, color="blue")
            if self.fib_enable:
                fib_prices = FiboTools.get_fib_levels(self.data[impulse[0]]['Low'], self.data[impulse[1]]['High'])
                for fib_price_key in fib_prices.keys():
                    fib_price = fib_prices[fib_price_key]
                    fig.line(x=[impulse[0], impulse[1]], y=[fib_price, fib_price], line_color='blue', line_width=1)

        for impulse in self.down_impulse:
            fig.patch([impulse[0], impulse[0], impulse[1], impulse[1]],
                      [self.data[impulse[0]]['High'], self.data[impulse[1]]['Low'], self.data[impulse[1]]['Low'],
                       self.data[impulse[0]]['High']], alpha=0.2, color="red")
            if self.fib_enable:
                fib_prices = FiboTools.get_fib_levels(self.data[impulse[0]]['High'], self.data[impulse[1]]['Low'])
                for fib_price_key in fib_prices.keys():
                    fib_price = fib_prices[fib_price_key]
                    fig.line(x=[impulse[0], impulse[1]], y=[fib_price, fib_price], line_color='red', line_width=1)

        show(fig)





