import pandas as pd
import copy
from Simulation import Utility as ut
from Simulation.Config import Config
import datetime

def getIdentifier(time_frame, time):
    identifier = None
    if time_frame == "D":
        identifier = int(time.days)
    if time_frame == "H12":
        identifier = int(time.days * 2) + int(time.seconds / 43200)
    if time_frame == "H4":
        identifier = int(time.days * 6) + int(time.seconds / 14400)
    if time_frame == "H1":
        identifier = int(time.days * 24) + int(time.seconds / 3600)
    if time_frame == "M30":
        identifier = int(time.days * 48) + int(time.seconds / 1800)
    if time_frame == "M1":
        identifier = int(time.days * 1440) + int(time.seconds / 60)
    return identifier

def get_time_delta(time_frame):
    time_delta = None
    if time_frame == "D":
        time_delta = datetime.timedelta(1)
    if time_frame == "H12":
        time_delta = datetime.timedelta(hours=12)
    if time_frame == "H4":
        time_delta = datetime.timedelta(hours=4)
    if time_frame == "H1":
        time_delta = datetime.timedelta(hours=1)
    if time_frame == "M30":
        time_delta = datetime.timedelta(minutes=30)
    if time_frame == "M1":
        time_delta = datetime.timedelta(minutes=1)
    return time_delta

def read_data(category, symbol, time_frame):
    data_paths = [category + "/" + symbol + "/" + time_frame + ".csv"]
    date_format = Config.date_format
    data = ut.csv_to_df(data_paths, date_format=date_format)
    return data[0].to_dict("Records")

def clean_data(data, time_frame):
    new_data = []
    for i in range(1,len(data)):
        old_candle = data[i-1]
        new_candle = data[i]
        time_difference = new_candle["GMT"] - old_candle["GMT"]
        identifier = getIdentifier(time_frame, time_difference)
        new_data.append(old_candle)
        j = 0
        while identifier > 1:
            j += 1
            time_delta = get_time_delta(time_frame)
            lost_candle = {'GMT': old_candle['GMT'] + j * time_delta, 'Open': old_candle['Close'], 'High': old_candle['Close'],
                           'Low': old_candle['Close'], 'Close': old_candle['Close'], 'Volume': 0}
            new_data.append(lost_candle)
            identifier -= 1
            print(f"Data Cleaned {lost_candle}")
            print("_______________________________________________________________")
    return new_data

def save_data(data, category, symbol, time_frame):
    data_df = pd.DataFrame(data, columns=['GMT', 'Open', 'High', 'Low', 'Close', 'Volume'])
    data_df.to_csv(category + "/" + symbol + "/" + time_frame + "_cleaned.csv", index=False)


category = "Metal"
symbol = "XAUUSD"
time_frame = "M1"

input_data = read_data(category, symbol, time_frame)
output_data = clean_data(input_data, time_frame)
save_data(output_data, category, symbol, time_frame)



