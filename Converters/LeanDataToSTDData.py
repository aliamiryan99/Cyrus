
from zipfile import ZipFile
import pandas as pd

zip_name = "Input/eurusd.zip"
file_name = "eurusd.csv"

zf = ZipFile(zip_name)
df = pd.read_csv(zf.open(file_name), header=None, names=['Time', 'BidOpen', 'BidHigh', 'BidLow', 'BidClose', 'BidVolume', 'AskOpen', 'AskHigh', 'AskLow', 'AskClose', 'AskVolume', 'Volume'])
df = df[['Time', 'BidOpen', 'BidHigh', 'BidLow', 'BidClose', 'Volume']]
df = df.rename(columns={"BidOpen": "Open", "BidHigh": "High", 'BidLow': "Low", "BidClose": "Close"})
print(df)
