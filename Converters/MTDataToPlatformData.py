from Simulation import Utility as ut
import pandas as pd

file_name = "Input/EURUSD.I1440.csv"

file = pd.read_csv(file_name)

file['Date'] = file['Date'].astype(str) + " " + file['Time'].astype(str)
file = file.drop(columns=['Time'])
file = file.rename(columns={'Date': 'GMT'})

print(file)

file.to_csv("Output/EURUSD_MT4_D.csv", index=False)