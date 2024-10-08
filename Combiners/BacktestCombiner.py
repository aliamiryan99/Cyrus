
import pandas as pd
from bokeh.io import output_file
import os

from Configuration.Trade.BackTestConfig import Config
from Simulation import Utility
from Simulation import Outputs
from Simulation import Candlestick


class BacktestCombiner:

    def __init__(self, backtests, balance, new_time_frame):
        self.backtests = backtests
        self.new_time_frame = new_time_frame
        self.histories = []
        for backtest in backtests:
            self.histories.append(pd.read_excel(f"Outputs/{backtest[3]}/{backtest[0]}_{backtest[1]}_{backtest[2]}/{backtest[4]}/history.xlsx", engine="openpyxl"))
        self.positions = pd.concat(self.histories, ignore_index=True)
        self.positions = self.positions.sort_values(['TimeOpen'])
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
            symbol = position['Symbol']
            position['Index'] = Outputs.index_date_v2(self.data_shows[symbol], position['TimeOpen'])
            position['IndexEnd'] = Outputs.index_date_v2(self.data_shows[symbol], position['TimeClose'])

        positions_df = pd.DataFrame(self.positions)

        for symbol in self.symbols:
            start = Outputs.index_date_v2(self.data_shows[symbol], self.positions[0]['TimeOpen'])
            end = Outputs.index_date_v2(self.data_shows[symbol], self.positions[-1]['TimeClose'])
            data_shows = pd.DataFrame(self.data_shows[symbol])
            self.show_candlestick(symbol + " " + self.new_time_frame, data_shows.iloc[start:end + 5],
                             positions_df.loc[positions_df['Symbol'] == symbol],
                             df_balance_history, df_equity_history, start, None, None)

    def create_balance_equity(self):
        j = 0
        for ii in self.index_range:
            time = self.data_shows[self.symbols[0]][self.indexes[self.symbols[0]] + ii]['Time']
            if j >= len(self.positions):
                break
            symbol = self.symbols[0]
            i = self.indexes[symbol] + ii
            row = self.data_shows[symbol][i]
            if j >= len(self.positions):
                break
            position_time = self.adjust_time(self.positions[j]['TimeOpen'], self.new_time_frame)
            while row['Time'] >= position_time:
                self.open(self.positions[j])
                j += 1
                if j >= len(self.positions):
                    break
                position_time = self.adjust_time(self.positions[j]['TimeOpen'], self.new_time_frame)

            for position in self.open_positions:
                if row['Time'] >= self.adjust_time(position['CloseTime'], self.new_time_frame):
                    self.close(position)

            self.equity = self.balance
            for position in self.open_positions:
                symbol = position['Symbol']
                i = self.indexes[symbol] + ii
                row = self.data_shows[symbol][i]
                self.equity += self.cal_profit(position['Type'], position['Symbol'], position['OpenPrice'],
                                               row['Close'], position['Volume'])  # add profit

            self.balances.append([ii, time, self.balance])
            self.equities.append([ii, time, self.equity])

    def open(self, position):
        self.open_positions.append({'Type': position['Type'], 'Symbol': position['Symbol'],
                                    'OpenPrice': position['OpenPrice'], 'OpenTime': position['TimeOpen'],
                                    'ClosePrice': position['PriceClose'], 'CloseTime': position['TimeClose'],
                                    'Volume': position['Volume']})

    def close(self, position):
        self.balance += BacktestCombiner.cal_profit(position['Type'], position['Symbol'], position['OpenPrice'],
                                            position['ClosePrice'], position['Volume'])
        self.open_positions.remove(position)

    def show_candlestick(self, name, df, positions_df, df_balance, df_equity, start, trends, extends):
        algorithm_name = self.backtests[0][3]
        for i in range(1, len(self.backtests)):
            algorithm_name += "_" + self.backtests[i][3]
        output_dir = "Outputs/" + algorithm_name + "/Custom/"
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        output_file(output_dir + name + ".html")
        Candlestick.candlestick_plot(df, positions_df, name, df_balance, df_equity, start,
                                     trends, extends)

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

    @staticmethod
    def adjust_time(time, time_fram):
        if time_fram == "M5":
            time = time.replace(minute=(time.minute // 5) * 5)
        elif time_fram == "M15":
            time = time.replace(minute=(time.minute // 15) * 15)
        elif time_fram == "M30":
            time = time.replace(minute=(time.minute // 30) * 30)
        elif time_fram == "H1":
            time = time.replace(minute=0)
        elif time_fram == "H4":
            time = time.replace(minute=0, hour=(time.hour // 4) * 4)
        elif time_fram == "H12":
            time = time.replace(minute=0, hour=(time.hour // 12) * 12)
        elif time_fram == "D":
            time = time.replace(minute=0, hour=0)
        return time
