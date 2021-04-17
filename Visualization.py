import pandas as pd
from bokeh.io import output_file
from Simulation.Config import Config
from Simulation import Utility
from Simulation import Outputs
from Simulation import Candlestick


class Visualization:

    def __init__(self, backtest, balance, new_time_frame):
        self.backtest = backtest
        self.positions = pd.read_excel(f"Outputs/{backtest[3]}/{backtest[0]}_{backtest[1]}_{backtest[2]}/{backtest[4]}/history.xlsx", engine="openpyxl")
        self.symbols = self.positions['Symbol'].unique()
        self.positions = self.positions.to_dict("Records")
        data_shows_paths = []
        for symbol in self.symbols:
            category = Config.categories_list[symbol]
            data_shows_paths += [f"Data/{category}/{symbol}/{new_time_frame}.csv"]
        data = Utility.csv_to_df(data_shows_paths)
        for i in range(len(data)):
            data[i] = data[i].to_dict("Records")
        self.data_shows = {}
        self.indexes = {}
        for i in range(len(data)):
            symbol = self.symbols[i]
            self.data_shows[symbol] = data[i]
            self.indexes[symbol] = Outputs.index_date_v2(data[i], self.positions[0]['TimeOpen'])
        self.index_range = range(0, Outputs.index_date_v2(data[0], self.positions[-1]['TimeClose']) - Outputs.index_date_v2(data[0], self.positions[0]['TimeOpen']))
        self.balance = balance
        self.equity = self.balance
        self.open_positions = []
        self.equities = []
        self.balances = []
        self.create_balance_equity()

    def get_output(self):

        df_balance_history = pd.DataFrame(self.balances, columns=['index', 'x', 'balance'])
        df_equity_history = pd.DataFrame(self.equities, columns=['index', 'x', 'equity'])

        for position in self.positions:
            position['Index'] = Outputs.index_date_v2(self.data_shows, position['TimeOpen'])
            position['IndexEnd'] = Outputs.index_date_v2(self.data_shows, position['TimeClose'])

        positions_df = pd.DataFrame(self.positions)

        for symbol in self.symbols:
            start = Outputs.index_date_v2(self.data_shows[symbol], self.positions[0]['TimeOpen'])
            end = Outputs.index_date_v2(self.data_shows[symbol], self.positions[-1]['TimeClose'])
            data_shows = pd.DataFrame(self.data_shows[symbol])
            self.show_candlestick(symbol, data_shows.iloc[start:end + 5],
                             positions_df.loc[positions_df['Symbol'] == symbol],
                             df_balance_history, df_equity_history, start, None, None)

    def create_balance_equity(self):
        j = 0
        k = 0
        for ii in self.index_range:
            time = self.data_shows[self.symbols[0]][self.indexes[self.symbols[0]] + ii]
            for symbol in self.symbols:
                i = self.indexes[symbol] + ii
                row = self.data_shows[symbol][i]
                self.equity = self.balance
                for position in self.open_positions:
                    self.equity += self.cal_profit(position['Type'], position['Symbol'], position['PriceOpen'],
                                                   row['Open'], position['volume'])  # add profit
                while row['Time'] >= self.positions[j]['TimeOpen']:
                    self.open(self.positions[j])
                for position in self.open_positions:
                    if row['Time'] >= position['TimeClose']:
                        self.close(position)
            self.balances.append([ii, time, self.balance])
            self.equities.append([ii, time, self.equity])

    def open(self, position):
        self.open_positions.append({'Type': position['Type'], 'Symbol': position['Symbol'],
                                    'OpenPrice': position['PriceOpen'], 'ClosePrice': position['PriceClose'],
                                    'Volume': position['Volume']})

    def close(self, position):
        self.balance += Visualization.cal_profit(position['Type'], position['symbol'], position['PriceOpen'],
                                                 position['ClosePrice'], position['Volume'])
    @staticmethod
    def cal_profit(type, symbol, price_open, price_close, volume):
        LOT = Config.symbols_pip_value[symbol]
        volume_digit = Config.volume_digit
        if type == 'buy':
            if symbol[-3:] == 'USD':
                return round((price_close - price_open) * volume * LOT, volume_digit)  # profit or loss
            else:
                return round(((price_close - price_open) * volume * LOT) / price_close,
                             volume_digit)  # profit or loss
        elif type == 'sell':
            if symbol[-3:] == 'USD':
                return round((price_open - price_close) * volume * LOT, volume_digit)  # profit or loss
            else:
                return round(((price_open - price_close) * volume * LOT) / price_close,
                             volume_digit)  # profit or loss

    def show_candlestick(self, name, df, positions_df, df_balance, df_equity, start, trends, extends):
        backtest = self.backtest
        output_dir = "Outputs/" + backtest[3] + "/" + backtest[0] + \
                     "_" + backtest[1] + "_" + backtest[2] + "/" + backtest[4] + "/"
        output_file(output_dir + name + ".html")
        Candlestick.candlestick_plot(df, positions_df, name, df_balance, df_equity, start,
                                     trends, extends)


backtest = ["D", "D", "M1", "SI&ReEntrance", "Normal"]
balance = 10000
new_time_frame = "H12"
visualization = Visualization(backtest, balance, new_time_frame)
visualization.get_output()
