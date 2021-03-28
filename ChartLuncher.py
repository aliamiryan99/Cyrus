from Simulation import Utility as ut
from bokeh.io import output_file
from AlgorithmTools import LocalExtermums
import Candlestick
from ta.momentum import rsi
from Algorithms.Divergence.Divergence import divergence_calculation
from AlgorithmTools.HeikinCandle import HeikinConverter
import numpy as np
from pandas import Series
from datetime import datetime
from Simulation import Outputs

category = "CFD"
symbol = "US30USD"
date_format = "%d.%m.%Y %H:%M:%S.%f"
start_date = "01.01.2016 00:00:00.000"
end_date = "01.01.2021 00:00:00.000"
data_show_paths = ["Data/" + category + "/" + symbol + "/D.csv"]

start_time = datetime.strptime(start_date, date_format)
end_time = datetime.strptime(end_date, date_format)

data_shows = ut.csv_to_df(data_show_paths, date_format=date_format)[0]

start_index = Outputs.index_date(data_shows, start_time)
end_index = Outputs.index_date(data_shows, end_time)

data_shows = data_shows.iloc[start_index:end_index+1]

data_shows = data_shows[data_shows.Volume != 0]
data = data_shows.to_dict("Records")

Open = np.array([d['Open'] for d in data])
High = np.array([d['High'] for d in data])
Low = np.array([d['Low'] for d in data])
Close = np.array([d['Close'] for d in data])

a = np.c_[Open, Close].max(1)
b = np.c_[Open, Close].min(1)

local_min_price_left, local_max_price_left = LocalExtermums.get_local_extermums(data, 8)
local_min_price_right, local_max_price_right = LocalExtermums.get_local_extermums_asymetric(data, 5, 4)

heikin_converter1 = HeikinConverter(data[0])
heikin_data = heikin_converter1.convert_many(data[1:])
heikin_converter2 = HeikinConverter(heikin_data[0])
heikin_data = heikin_converter2.convert_many(heikin_data[1:])

indicator = rsi(Series([item['Close'] for item in heikin_data]), 14).reset_index().rename(columns={'rsi': 'value'})
indicator_np = np.array(list(indicator['value']))

local_min_indicator_left, local_max_indicator_left = LocalExtermums.get_indicator_local_extermums(list(indicator['value']), 5)
local_min_indicator_right, local_max_indicator_right = LocalExtermums.get_indicator_local_extermums_asymetric(list(indicator['value']), 3, 4)


real_time = False
hidden_divergence_check_window = 25
upper_line_tr = 0.90
body_avg = np.mean(a - b)
pip_difference = body_avg * .2
# --- bullish divergence
trend_direction = 1
down_direction = 0
[idx1, val1] = divergence_calculation(b, Low, indicator_np, local_min_price_left, local_min_price_right, local_min_indicator_left,
                          local_min_indicator_right, hidden_divergence_check_window, down_direction, trend_direction,
                          pip_difference, upper_line_tr, real_time)

trend_direction = 1
down_direction = 1
[idx2, val2] = divergence_calculation(b, Low, indicator_np, local_min_price_left, local_min_price_right, local_min_indicator_left,
                          local_min_indicator_right, hidden_divergence_check_window, down_direction, trend_direction,
                          pip_difference, upper_line_tr, real_time)

# --- bearish divergence
trend_direction = 0
down_direction = 0
[idx3, val3] = divergence_calculation(a, High, indicator_np, local_max_price_left, local_max_price_right, local_max_indicator_left,
                          local_max_indicator_right, hidden_divergence_check_window, down_direction, trend_direction,
                          pip_difference, upper_line_tr, real_time)

trend_direction = 0
down_direction = 1
[idx4, val4] = divergence_calculation(a, High, indicator_np, local_max_price_left, local_max_price_right, local_max_indicator_left,
                          local_max_indicator_right, hidden_divergence_check_window, down_direction, trend_direction,
                          pip_difference, upper_line_tr, real_time)

line1 = []
indicator_line_1 = []
line2 = []
indicator_line_2 = []
for i in range(len(idx1)):
    row = idx1[i]
    line1.append({'x': [row[0][0], row[0][1]], 'y': [Low[row[0][0]], Low[row[0][1]]]})
    indicator_line_1.append({'x': [row[1][0], row[1][1]], 'y': [indicator_np[row[1][0]], indicator_np[row[1][1]]]})

for i in range(len(idx2)):
    row = idx2[i]
    line1.append({'x': [row[0][0], row[0][1]], 'y': [Low[row[0][0]], Low[row[0][1]]]})
    indicator_line_1.append({'x': [row[1][0], row[1][1]], 'y': [indicator_np[row[1][0]], indicator_np[row[1][1]]]})

for i in range(len(idx3)):
    row = idx3[i]
    line2.append({'x': [row[0][0], row[0][1]], 'y': [High[row[0][0]], High[row[0][1]]]})
    indicator_line_2.append({'x': [row[1][0], row[1][1]], 'y': [indicator_np[row[1][0]], indicator_np[row[1][1]]]})

for i in range(len(idx4)):
    row = idx4[i]
    line2.append({'x': [row[0][0], row[0][1]], 'y': [High[row[0][0]], High[row[0][1]]]})
    indicator_line_2.append({'x': [row[1][0], row[1][1]], 'y': [indicator_np[row[1][0]], indicator_np[row[1][1]]]})


Candlestick.candlestick_plot(data_shows, symbol, True, indicator, divergence_line=line1,
                             indicator_divergene_line=indicator_line_1, divergence_line_2=line2,
                             indicator_divergene_line_2=indicator_line_2, indicatorLocalMax=local_max_indicator_left,
                             indicatorLocalMin=local_min_indicator_left, indicatorLocalMax2=local_max_indicator_right,
                             indicatorLocalMin2=local_min_indicator_right, localMax=local_max_price_left,
                             localMin=local_min_price_left, localMax2=local_max_price_right,
                             localMin2=local_min_price_right)
