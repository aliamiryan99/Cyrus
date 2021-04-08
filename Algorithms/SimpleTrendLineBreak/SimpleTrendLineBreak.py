
from Simulation.Config import Config as S_Config
from MetaTrader.Config import Config as MT_Config
import numpy as np

def simple_trend_detect(window):
    if window[-1]['Close'] > window[-1]['Open'] and window[-2]['Close'] > window[-2]['Open']:
        if window[-1]['Low'] > window[-2]['Low']:
            return 1
    if window[-1]['Close'] < window[-1]['Open'] and window[-2]['Close'] < window[-2]['Open']:
        if window[-1]['High'] < window[-2]['High']:
            return -1
    return 0


def get_ascending_line_value(window):
    line = np.polyfit([0, 1], [window[-1]['Low'], window[-2]['Low']], 1)
    return np.polyval(line, 2)


def get_descending_line_value(window):
    line = np.polyfit([0, 1], [window[-1]['High'], window[-2]['High']], 1)
    return np.polyval(line, 2)

