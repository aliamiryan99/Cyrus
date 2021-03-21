# %% -----------|| Main Section ||----------
from datetime import datetime
import copy
from Simulation import Utility as ut

from tqdm import tqdm

from Simulation.LuncherConfig import LauncherConfig

from Simulation import Simulation
from Simulation.Config import Config
from Simulation import Outputs


def initialize():
    Simulation.initialize()
    start_time = datetime.strptime(Config.start_date, Config.date_format)
    end_time = datetime.strptime(Config.end_date, Config.date_format)
    data = Simulation.data
    start_i = Outputs.index_date(data[0], start_time)
    end_i = Outputs.index_date(data[0], end_time)
    config = LauncherConfig(data[0].to_dict('Records'), start_i)
    data_algorithm_paths = []
    data_algorithm_paths += ["Data/Major/EURUSD/" + config.algorithm_time_frame + ".csv"]
    algorithm_data = ut.csv_to_df(data_algorithm_paths, date_format=Config.date_format)
    algorithm_start_i = Outputs.index_date(algorithm_data[0], start_time)
    algorithm_end_i = Outputs.index_date(algorithm_data[0], end_time)
    return data, start_i, end_i, config, algorithm_data, algorithm_start_i, algorithm_end_i


def simulate():
    # Parameters Section
    symbol = "EURUSD"
    data_total, start_i, end_i, config, algorithm_data_total, algorithm_start_i, algorithm_end_i = initialize()
    data = data_total[Config.symbols_dict[symbol]].to_dict('Records')
    algorithm_data = algorithm_data_total[Config.symbols_dict[symbol]].to_dict('Records')
    # history
    history_size = config.history_size

    # Algorithm Section
    algorithm = config.algorithm

    # Algorithm Tools Section
    close_mode = config.close_mode
    tp_sl_tool = config.tp_sl_tool
    trailing_tool = config.trailing_tool

    # Account Management Section
    account_management = config.account_management

    # Market Config Section
    start_time = datetime.strptime(Config.start_date, Config.date_format)
    end_time = datetime.strptime(Config.end_date, Config.date_format)
    market = Simulation.Simulation(Config.spread, Config.leverage, Config.balance, start_time, end_time)

    # Launcher Section
    last_ticket = 0
    algorithm_time = datetime.now() - datetime.now()
    simulate_time = datetime.now() - datetime.now()
    j = algorithm_start_i
    algorithm_history = algorithm_data[j - history_size:j-1]
    last_candle = {"GMT": data[start_i]['GMT'], "Open": data[start_i]['Open'],
                   "High": data[start_i]['High'],
                   "Low": data[start_i]['Low'], "Close": data[start_i]['Close'], "IsClosed": False,
                   "IsOpen": True}
    algorithm_history.append(last_candle)
    for i in tqdm(range(start_i, end_i)):
        # Algorithm Start Time
        start = datetime.now()
        data_time = data[i]['GMT']

        # Main History
        history = data[i - history_size:i+1]

        # Algorithm History Section
        signal, price = 0, 0
        history_time = history[-1]['GMT'].day
        algorithm_history_time = algorithm_history[-1]['GMT'].day
        if config.algorithm_time_frame == "H1":
            history_time = history[-1]['GMT'].hour
            algorithm_history_time = algorithm_history[-1]['GMT'].hour
        elif config.algorithm_time_frame == "M1":
            history_time = history[-1]['GMT'].minute
            algorithm_history_time = algorithm_history[-1]['GMT'].minute

        if history_time != algorithm_history_time:
            # Signal Section
            signal, price = algorithm.on_data(algorithm_history[-1])
            last_candle = {"GMT": history[-1]['GMT'], "Open": history[-1]['Open'], "High": history[-1]['High'], "Low": history[-1]['Low'], "Close": history[-1]['Close'], "IsClosed": False, "IsOpen": True}
            j += 1
            algorithm_history = algorithm_data[j - history_size:j - 1]
            algorithm_history.append(last_candle)

        algorithm_history[-1]['High'] = max(algorithm_history[-1]['High'], history[-1]['High'])
        algorithm_history[-1]['Low'] = min(algorithm_history[-1]['Low'], history[-1]['Low'])
        algorithm_history[-1]['Close'] = history[-1]['Close']
        algorithm_history[-1]['IsOpen'] = False

        algo_candle = algorithm_history[-1]
        data_candle = algorithm_data[j-1]
        if algo_candle['Open'] == data_candle['Open'] and algo_candle['High'] == data_candle['High'] and algo_candle['Low'] == data_candle['Low'] and algo_candle['Close'] == data_candle['Close']:
            algorithm_history[-1]['IsClosed'] = True

        # Algorithm End Time
        algorithm_time += datetime.now() - start

        # Simulation Start Time
        start = datetime.now()
        # TP_SL Section
        take_profit, stop_loss = 0, 0
        if close_mode == 'tp_sl' or close_mode == 'both':
            position_type = 'buy'
            if signal == -1:
                position_type = 'sell'
            take_profit, stop_loss = tp_sl_tool.on_data(algorithm_history, position_type)
            if take_profit != 0:
                take_profit += price
            if stop_loss != 0:
                stop_loss += price

        # Account Management Section
        volume = account_management.calculate(market.balance, stop_loss, symbol)

        # Trailing Stop Section
        if close_mode == 'trailing' or close_mode == 'both':
            open_sell_poses = copy.deepcopy(market.open_sell_positions)
            for position in open_sell_poses:
                entry_point = Outputs.index_date_v2(algorithm_history, position['start_gmt'])
                is_close, close_price = trailing_tool.on_data(algorithm_history, entry_point, 'sell')
                if is_close:
                    market.close(data_time, close_price, position['volume'], position['ticket'])
            open_buy_positions = copy.deepcopy(market.open_buy_positions)
            for position in open_buy_positions:
                entry_point = Outputs.index_date_v2(algorithm_history, position['start_gmt'])
                is_close, close_price = trailing_tool.on_data(algorithm_history, entry_point, 'buy')
                if is_close:
                    market.close(data_time, close_price, position['volume'], position['ticket'])

        # Simulation Section
        if signal == 1:  # buy signal
            market.buy(data_time, price, symbol, take_profit, stop_loss, volume, last_ticket)
            last_ticket += 1

        elif signal == -1:  # sell signal
            market.sell(data_time, price, symbol, take_profit, stop_loss, volume, last_ticket)
            last_ticket += 1

        # Market Update Section
        market.update(data_time)
        simulate_time = datetime.now() - start
        # Simulation End Time

    # Exit Section
    print(f"algorithm time : {algorithm_time}")
    print(f"simulate time : {simulate_time}")
    market.exit()
    return market


# Output Section
market = simulate()
Simulation.get_output(market)