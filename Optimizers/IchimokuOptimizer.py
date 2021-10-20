
import pandas as pd
import os
from tqdm import tqdm

base_directory = "Ichimoku"

param_list = {
    'Symbol': ['EURUSD', 'GBPUSD', 'XAUUSD'],
    'TimeFrame': ['M30', 'H1', 'H4', 'D1'],
    'Role': [1, 2, 3, 6, 8, 9],
    'Tenkan': [9*i for i in range(1,10)],
    'Kijun': [26*i for i in range(1,10)],
    'SenkouSpanProjection': [0, 26],
    'RangeFilterEnable': [False, True],
    'SequentialTrade': [False, True],
    'KomuCloudFilter': [False, True]
}


if __name__ == "__main__":

    results = {'Symbol': [], 'TimeFrame': [], 'Role': [], 'Tenkan': [], 'Kijun': [], 'SenkouSpanProjection': [],
               'RangeFilterEnable': [], 'SequentialTrade': [], 'KomuCloudFilter': [], 'Profit': []}
    file_list = os.listdir(base_directory)
    for file_name in tqdm(file_list):
        result = pd.read_csv(base_directory + "/" + file_name)
        result = result.to_dict('list')
        for key in result.keys():
            results[key] += result[key]
    df = pd.DataFrame(results)
    df = df.sort_values(['Profit'], ascending=False)
    df.to_csv("IchimokuOptimizersResults.csv", index=False)
