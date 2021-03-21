from Simulation import Simulation
from Simulation.Config import Config
from Simulation import Outputs
import numpy as np
from datetime import datetime

from Indicators.ForcastingMultiInterpolation import forecastingMultiInterpolation
from Indicators.ForcastingParabloicApproach import forecasting_ParabolicApproach
import Candlestick

from Indicators.LocalExtremum import localExtremum

def initialize():
    Simulation.initialize()

    symbol = 'EURUSD'
    start_time = datetime.strptime(Config.start_date, Config.date_format)
    end_time = datetime.strptime(Config.end_date, Config.date_format)
    dataFrame = Simulation.data[Config.symbols_dict[symbol]]
    s_i = Outputs.index_date(dataFrame, start_time)
    e_i = Outputs.index_date(dataFrame, end_time)
    dataFrame = dataFrame.iloc[s_i:e_i]
    data = dataFrame.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close"})
    data = data.to_dict('records')

    return data, dataFrame

def multi_interpolation_launch():

    data, dataFrame = initialize()
    stp, X, XE, XExtend, LUE, LLE = forecastingMultiInterpolation(data)

    print(f"stp : {stp} \n X : {X} \n XE : {XE} \n LUE : {LUE} \n LLE : {LLE}")

    LUE_extend = []
    for list in LUE:
        list = np.array(list)
        LUE_extend.append(list[len(data)*10:])

    LLE_extend = []
    for list in LLE:
        LLE_extend.append(list[len(data)*10:])

    lines = [{'x': X, 'y': LUE}, {'x': X, 'y': LLE}]
    extends = [{'x': XExtend, 'y': LUE_extend}, {'x': XExtend, 'y': LLE_extend}]
    print(lines)

    [localMin, localMax] = localExtremum(data, 2)

    Candlestick.candlestick_plot(dataFrame, "Interpolation", lines, extends, localMax=localMax, localMin=localMin)


def parabloic_approach_launch():
    data, dataFrame = initialize()

    x, xExtend, LUExtend, LDExtend, buyIdx, sellIdx = forecasting_ParabolicApproach(data)

    print(f"x : {x} \n xExtend : {xExtend} \n LUExtend : {LUExtend} \n LDExtend : {LDExtend}")

    x = []
    yLU = []
    yLD = []
    for i in range(len(xExtend)-1, len(xExtend)-100, -1):
        x.append(xExtend[i])
        yLU.append(LUExtend[i])
        yLD.append(LDExtend[i])

    extends = [{'x': x, 'y': yLU}, {'x': x, 'y': yLD}]

    buyMarker = {'x': buyIdx, 'y': dataFrame['Close'].iloc[buyIdx]}
    sellMarker = {'x': sellIdx, 'y': dataFrame['Close'].iloc[sellIdx]}
    print(extends)

    Candlestick.candlestick_plot(dataFrame, "Interpolation", buyMarker=buyMarker, sellMarker=sellMarker)


multi_interpolation_launch()
