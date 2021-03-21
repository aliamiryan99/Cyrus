from Simulation.Config import Config
from Simulation import Utility as ut
from AlgorithmTools.HeikinCandle import HeikinConverter

import pandas as pd

def read_data(category, symbol, time_frame):
    data_paths = ["../Data/" + category + "/" + symbol + "/" + time_frame + ".csv"]
    date_format = Config.date_format
    data = ut.csv_to_df(data_paths, date_format=date_format)
    return data[0].to_dict("Records")

def convert_to_heiking(data):
    heikin_converter = HeikinConverter(data[0])

    heikin_data = []
    for i in range(1, len(data)):
        heikin_data.append(heikin_converter.on_data(data[i]))

    return heikin_data

def save_data(data, category, symbol, time_frame):
    data_df = pd.DataFrame(data, columns=['GMT', 'Open', 'High', 'Low', 'Close', 'Volume'])
    data_df.to_csv("../Data/" + category + "/" + symbol + "/" + time_frame + "_heikined.csv", index=False)


category = "CFD"
symbol = "US30USD"
time_frame = "D"

input_data = read_data(category, symbol, time_frame)
output_data = convert_to_heiking(input_data)
save_data(output_data, category, symbol, time_frame)



