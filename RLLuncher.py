# %% -----------|| Main Section ||----------
from datetime import datetime
import copy
import csv
import pandas as pd

from tqdm import tqdm

from Simulation import Simulation
from Simulation.Config import Config
from Simulation import Outputs

date_format = "%m/%d/%Y %H:%M "
symbol = "EURUSD"
volume = 0.1
sl = 400
balance = 100000
spread = 20

def data_init(timeFrame):
    Config.time_frame = timeFrame
    Simulation.initialize()
    start_time = datetime.strptime(Config.start_date, Config.date_format)
    end_time = datetime.strptime(Config.end_date, Config.date_format)
    data = Simulation.data
    s_i = Outputs.index_date(data[0], start_time)
    e_i = Outputs.index_date(data[0], end_time)
    return data, s_i, e_i

def get_signals():
    signals = pd.read_csv("inputs/kafyan/Signals_2004-2006.csv")
    signals = signals[['crossTime', 'Var1']]
    signals['crossTime'] = pd.to_datetime(signals['crossTime'])
    signals = signals.values.tolist()
    return signals



def RL_show():
    signals = get_signals()
    data, s_i, e_i = data_init("M1")

    signals_i = 0

    start_time = datetime.strptime(Config.start_date, Config.date_format)
    end_time = datetime.strptime(Config.end_date, Config.date_format)
    market = Simulation.Simulation(spread, Config.leverage, balance, start_time, end_time)

    last_ticket = 0
    stop_loss = sl * 10 ** -Config.symbols_pip[symbol]

    while signals[signals_i][0] < start_time:
        signals_i += 1

    for i in tqdm(range(s_i, e_i)):
        data_time = data[0].iloc[i]['GMT']
        while signals[signals_i][0] < data_time:
            if signals[signals_i][1] == 1:      # buy signal
                open_sell_poses = copy.deepcopy(market.open_sell_positions)
                for position in open_sell_poses:
                    market.close(data_time, data[0].iloc[i]['Close'], volume, position['ticket'])
                market.buy(data_time, data[0].iloc[i]['Close'], symbol, 0, data[0].iloc[i]['Close'] - stop_loss, volume, last_ticket)
                last_ticket += 1
            elif signals[signals_i][1] == -1:       # sell signal
                open_buy_poses = copy.deepcopy(market.open_buy_positions)
                for position in open_buy_poses:
                    market.close(data_time, data[0].iloc[i]['Close'], volume, position['ticket'])
                market.sell(data_time, data[0].iloc[i]['Close'], symbol, 0, data[0].iloc[i]['Close'] + stop_loss, volume, last_ticket)
                last_ticket += 1
            signals_i += 1
        market.update(data_time)
    market.exit()
    return market


market = RL_simulate()
Simulation.get_output(market)

