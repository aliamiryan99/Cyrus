from Converters.Tools import *
from tqdm import tqdm
from datetime import timedelta


def change_time(data, shift_h):
    for i in tqdm(range(len(data))):
        data[i]['Time'] = data[i]['Time'] + timedelta(hours=shift_h)
    return data

category = "Metal"
symbol = "XAUUSD"
time_frame = "M1"
time_frame_output = "M1_New"
shift_h = 3

data = read_data(category, symbol, time_frame)

total_data = change_time(data, shift_h)

save_data(total_data, category, symbol, time_frame_output)

print("Completed")
