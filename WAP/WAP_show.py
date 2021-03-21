import numpy as np
import pandas as pd

import Candlestick


df = pd.read_csv("vbSlow.csv")
df = df.rename(columns={"Time": "GMT"})

data = df[['Open', 'High', 'Low', 'Close']]
data = data.to_dict('records')

marker = {'x': np.arange(0, len(df)), 'y': df['WAP']}

Candlestick.candlestick_plot(df, "Slow", marker=marker)

