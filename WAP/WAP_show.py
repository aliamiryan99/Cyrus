import numpy as np
import pandas as pd

from Visualization import BaseChart

df = pd.read_csv("vbSlow.csv")
df = df.rename(columns={"Time": "GMT"})

data = df[['Open', 'High', 'Low', 'Close']]
data = data.to_dict('records')

marker = {'x': np.arange(0, len(df)), 'y': df['WAP']}

BaseChart.candlestick_plot(df, "Slow", marker=marker)

