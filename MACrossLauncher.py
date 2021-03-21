
# %% -----------|| Main Section ||----------
from datetime import datetime
import copy
import csv

from tqdm import tqdm
from Algorithms.MACrossAlgorithm import MAAlgorithm


from Simulation import Simulation
from Simulation.Config import Config
from Simulation import Outputs

volume = 0.1
sl = 400
balance = 100000
spread = 20


def initialize():
    Simulation.initialize()
    start_time = datetime.strptime(Config.start_date, Config.date_format)
    end_time = datetime.strptime(Config.end_date, Config.date_format)
    data = Simulation.data
    start_i = Outputs.index_date(data[0], start_time)
    end_i = Outputs.index_date(data[0], end_time)
    return data, start_i, end_i


def simulate():
    symbol = "EURUSD"
    data, start_i, end_i = initialize()
    window_size1 = 20
    window_size2 = 40
    price_type = "Close"    # Open, High, Low, Close
    ma_type = "EMA"     # EMA, SMA, WMA

    start_time = datetime.strptime(Config.start_date, Config.date_format)
    end_time = datetime.strptime(Config.end_date, Config.date_format)
    market = Simulation.Simulation(spread, Config.leverage, balance, start_time, end_time)

    algorithm = MAAlgorithm(data[Config.symbols_dict[symbol]][start_i - 42:start_i], window_size1, window_size2, price_type, ma_type)
    last_ticket = 0

    stop_loss = sl * 10 ** -Config.symbols_pip[symbol]

    algorithm_time = datetime.now()-datetime.now()
    simulate_time = datetime.now()-datetime.now()
    for i in tqdm(range(start_i, end_i)):
        start = datetime.now()
        data_time = data[Config.symbols_dict[symbol]].iloc[i]['GMT']
        signal = algorithm.on_data(data[Config.symbols_dict[symbol]].iloc[i])
        algorithm_time += datetime.now()-start

        start = datetime.now()
        if signal == 1:  # buy signal
            open_sell_poses = copy.deepcopy(market.open_sell_positions)
            for position in open_sell_poses:
                market.close(data_time, data[Config.symbols_dict[symbol]].iloc[i]['Close'], volume, position['ticket'])
            market.buy(data_time, data[Config.symbols_dict[symbol]].iloc[i]['Close'], symbol, 0, data[Config.symbols_dict[symbol]].iloc[i]['Close'] - stop_loss, volume,
                       last_ticket)
            last_ticket += 1
        elif signal == -1:  # sell signal
            open_buy_poses = copy.deepcopy(market.open_buy_positions)
            for position in open_buy_poses:
                market.close(data_time, data[Config.symbols_dict[symbol]].iloc[i]['Close'], volume, position['ticket'])
            market.sell(data_time, data[Config.symbols_dict[symbol]].iloc[i]['Close'], symbol, 0, data[Config.symbols_dict[symbol]].iloc[i]['Close'] + stop_loss, volume,
                        last_ticket)
            last_ticket += 1
        market.update(data_time)
        simulate_time = datetime.now()-start
    print(f"algorithm time : {algorithm_time}")
    print(f"simulate time : {simulate_time}")
    print(f"ratio : {algorithm_time/simulate_time}")
    market.exit()
    return market


market = simulate()
Simulation.get_output(market)

