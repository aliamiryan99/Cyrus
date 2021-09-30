
import pandas as pd
from datetime import datetime, timedelta
import os
from tqdm import tqdm

base_directory = "../MetaTrader/TickData"


def convert_tick_data(file_list):
    total_data = {'Time': [], 'Bid': [], 'Ask': []}
    for file_name in tqdm(file_list):
        data = extract_tick_data(file_name)
        total_data['Time'] += data['Time']
        total_data['Bid'] += data['Bid']
        total_data['Ask'] += data['Ask']
    return total_data


def extract_tick_data(file_name):
    df = pd.read_csv(base_directory + "/" + file_name, header=None, names=['Time', 'Bid', 'Ask'])
    data = df.to_dict('list')
    return data


file_list = os.listdir(base_directory)
total_data = convert_tick_data(file_list)
df = pd.DataFrame(total_data)
df.to_csv("../Data/EURUSD.csv", index=False)
