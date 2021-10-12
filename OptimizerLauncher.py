
from BackTestTradeManager import BackTestLauncher

from Optimizers.IchimokuOptimizer import param_list

import pandas as pd

keys = list(param_list.keys())
n = len(keys)

param_indexes = {}
for key in param_list:
    param_indexes[key] = 0

end_condition = False
results = []

while not end_condition:

    param = {}
    for key in param_list:
        param[key] = param_list[key][param_indexes[key]]

    launcher = BackTestLauncher(param)
    market = launcher.run()
    param['Profit'] = market.profit
    results.append(param)
    print(param)

    i = 0
    while param_indexes[keys[i]] == len(param_list[keys[i]]) - 1:
        i += 1
        if i == n:
            end_condition = True
            break
    if not end_condition:
        for j in range(i):
            param_indexes[keys[j]] = 0
        param_indexes[keys[i]] += 1


df_results = pd.DataFrame(results)

df_results = df_results.sort_values(['Profit'])

df_results.to_csv("Optimizers/IchimokuResults.csv", index=False)
