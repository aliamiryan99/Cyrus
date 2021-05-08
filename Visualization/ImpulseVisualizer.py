import numpy as np
from AlgorithmTools.LocalExtermums import *
from Algorithms.Divergence.Divergence import divergence_calculation
from ta.momentum import *

from AlgorithmTools import Impulse

from Visualization.BaseChart import *


class ImpulseVisualizer:

    def __init__(self, data, extremum_window):
        self.data = data

        self.extremum_window = extremum_window

        self.local_min_price, self.local_max_price = get_local_extermums(self.data, extremum_window, 1)

        self.up_impulse, self.down_impulse = Impulse.get_impulses(self.data, self.local_min_price, self.local_max_price)

    def draw(self, fig, height):
        data_df = pd.DataFrame(self.data)

        fig.circle(self.local_max_price, data_df.High[self.local_max_price], size=5, color="red")
        fig.circle(self.local_min_price, data_df.Low[self.local_min_price], size=5, color="blue")

        for impulse in self.up_impulse:
            fig.patch([impulse[0], impulse[0], impulse[1], impulse[1]],
                      [self.data[impulse[0]]['Low'], self.data[impulse[1]]['High'], self.data[impulse[1]]['High'],
                       self.data[impulse[0]]['Low']], alpha=0.2, color="blue")

        for impulse in self.down_impulse:
            fig.patch([impulse[0], impulse[0], impulse[1], impulse[1]],
                      [self.data[impulse[0]]['High'], self.data[impulse[1]]['Low'], self.data[impulse[1]]['Low'],
                       self.data[impulse[0]]['High']], alpha=0.2, color="red")

        show(fig)





