
from zipfile import ZipFile
import pandas as pd
from datetime import datetime, timedelta
import os
from tqdm import tqdm

base_directory = "tick"
symbol = "eurusd"
directory = base_directory + "/" + symbol


def convert_tick_data(file_list):
    total_data = {'Time': [], 'Bid': [], 'Ask': []}
    for zip_name in tqdm(file_list):
        date_str = zip_name.split("_")[0]
        zip_name = directory + "/" + zip_name
        file_name = date_str + "_" + symbol + "_tick_quote.csv"
        data = extract_tick_data(zip_name, file_name)
        total_data['Time'] += data['Time']
        total_data['Bid'] += data['Bid']
        total_data['Ask'] += data['Ask']
    return total_data


def extract_tick_data(zip_name, file_name):
    zf = ZipFile(zip_name)
    df = pd.read_csv(zf.open(file_name), header=None, names=['Time', 'Bid', 'Ask'])
    data = df.to_dict('list')
    date_str = file_name.split('_')[0]
    date = datetime.strptime(date_str, "%Y%m%d")
    for i in range(len(data['Time'])):
        data['Time'][i] = date + timedelta(milliseconds=int(data['Time'][i]))
    return data


part = 8
file_list = os.listdir(directory)
file_list = file_list[int((part-1)*len(file_list) / 8): int(part*len(file_list)/8)]
total_data = convert_tick_data(file_list)
df = pd.DataFrame(total_data)
df.to_csv("tick/EURUSD"+str(part)+".csv", index=False)
