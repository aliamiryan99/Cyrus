
import pandas as pd
from bokeh.io import output_file
import os

from Simulation import Utility
from Simulation import Outputs

from Visualization.BaseChart import *


class EnterPositionCombiner:

    def __init__(self, backtests, new_time_frame, colors, width):
        self.backtests = backtests
        self.new_time_frame = new_time_frame
        self.colors = colors
        self.width = width
        self.histories = {}
        self.algorithms = []
        self.symbols = []
        for backtest in backtests:
            if backtest[3] not in self.algorithms:
                self.algorithms.append(backtest[3])
                self.histories[backtest[3]] = []
            self.histories[backtest[3]].append(pd.read_excel(
                f"Outputs/{backtest[3]}/{backtest[0]}_{backtest[1]}_{backtest[2]}/{backtest[4]}/history.xlsx",
                engine="openpyxl"))
        self.positions = {}
        for algorithm in self.algorithms:
            self.positions[algorithm] = pd.concat(self.histories[algorithm], ignore_index=True)
            self.positions[algorithm] = self.positions[algorithm].sort_values(['TimeOpen'])
            self.symbols += self.positions[algorithm]['Symbol'].unique().tolist()
            self.positions[algorithm] = self.positions[algorithm].to_dict("Records")

        self.symbols = list(dict.fromkeys(self.symbols))
        data_shows_paths = []
        for symbol in self.symbols:
            category = Config.categories_list[symbol]
            data_shows_paths += [f"Data/{category}/{symbol}/{new_time_frame}.csv"]
        data = Utility.csv_to_df(data_shows_paths)
        self.data_shows = {}
        for i in range(len(data)):
            symbol = self.symbols[i]
            self.data_shows[symbol] = data[i].to_dict("Records")

        start_index = {}
        end_index = {}
        for symbol in self.symbols:
            start_index[symbol] = Outputs.index_date_v2(self.data_shows[symbol], self.positions[self.algorithms[0]][0]['TimeOpen'])
            end_index[symbol] = Outputs.index_date_v2(self.data_shows[symbol], self.positions[self.algorithms[-1]][0]['TimeClose'])
            for algorithm in self.algorithms:
                start_index[symbol] = min(start_index[symbol], Outputs.index_date_v2(self.data_shows[symbol], self.positions[algorithm][0]['TimeOpen']))
                end_index[symbol] = max(end_index[symbol], Outputs.index_date_v2(self.data_shows[symbol], self.positions[algorithm][-1]['TimeClose']))

        output_dir = "Combiners/Outputs"
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)

        self.base_figs = {}
        for i in range(len(data)):
            symbol = self.symbols[i]
            output_file(output_dir + symbol + ".html")
            data[i] = data[i].iloc[start_index[symbol]-20:end_index[symbol]+20]
            self.base_figs[symbol] = get_base_fig(data[i], symbol)
            data[i] = data[i].to_dict("Records")
            self.data_shows[symbol] = data[i]

        for i in range(len(data)):
            symbol = self.symbols[i]

    def get_output(self):
        for algorithm in self.algorithms:
            for position in self.positions[algorithm]:
                symbol = position['Symbol']
                position['Index'] = Outputs.index_date_v2(self.data_shows[symbol], position['TimeOpen'])
                position['IndexEnd'] = Outputs.index_date_v2(self.data_shows[symbol], position['TimeClose'])

        for i in range(len(self.algorithms)):
            algorithm = self.algorithms[i]
            symbols = []
            buy_x, buy_y = {}, {}
            sell_x, sell_y = {}, {}
            for position in self.positions[algorithm]:
                if position['Symbol'] not in symbols:
                    symbols.append(position['Symbol'])
                    buy_x[position['Symbol']], buy_y[position['Symbol']] = [], []
                    sell_x[position['Symbol']], sell_y[position['Symbol']] = [], []
                if position['Type'] == 'buy':
                    buy_x[position['Symbol']].append(position['Index'])
                    buy_y[position['Symbol']].append(position['OpenPrice'])
                elif position['Type'] == 'sell':
                    sell_x[position['Symbol']].append(position['Index'])
                    sell_y[position['Symbol']].append(position['OpenPrice'])
            for symbol in symbols:
                self.base_figs[symbol].circle(buy_x[symbol], buy_y[symbol], size=self.width, color=self.colors[i])
                self.base_figs[symbol].square(sell_x[symbol], sell_y[symbol], size=self.width, color=self.colors[i])

        for symbol in self.symbols:
            show(self.base_figs[symbol])

