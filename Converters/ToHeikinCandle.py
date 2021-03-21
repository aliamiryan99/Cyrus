from Simulation.Config import Config
from Converters.Tools import *
from AlgorithmTools.HeikinCandle import HeikinConverter

def convert_to_heiking(data):
    heikin_converter = HeikinConverter(data[0])

    heikin_data = []
    for i in range(1, len(data)):
        heikin_data.append(heikin_converter.on_data(data[i]))

    return heikin_data

category = "CFD"
symbol = "US30USD"
time_frame = "D"

input_data = read_data(category, symbol, time_frame)
output_data = convert_to_heiking(input_data)
save_data(output_data, category, symbol, time_frame + "_heikined")



