from Converters.Tools import *
from Simulation.Outputs import *


def join_data(data1, data2):
    if data2[0]['GMT'] < data1[0]['GMT']:
        data1, data2 = data2, data1
    middle_index = index_date_v2(data1, data2[0]['GMT'])
    total_data = data1[:middle_index] + data2
    return total_data

category = "Metal"
symbol = "XAGUSD"
time_frame1 = "M1_2017"
time_frame2 = "M1_2019"
time_frame_output = "M1"

data1 = read_data(category, symbol, time_frame1)
data2 = read_data(category, symbol, time_frame2)

total_data = join_data(data1, data2)

save_data(total_data, category, symbol, time_frame_output)

print("Completed")

