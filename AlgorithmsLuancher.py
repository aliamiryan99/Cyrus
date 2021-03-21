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
    # Simulation init
    symbols = LauncherConfig.symbols
    categories = LauncherConfig.categories
    symbols_ratio = LauncherConfig.symbols_ratio
    algorithm_time_frame = LauncherConfig.algorithm_time_frame
    trailing_time_frame = LauncherConfig.trailing_time_frame
    Config.symbols_list.clear()
    Config.symbols_dict.clear()
    for i in range(len(symbols)):
        symbol = symbols[i]
        Config.symbols_list.append(symbol)
        Config.symbols_dict[symbol] = i
        Config.symbols_show[symbol] = 1
    Simulation.initialize()
    start_time = datetime.strptime(Config.start_date, Config.date_format)
    end_time = datetime.strptime(Config.end_date, Config.date_format)
    # algorithm init
    data = Simulation.data
    start_indexes = {}
    end_indexes = {}

    for i in range(len(symbols)):
        symbol = symbols[i]
        start_indexes[symbol] = Outputs.index_date(data[Config.symbols_dict[symbol]], start_time)
        end_indexes[symbol] = Outputs.index_date(data[Config.symbols_dict[symbol]], end_time)

    data_algorithm_paths = []
    data_trailing_paths = []
    for i in range(len(symbols)):
        symbol = symbols[i]
        data_algorithm_paths += ["Data/" + categories[i] + "/" + symbol + "/" + algorithm_time_frame + ".csv"]
        data_trailing_paths += ["Data/" + categories[i] + "/" + symbol + "/" + trailing_time_frame + ".csv"]
    algorithm_data = ut.csv_to_df(data_algorithm_paths, date_format=Config.date_format)
    trailing_data = ut.csv_to_df(data_trailing_paths, date_format=Config.date_format)
    algorithm_start_indexes = {}
    trailing_start_indexes = {}
    algorithm_end_indexes = {}
    trailing_end_indexes = {}
    configs = {}
    for i in range(len(symbols)):
        symbol = symbols[i]
        algorithm_start_indexes[symbol] = Outputs.index_date(algorithm_data[i], start_time)
        trailing_start_indexes[symbol] = Outputs.index_date(algorithm_data[i], start_time)
        algorithm_end_indexes[symbol] = Outputs.index_date(algorithm_data[i], end_time)
        trailing_end_indexes[symbol] = Outputs.index_date(algorithm_data[i], end_time)
        configs[symbol] = LauncherConfig(symbol, algorithm_data[i].to_dict('Records'), algorithm_start_indexes[symbol],
                                         symbols_ratio[i])
    return data, start_indexes, end_indexes, configs, algorithm_data, algorithm_start_indexes, algorithm_end_indexes, \
           trailing_data, trailing_start_indexes, trailing_end_indexes

def get_identifier(time, time_frame):
    identifier = time.day
    if time_frame == "H12":
        identifier = time.hour // 12
    if time_frame == "H4":
        identifier = time.hour // 4
    if time_frame == "H1":
        identifier = time.hour
    if time_frame == "M30":
        identifier = time.minute // 30
    if time_frame == "M15":
        identifier = time.minute // 15
    if time_frame == "M5":
        identifier = time.minute // 5
    if time_frame == "M1":
        identifier = time.minute
    return identifier


def launch():
    # Parameters Section
    symbols = LauncherConfig.symbols
    data_total, start_indexes, end_indexes, configs, algorithm_data_total, algorithm_start_indexes,\
    algorithm_end_indexes, trailing_data_total, trailing_start_indexes, trailing_end_indexes = initialize()
    data = {}
    algorithm_data = {}
    trailing_data = {}
    for symbol in symbols:
        data[symbol] = data_total[Config.symbols_dict[symbol]].to_dict('Records')

    for i in range(len(symbols)):
        algorithm_data[symbols[i]] = algorithm_data_total[i].to_dict('Records')
        trailing_data[symbols[i]] = trailing_data_total[i].to_dict('Records')
    # history
    history_size = LauncherConfig.history_size

    # Algorithm Section
    algorithms = {}
    for symbol in symbols:
        algorithms[symbol] = configs[symbol].algorithm

    # Re entrance Section
    re_entrance_algorithms = {}
    for symbol in symbols:
        re_entrance_algorithms[symbol] = configs[symbol].repairment_algorithm

    # Algorithm Tools Section
    close_modes = {}
    tp_sl_tools = {}
    trailing_tools = {}
    for symbol in symbols:
        close_modes[symbol] = configs[symbol].close_mode
        tp_sl_tools[symbol] = configs[symbol].tp_sl_tool
        trailing_tools[symbol] = configs[symbol].trailing_tool

    # Account Management Section
    account_managements = {}
    for symbol in symbols:
        account_managements[symbol] = configs[symbol].account_management

    # Market Config Section
    start_time = datetime.strptime(Config.start_date, Config.date_format)
    end_time = datetime.strptime(Config.end_date, Config.date_format)
    market = Simulation.Simulation(Config.leverage, Config.balance, start_time, end_time)

    # Launcher Section
    last_ticket = 0
    last_algorithm_signal_ticket = {}
    algorithm_histories = {}
    trailing_histories = {}
    buy_open_positions_lens = {}
    sell_open_positions_lens = {}
    last_buy_closed = {}
    last_sell_closed = {}
    trade_buy_in_candle_counts = {}
    trade_sell_in_candle_counts = {}
    for symbol in symbols:
        row = data[symbol][start_indexes[symbol]]
        last_candle = {"GMT": row['GMT'], "Open": row['Open'], "High": row['High'],
                       "Low": row['Low'], "Close": row['Close'], "Volume": row['Volume']}
        algorithm_histories[symbol] = algorithm_data[symbol][algorithm_start_indexes[symbol] - history_size:algorithm_start_indexes[symbol]]
        algorithm_histories[symbol].append(last_candle)
        trailing_histories[symbol] = trailing_data[symbol][trailing_start_indexes[symbol] - history_size:trailing_start_indexes[symbol]]

        buy_open_positions_lens[symbol] = 0
        sell_open_positions_lens[symbol] = 0

        trade_buy_in_candle_counts[symbol] = 0
        trade_sell_in_candle_counts[symbol] = 0


    back_test_length = end_indexes[symbols[0]] - start_indexes[symbols[0]]
    for ii in tqdm(range(back_test_length)):
        i = start_indexes[symbols[0]] + ii
        data_time = data[symbols[0]][i]['GMT']
        # Market Update Section
        market.update(data_time)

        for symbol in symbols:
            i = start_indexes[symbol] + ii
            # Algorithm Start Time
            start = datetime.now()
            data_time = data[symbol][i]['GMT']

            # Main History
            history = data[symbol][i - history_size:i+1]
            config = configs[symbol]
            algorithm = algorithms[symbol]
            tp_sl_tool = tp_sl_tools[symbol]
            trailing_tool = trailing_tools[symbol]
            re_entrance_algorithm = re_entrance_algorithms[symbol]
            # Algorithm History Section
            signal, price = 0, 0
            history_time = get_identifier(history[-1]['GMT'], config.algorithm_time_frame)
            algorithm_time = get_identifier(algorithm_histories[symbol][-1]['GMT'], config.algorithm_time_frame)

            # if symbol == 'GBPUSD' and data_time == datetime(year=2020, month=3, day=10, hour=14, minute=20):
            #     print(data_time)

            if history[-1]['Volume'] == 0:
                continue

            if history_time != algorithm_time:
                # New Candle Open Section
                last_candle = {"GMT": history[-1]['GMT'], "Open": history[-1]['Open'], "High": history[-1]['High'],
                               "Low": history[-1]['Low'], "Close": history[-1]['Close'], "Volume": history[-1]['Volume']}
                algorithm_histories[symbol].append(last_candle)
                algorithm_histories[symbol].pop(0)
                signal, price = algorithm.on_data(algorithm_histories[symbol][-1])
                re_entrance_algorithm.on_data()
            else:
                # Update Last Candle Section
                algorithm_histories[symbol][-1]['High'] = max(algorithm_histories[symbol][-1]['High'], history[-1]['High'])
                algorithm_histories[symbol][-1]['Low'] = min(algorithm_histories[symbol][-1]['Low'], history[-1]['Low'])
                algorithm_histories[symbol][-1]['Close'] = history[-1]['Close']
                algorithm_histories[symbol][-1]['Volume'] += history[-1]['Volume']
                # Signal Section
                signal, price = algorithm.on_tick(algorithm_histories[symbol][-1])


            trailing_time = get_identifier(trailing_histories[symbol][-1]['GMT'], config.trailing_time_frame)
            history_time = get_identifier(history[-1]['GMT'], config.trailing_time_frame)

            if history_time != trailing_time:
                last_candle = {"GMT": history[-1]['GMT'], "Open": history[-1]['Open'], "High": history[-1]['High'],
                               "Low": history[-1]['Low'], "Close": history[-1]['Close'],
                               "Volume": history[-1]['Volume']}
                trailing_histories[symbol].append(last_candle)
                trailing_histories[symbol].pop(0)
                trade_buy_in_candle_counts[symbol] = 0
                trade_sell_in_candle_counts[symbol] = 0
                trailing_tool.on_data(trailing_histories[symbol][:-1])
            else:
                trailing_histories[symbol][-1]['High'] = max(trailing_histories[symbol][-1]['High'], history[-1]['High'])
                trailing_histories[symbol][-1]['Low'] = min(trailing_histories[symbol][-1]['Low'], history[-1]['Low'])
                trailing_histories[symbol][-1]['Close'] = history[-1]['Close']
                trailing_histories[symbol][-1]['Volume'] += history[-1]['Volume']



            # TP_SL Section
            take_profit, stop_loss, first_stop_loss = 0, 0, 0
            take_profit_buy, stop_loss_buy = 0, 0
            take_profit_sell, stop_loss_sell = 0, 0
            if close_modes[symbol] == 'tp_sl' or close_modes[symbol] == 'both':
                take_profit_buy, stop_loss_buy = tp_sl_tool.on_tick(algorithm_histories[symbol], 'buy')
                take_profit_sell, stop_loss_sell = tp_sl_tool.on_tick(algorithm_histories[symbol], 'sell')
                if take_profit_buy != 0:
                    take_profit_buy += price
                if stop_loss_buy != 0:
                    stop_loss_buy += price
                if take_profit_sell != 0:
                    take_profit_sell += price
                if stop_loss_sell != 0:
                    stop_loss_sell += price
                take_profit, stop_loss = take_profit_buy, stop_loss_buy
                if signal == -1:
                    take_profit, stop_loss = take_profit_sell, stop_loss_sell
                first_stop_loss = stop_loss


            # Account Management Section
            volume = account_managements[symbol].calculate(market.balance, abs(first_stop_loss - price), symbol)

            # Simulation Section
            if signal == 1:  # buy signal
                if config.multi_position or (not config.multi_position and market.get_open_buy_positions_count(symbol) == 0):
                    if not config.enable_max_trade_per_candle or \
                            (config.enable_max_trade_per_candle and trade_buy_in_candle_counts[symbol] < config.max_trade_per_candle):
                        market.buy(data_time, price, symbol, take_profit_buy, stop_loss_buy, volume, last_ticket)
                        last_algorithm_signal_ticket[symbol] = last_ticket
                        last_ticket += 1
                        trade_buy_in_candle_counts[symbol] += 1
            elif signal == -1:  # sell signal
                if config.multi_position or (not config.multi_position and market.get_open_sell_positions_count(symbol) == 0):
                    if not config.enable_max_trade_per_candle or \
                            (config.enable_max_trade_per_candle and trade_sell_in_candle_counts[symbol] < config.max_trade_per_candle):
                        market.sell(data_time, price, symbol, take_profit_sell, stop_loss_sell, volume, last_ticket)
                        last_algorithm_signal_ticket[symbol] = last_ticket
                        last_ticket += 1
                        trade_sell_in_candle_counts[symbol] += 1

            # Trailing Stop Section
            if close_modes[symbol] == 'trailing' or close_modes[symbol] == 'both':
                position_type = 'buy'
                if signal == -1:
                    position_type = 'sell'
                first_stop_loss = trailing_tool.get_first_stop_loss(trailing_histories[symbol],
                                                                    position_type)
                open_buy_positions = copy.deepcopy(market.open_buy_positions)
                for position in open_buy_positions:
                    if position['symbol'] == symbol:
                        entry_point = Outputs.index_date_v2(trailing_histories[symbol],
                                                            position['start_gmt'])
                        is_close, close_price = trailing_tool.on_tick(trailing_histories[symbol],
                                                                      entry_point, 'buy')
                        if is_close:
                            if history[-1]['Low'] <= close_price <= history[-1]['High']:
                                market.close(data_time, close_price, position['volume'], position['ticket'])
                            elif not config.force_close_on_algorithm_price and history[-1]['Open'] < close_price:
                                market.close(data_time, history[-1]['Open'], position['volume'],
                                             position['ticket'])
                open_sell_poses = copy.deepcopy(market.open_sell_positions)
                for position in open_sell_poses:
                    if position['symbol'] == symbol:
                        entry_point = Outputs.index_date_v2(trailing_histories[symbol],
                                                            position['start_gmt'])
                        is_close, close_price = trailing_tool.on_tick(trailing_histories[symbol],
                                                                      entry_point, 'sell')
                        if is_close:
                            if history[-1]['Low'] <= close_price <= history[-1]['High']:
                                market.close(data_time, close_price, position['volume'], position['ticket'])
                            elif not config.force_close_on_algorithm_price and close_price < history[-1]['Open']:
                                market.close(data_time, history[-1]['Open'], position['volume'],
                                             position['ticket'])

            last_buy_closed[symbol] = market.get_last_buy_closed(symbol)
            last_sell_closed[symbol] = market.get_last_sell_closed(symbol)

            # Re Entrance Algorithm Section
            if config.re_entrance_enable:
                is_buy_closed, is_sell_closed = False, False
                start_index_position_buy, start_index_position_sell = 0, 0
                is_algorithm_signal = False
                profit_in_pip = 0
                if buy_open_positions_lens[symbol] > market.get_open_buy_positions_count(symbol):
                    is_buy_closed = True
                    start_index_position_buy = Outputs.index_date_v2(algorithm_histories[symbol], last_buy_closed[symbol]['start_gmt'])
                    if start_index_position_buy == -1:
                        start_index_position_buy = len(algorithm_histories[symbol]) - 1
                    if last_buy_closed[symbol]['ticket'] == last_algorithm_signal_ticket[symbol]:
                        is_algorithm_signal = True
                    position = last_buy_closed[symbol]
                    profit_in_pip = (position['end_price'] - position['start_price']) * 10 ** Config.symbols_pip[position['symbol']] / 10
                if sell_open_positions_lens[symbol] > market.get_open_sell_positions_count(symbol):
                    is_sell_closed = True
                    start_index_position_sell = Outputs.index_date_v2(algorithm_histories[symbol], last_sell_closed[symbol]['start_gmt'])
                    if start_index_position_sell == -1:
                        start_index_position_sell = len(algorithm_histories[symbol]) - 1
                    if last_sell_closed[symbol]['ticket'] == last_algorithm_signal_ticket[symbol]:
                        is_algorithm_signal = True
                    position = last_sell_closed[symbol]
                    profit_in_pip = (position['start_price'] - position['end_price']) * 10 ** Config.symbols_pip[position['symbol']] / 10

                signal_re_entrance, price_re_entrance = re_entrance_algorithm.on_tick(algorithm_histories[symbol], is_buy_closed, is_sell_closed, is_algorithm_signal, profit_in_pip,
                                                                                      start_index_position_buy, start_index_position_sell, len(algorithm_histories[symbol])-1)

                if take_profit_buy != 0:
                    take_profit_buy += price_re_entrance - price
                if stop_loss_buy != 0:
                    stop_loss_buy += price_re_entrance - price
                if take_profit_sell != 0:
                    take_profit_sell += price_re_entrance - price
                if stop_loss_sell != 0:
                    stop_loss_sell += price_re_entrance - price

                if signal_re_entrance == 1:     # re entrance buy signal
                        if config.multi_position or (not config.multi_position and market.get_open_buy_positions_count(symbol) == 0):
                            if not config.enable_max_trade_per_candle or \
                                    (config.enable_max_trade_per_candle and trade_buy_in_candle_counts[symbol] < config.max_trade_per_candle):
                                if not config.force_re_entrance_price and price_re_entrance <= history[-1]['Open']:
                                    market.buy(data_time, history[-1]['Open'], symbol, take_profit_buy, stop_loss_buy, volume, last_ticket)
                                    last_ticket += 1
                                    trade_buy_in_candle_counts[symbol] += 1
                                    re_entrance_algorithm.reset_triggers('buy')
                                elif history[-1]['Low'] <= price_re_entrance <= history[-1]['High']:
                                    market.buy(data_time, price_re_entrance, symbol, take_profit_buy, stop_loss_buy,
                                               volume, last_ticket)
                                    last_ticket += 1
                                    trade_buy_in_candle_counts[symbol] += 1
                                    re_entrance_algorithm.reset_triggers('buy')
                elif signal_re_entrance == -1 :  # re entrance sell signal
                    if config.multi_position or (not config.multi_position and market.get_open_sell_positions_count(symbol) == 0):
                        if not config.enable_max_trade_per_candle or \
                                (config.enable_max_trade_per_candle and trade_sell_in_candle_counts[symbol] < config.max_trade_per_candle):
                            if not config.force_re_entrance_price and price_re_entrance >= history[-1]['Open']:
                                market.sell(data_time, history[-1]['Open'], symbol, take_profit_sell, stop_loss_sell, volume, last_ticket)
                                last_ticket += 1
                                trade_sell_in_candle_counts[symbol] += 1
                                re_entrance_algorithm.reset_triggers('sell')
                            elif history[-1]['Low'] <= price_re_entrance <= history[-1]['High']:
                                market.sell(data_time, price_re_entrance, symbol, take_profit_sell, stop_loss_sell,
                                            volume, last_ticket)
                                last_ticket += 1
                                trade_sell_in_candle_counts[symbol] += 1
                                re_entrance_algorithm.reset_triggers('sell')

                buy_open_positions_lens[symbol] = market.get_open_buy_positions_count(symbol)
                sell_open_positions_lens[symbol] = market.get_open_sell_positions_count(symbol)

            # Simulation End Time

    # Exit Section
    market.exit()
    return market


# Output Section
market = launch()
Simulation.get_output(market)