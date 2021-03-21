from Simulation.Config import Config
from Simulation import Utility as ut

import pandas as pd

def read_data(category, symbol, time_frame):
    data_paths = ["../Data/" + category + "/" + symbol + "/" + time_frame + ".csv"]
    date_format = Config.date_format
    data = ut.csv_to_df(data_paths, date_format=date_format)
    return data[0].to_dict("Records")

def save_data(data, category, symbol, time_frame):
    data_df = pd.DataFrame(data, columns=['GMT', 'Open', 'High', 'Low', 'Close', 'Volume'])
    data_df.to_csv("../Data/" + category + "/" + symbol + "/" + time_frame + ".csv", index=False)