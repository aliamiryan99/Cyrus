from Simulation import Utility as ut
from bokeh.io import output_file
import Candlestick

file_name = "EURUSD_Fibo"
date_format = "%Y.%m.%d %H:%M"
data_show_paths = ["Data/CustomData/" + file_name + ".csv"]

data_shows = ut.csv_to_df(data_show_paths, date_format=date_format)

Candlestick.candlestick_plot(data_shows[0], "EURUSD_fibo")
