# %% -----------|| Main Section ||----------
from datetime import datetime
import copy
from Simulation import Utility as Ut

from tqdm import tqdm

from Simulation.InstanceConfig import InstanceConfig

from Simulation import Simulation
from Simulation.Config import Config
from Simulation import Outputs

from Shared.Variables import Variables
from Shared.Functions import Functions

data = {}


class BackTestLauncher:

    def __init__(self):
        self.symbols = InstanceConfig.symbols
        self.start_indexes, self.end_indexes, self.configs, self.algorithm_data_total, self.algorithm_start_indexes, \
            self.algorithm_end_indexes, self.trailing_data_total, self.trailing_start_indexes,\
            self.trailing_end_indexes = self.initialize_data()

        self.algorithm_data, self.trailing_data, self.history_size, self.algorithms, self.re_entrance_algorithms,\
            self.recovery_algorithms, self.close_modes, self.tp_sl_tools, self.trailing_tools,\
            self.account_managements, self.market, self.last_ticket, self.last_algorithm_signal_ticket,\
            self.algorithm_histories, self.trailing_histories, self.buy_open_positions_lens,\
            self.sell_open_positions_lens, self.last_buy_closed, self.last_sell_closed,\
            self.trade_buy_in_candle_counts, self.trade_sell_in_candle_counts, self.virtual_buys, self.virtual_sells, \
            self.recovery_trades = self.initialize_algorithms()

    def run(self):
        # Back Test
        back_test_length = self.end_indexes[self.symbols[0]] - self.start_indexes[self.symbols[0]]
        for ii in tqdm(range(back_test_length)):
            i = self.start_indexes[self.symbols[0]] + ii
            data_time = data[self.symbols[0]][i]['Time']
            # Market Update Section
            self.market.update(data_time)

            for symbol in self.symbols:
                i = self.start_indexes[symbol] + ii
                data_time = data[symbol][i]['Time']

                # Select Symbol Configuration
                history = data[symbol][i - self.history_size:i + 1]

                # Debug Section
                # if data_time == datetime(year=2017, month=2, day=22, hour=0, minute=0):
                #     print(data_time)

                # Ignore Holidays
                if history[-1]['Volume'] == 0:
                    continue

                # Update History
                signal, price = self.update_history(history, symbol)

                # Take Profit And Stop Loss
                stop_loss, take_profit_buy, stop_loss_buy, take_profit_sell, stop_loss_sell =\
                    self.tp_sl(signal, price, symbol)

                # Account Management
                volume = self.account_managements[symbol].calculate(self.market.balance, symbol, price, stop_loss)

                # Algorithm Execution
                self.algorithm_execute(history, signal, price, data_time, symbol, take_profit_buy, stop_loss_buy,
                                       take_profit_sell, stop_loss_sell, volume)

                # Trailing Stop Section
                self.trailing(history, data_time, symbol)

                if self.last_buy_closed[symbol] is None:
                    self.last_buy_closed[symbol] = self.market.get_last_buy_closed(symbol)
                if self.last_sell_closed[symbol] is None:
                    self.last_sell_closed[symbol] = self.market.get_last_sell_closed(symbol)

                # Virtual Tp Sl Check
                self.virtual_check(history, symbol)

                # Re Entrance Algorithm Section
                self.re_entrance(history, data_time, symbol)

                # Recovery Algorithm Section
                self.recovery(symbol, history, data_time)

        # Exit Section
        self.market.exit()
        return self.market

    @staticmethod
    def initialize_data():
        # Simulation init
        Variables.config = Config
        global data
        symbols = InstanceConfig.symbols
        symbols_ratio = InstanceConfig.management_ratio
        algorithm_time_frame = InstanceConfig.algorithm_time_frame
        trailing_time_frame = InstanceConfig.trailing_time_frame
        Config.time_frame_show = algorithm_time_frame
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
        data_total = Simulation.data
        start_indexes = {}
        end_indexes = {}

        for i in range(len(symbols)):
            symbol = symbols[i]
            start_indexes[symbol] = Outputs.index_date_v2(data_total[Config.symbols_dict[symbol]], start_time)
            end_indexes[symbol] = Outputs.index_date_v2(data_total[Config.symbols_dict[symbol]], end_time)

        data_algorithm_paths = []
        data_trailing_paths = []
        for i in range(len(symbols)):
            symbol = symbols[i]
            data_algorithm_paths += ["Data/" + Config.categories_list[symbol] + "/" + symbol +
                                     "/" + algorithm_time_frame + ".csv"]
            data_trailing_paths += ["Data/" + Config.categories_list[symbol] + "/" + symbol +
                                    "/" + trailing_time_frame + ".csv"]
        algorithm_data = Ut.csv_to_df(data_algorithm_paths, date_format=Config.date_format)
        trailing_data = Ut.csv_to_df(data_trailing_paths, date_format=Config.date_format)

        algorithm_start_indexes = {}
        trailing_start_indexes = {}
        algorithm_end_indexes = {}
        trailing_end_indexes = {}
        configs = {}
        for i in range(len(symbols)):
            symbol = symbols[i]
            algorithm_data[i] = algorithm_data[i][algorithm_data[i].Volume != 0]
            trailing_data[i] = trailing_data[i][trailing_data[i].Volume != 0]
            algorithm_start_indexes[symbol] = Outputs.index_date(algorithm_data[i], start_time)
            trailing_start_indexes[symbol] = Outputs.index_date(algorithm_data[i], start_time)
            algorithm_end_indexes[symbol] = Outputs.index_date(algorithm_data[i], end_time)
            trailing_end_indexes[symbol] = Outputs.index_date(algorithm_data[i], end_time)
            algo_data = \
                algorithm_data[i].to_dict('Records')[algorithm_start_indexes[symbol] -
                                                     InstanceConfig.history_size:algorithm_start_indexes[symbol]]
            configs[symbol] = InstanceConfig(symbol, algo_data, InstanceConfig.algorithm_name,
                                             InstanceConfig.repairment_name, InstanceConfig.recovery_name,
                                             InstanceConfig.close_mode, InstanceConfig.tp_sl_name,
                                             InstanceConfig.trailing_name, InstanceConfig.account_management_name,
                                             symbols_ratio[i])
        for symbol in symbols:
            data[symbol] = data_total[Config.symbols_dict[symbol]]

        return start_indexes, end_indexes, configs, algorithm_data, algorithm_start_indexes, algorithm_end_indexes, \
            trailing_data, trailing_start_indexes, trailing_end_indexes

    def initialize_algorithms(self):
        global data
        algorithm_data = {}
        trailing_data = {}

        for i in range(len(self.symbols)):
            algorithm_data[self.symbols[i]] = self.algorithm_data_total[i].to_dict('Records')
            trailing_data[self.symbols[i]] = self.trailing_data_total[i].to_dict('Records')
        # history
        history_size = InstanceConfig.history_size

        # Algorithm
        algorithms = {}
        for symbol in self.symbols:
            algorithms[symbol] = self.configs[symbol].algorithm

        # Re entrance
        re_entrance_algorithms = {}
        for symbol in self.symbols:
            re_entrance_algorithms[symbol] = self.configs[symbol].repairment_algorithm

        # Recovery
        recovery_algorithms = {}
        for symbol in self.symbols:
            recovery_algorithms[symbol] = self.configs[symbol].recovery_algorithm

        # Algorithm Tools
        close_modes = {}
        tp_sl_tools = {}
        trailing_tools = {}
        for symbol in self.symbols:
            close_modes[symbol] = self.configs[symbol].close_mode
            tp_sl_tools[symbol] = self.configs[symbol].tp_sl_tool
            trailing_tools[symbol] = self.configs[symbol].trailing_tool

        # Account Management
        account_managements = {}
        for symbol in self.symbols:
            account_managements[symbol] = self.configs[symbol].account_management

        # Market Config
        start_time = datetime.strptime(Config.start_date, Config.date_format)
        end_time = datetime.strptime(Config.end_date, Config.date_format)
        market = Simulation.Simulation(Config.leverage, Config.balance, start_time, end_time)

        # OnlineLauncher Requirement
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
        virtual_buys = {}
        virtual_sells = {}
        recovery_trades = {}
        for symbol in self.symbols:

            algorithm_histories[symbol] =\
                algorithm_data[symbol][self.algorithm_start_indexes[symbol] -
                                       history_size:self.algorithm_start_indexes[symbol]]
            trailing_histories[symbol] = \
                trailing_data[symbol][self.trailing_start_indexes[symbol] -
                                      history_size:self.trailing_start_indexes[symbol]]

            buy_open_positions_lens[symbol] = 0
            sell_open_positions_lens[symbol] = 0

            trade_buy_in_candle_counts[symbol] = 0
            trade_sell_in_candle_counts[symbol] = 0

            virtual_buys[symbol] = []
            virtual_sells[symbol] = []

            recovery_trades[symbol] = []

        return algorithm_data, trailing_data, history_size, algorithms, re_entrance_algorithms, recovery_algorithms,\
            close_modes, tp_sl_tools, trailing_tools, account_managements, market, last_ticket,\
            last_algorithm_signal_ticket, algorithm_histories, trailing_histories, buy_open_positions_lens,\
            sell_open_positions_lens, last_buy_closed, last_sell_closed, trade_buy_in_candle_counts,\
            trade_sell_in_candle_counts, virtual_buys, virtual_sells, recovery_trades

    def update_history(self, history, symbol):
        # Algorithm Time ID
        history_time = Functions.get_time_id(history[-1]['Time'], self.configs[symbol].algorithm_time_frame)
        algorithm_time = Functions.get_time_id(self.algorithm_histories[symbol][-1]['Time'], self.configs[symbol].algorithm_time_frame)
        if history_time != algorithm_time:
            # New Candle Open Section
            last_candle = {"Time": history[-1]['Time'], "Open": history[-1]['Open'], "High": history[-1]['High'],
                           "Low": history[-1]['Low'], "Close": history[-1]['Close'],"Volume": history[-1]['Volume']}
            self.algorithm_histories[symbol].append(last_candle)
            self.algorithm_histories[symbol].pop(0)
            signal, price = self.algorithms[symbol].on_data(self.algorithm_histories[symbol][-1], self.market.equity)
            self.recovery_algorithms[symbol].on_data(self.algorithm_histories[symbol][-1])
            self.tp_sl_tools[symbol].on_data(self.algorithm_histories[symbol][-1])
        else:
            # Update Last Candle Section
            self.algorithm_histories[symbol][-1]['High'] = max(self.algorithm_histories[symbol][-1]['High'],history[-1]['High'])
            self.algorithm_histories[symbol][-1]['Low'] = min(self.algorithm_histories[symbol][-1]['Low'], history[-1]['Low'])
            self.algorithm_histories[symbol][-1]['Close'] = history[-1]['Close']
            self.algorithm_histories[symbol][-1]['Volume'] += history[-1]['Volume']
            # Signal Section
            signal, price = self.algorithms[symbol].on_tick()

        # Trailing Time ID
        trailing_time = Functions.get_time_id(self.trailing_histories[symbol][-1]['Time'], self.configs[symbol].trailing_time_frame)
        history_time = Functions.get_time_id(history[-1]['Time'], self.configs[symbol].trailing_time_frame)

        if history_time != trailing_time:
            last_candle = {"Time": history[-1]['Time'], "Open": history[-1]['Open'], "High": history[-1]['High'],
                           "Low": history[-1]['Low'], "Close": history[-1]['Close'],
                           "Volume": history[-1]['Volume']}
            self.trailing_histories[symbol].append(last_candle)
            self.trailing_histories[symbol].pop(0)
            self.trade_buy_in_candle_counts[symbol] = 0
            self.trade_sell_in_candle_counts[symbol] = 0
            self.trailing_tools[symbol].on_data(self.trailing_histories[symbol])
            self.re_entrance_algorithms[symbol].on_data()
        else:
            self.trailing_histories[symbol][-1]['High'] = max(self.trailing_histories[symbol][-1]['High'], history[-1]['High'])
            self.trailing_histories[symbol][-1]['Low'] = min(self.trailing_histories[symbol][-1]['Low'], history[-1]['Low'])
            self.trailing_histories[symbol][-1]['Close'] = history[-1]['Close']
            self.trailing_histories[symbol][-1]['Volume'] += history[-1]['Volume']
        return signal, price

    def tp_sl(self, signal, price, symbol):
        stop_loss, take_profit_buy, stop_loss_buy, take_profit_sell, stop_loss_sell = 0, 0, 0, 0, 0
        if signal == 1 or signal == -1:
            if self.close_modes[symbol] == 'tp_sl' or self.close_modes[symbol] == 'both':
                take_profit_buy, stop_loss_buy = self.tp_sl_tools[symbol].on_tick(self.algorithm_histories[symbol], 'Buy')
                take_profit_sell, stop_loss_sell =\
                    self.tp_sl_tools[symbol].on_tick(self.algorithm_histories[symbol], 'Sell')
                if take_profit_buy != 0:
                    take_profit_buy += price
                if stop_loss_buy != 0:
                    stop_loss_buy += price
                if take_profit_sell != 0:
                    take_profit_sell += price
                if stop_loss_sell != 0:
                    stop_loss_sell += price
            spread = Config.spreads[symbol]
            stop_loss = stop_loss_buy - spread if signal == 1 else stop_loss_sell + spread

        return stop_loss, take_profit_buy, stop_loss_buy, take_profit_sell, stop_loss_sell

    def algorithm_execute(self, history, signal, price, data_time, symbol, take_profit_buy, stop_loss_buy,
                          take_profit_sell, stop_loss_sell, volume):
        config = self.configs[symbol]
        if signal == 1:  # buy signal
            if config.multi_position or \
                    (not config.multi_position and self.market.get_open_buy_positions_count(symbol) == 0):
                if not config.enable_max_trade_per_candle or \
                        (config.enable_max_trade_per_candle and
                         self.trade_buy_in_candle_counts[symbol] < config.max_trade_per_candle):
                    if config.algorithm_force_price and history[-1]['Low'] <= price <= history[-1]['High'] or\
                            not config.algorithm_force_price:
                        if not config.algorithm_force_price and not history[-1]['Low'] <= price <= history[-1]['High']:
                            price = history[-1]['Open']
                        if not config.algorithm_virtual_signal:
                            trade = self.market.buy(data_time, price, symbol, take_profit_buy, stop_loss_buy, volume, self.last_ticket)
                            if trade is not None:
                                self.recovery_trades[symbol].append([trade])
                                self.last_algorithm_signal_ticket[symbol] = self.last_ticket
                                self.last_ticket += 1
                                self.trade_buy_in_candle_counts[symbol] += 1
                        else:
                            self.virtual_buys[symbol].append({'OpenTime': data_time, 'OpenPrice': price,
                                                              'Symbol': symbol, 'TP': take_profit_buy,
                                                              'SL': stop_loss_buy, 'Volume': volume, 'ClosedVolume': 0,
                                                              'Ticket': -1})
                            self.last_algorithm_signal_ticket[symbol] = -1
                            self.trade_buy_in_candle_counts[symbol] += 1

        elif signal == -1:  # sell signal
            if config.multi_position or (
                    not config.multi_position and self.market.get_open_sell_positions_count(symbol) == 0):
                if not config.enable_max_trade_per_candle or \
                        (config.enable_max_trade_per_candle and self.trade_sell_in_candle_counts[
                            symbol] < config.max_trade_per_candle):
                    if config.algorithm_force_price and history[-1]['Low'] <= price <= history[-1]['High'] or\
                            not config.algorithm_force_price:
                        if not config.algorithm_force_price and not history[-1]['Low'] <= price <= history[-1]['High']:
                            price = history[-1]['Open']
                        if not config.algorithm_virtual_signal:
                            trade = self.market.sell(data_time, price, symbol, take_profit_sell, stop_loss_sell, volume, self.last_ticket)
                            if trade is not None:
                                self.recovery_trades[symbol].append([trade])
                                self.last_algorithm_signal_ticket[symbol] = self.last_ticket
                                self.last_ticket += 1
                                self.trade_sell_in_candle_counts[symbol] += 1
                        else:
                            self.virtual_sells[symbol].append({'OpenTime': data_time, 'OpenPrice': price,
                                                               'Symbol': symbol, 'TP': take_profit_sell,
                                                               'SL': stop_loss_sell, 'Volume': volume,
                                                               'ClosedVolume': 0, 'Ticket': -1})
                            self.last_algorithm_signal_ticket[symbol] = -1
                            self.trade_sell_in_candle_counts[symbol] += 1

    def trailing(self, history, data_time, symbol):
        self.last_buy_closed[symbol] = None
        self.last_sell_closed[symbol] = None
        if self.close_modes[symbol] == 'trailing' or self.close_modes[symbol] == 'both':
            open_buy_positions = copy.deepcopy(self.market.open_buy_positions) + self.virtual_buys[symbol]
            for position in open_buy_positions:
                if position['Symbol'] == symbol:
                    entry_point = Outputs.index_date_v2(self.trailing_histories[symbol],
                                                        position['OpenTime'])
                    is_close, close_price = self.trailing_tools[symbol].on_tick(self.trailing_histories[symbol],
                                                                  entry_point, 'Buy', data_time)
                    if is_close:
                        if history[-1]['Low'] <= close_price <= history[-1]['High']:
                            if position['Ticket'] == -1:
                                self.last_buy_closed[symbol] = self.virtual_close(position, history[-1]['Time'], close_price)
                                self.virtual_buys[symbol].remove(position)
                            else:
                                self.market.close(data_time, close_price, position['Volume'], position['Ticket'])
                                for trades in self.recovery_trades[symbol]:
                                    if trades[0]['Ticket'] == position['Ticket']:
                                        self.recovery_trades[symbol].remove(trades)
                                        break
                        elif not self.configs[symbol].force_close_on_algorithm_price and history[-1]['Open'] < close_price:
                            if position['Ticket'] == -1:
                                self.last_buy_closed[symbol] = self.virtual_close(position, history[-1]['Time'],
                                                                        history[-1]['Open'])
                                self.virtual_buys[symbol].remove(position)
                            else:
                                self.market.close(data_time, history[-1]['Open'], position['Volume'], position['Ticket'])
                                for trades in self.recovery_trades[symbol]:
                                    if trades[0]['Ticket'] == position['Ticket']:
                                        self.recovery_trades[symbol].remove(trades)
                                        break

            open_sell_poses = copy.deepcopy(self.market.open_sell_positions) + self.virtual_sells[symbol]
            for position in open_sell_poses:
                if position['Symbol'] == symbol:
                    entry_point = Outputs.index_date_v2(self.trailing_histories[symbol],
                                                        position['OpenTime'])
                    is_close, close_price = self.trailing_tools[symbol].on_tick(self.trailing_histories[symbol],
                                                                                entry_point, 'Sell', data_time)
                    if is_close:
                        if history[-1]['Low'] <= close_price <= history[-1]['High']:
                            if position['Ticket'] == -1:
                                self.last_sell_closed[symbol] = self.virtual_close(position, history[-1]['Time'],
                                                                                   close_price)
                                self.virtual_sells[symbol].remove(position)
                            else:
                                self.market.close(data_time, close_price, position['Volume'], position['Ticket'])
                                for trades in self.recovery_trades[symbol]:
                                    if trades[0]['Ticket'] == position['Ticket']:
                                        self.recovery_trades[symbol].remove(trades)
                                        break
                        elif not self.configs[symbol].force_close_on_algorithm_price and close_price < history[-1]['Open']:
                            if position['Ticket'] == -1:
                                self.last_sell_closed[symbol] = self.virtual_close(position, history[-1]['Time'],
                                                                         history[-1]['Open'])
                                self.virtual_sells[symbol].remove(position)
                            else:
                                self.market.close(data_time, history[-1]['Open'], position['Volume'], position['Ticket'])
                                for trades in self.recovery_trades[symbol]:
                                    if trades[0]['Ticket'] == position['Ticket']:
                                        self.recovery_trades[symbol].remove(trades)
                                        break
            self.trailing_tools[symbol].on_tick_end()

    def virtual_check(self, history, symbol):
        virtual_buys_copy = copy.copy(self.virtual_buys[symbol])
        for virtual_buy in virtual_buys_copy:
            if virtual_buy['SL'] != 0 and history[-1]['Low'] <= virtual_buy['SL']:
                self.last_buy_closed[symbol] = self.virtual_close(virtual_buy, history[-1]['Time'], virtual_buy['SL'])
                self.virtual_buys[symbol].remove(virtual_buy)
            elif virtual_buy['TP'] != 0 and history[-1]['High'] >= virtual_buy['TP']:
                self.last_buy_closed[symbol] = self.virtual_close(virtual_buy, history[-1]['Time'], virtual_buy['TP'])
                self.virtual_buys[symbol].remove(virtual_buy)

        virtual_sells_copy = copy.copy(self.virtual_sells[symbol])
        for virtual_sell in virtual_sells_copy:
            if virtual_sell['SL'] != 0 and history[-1]['High'] + Config.spreads[symbol] >= virtual_sell['SL']:
                self.last_sell_closed[symbol] = self.virtual_close(virtual_sell, history[-1]['Time'],
                                                                   virtual_sell['SL'] + Config.spreads[symbol])
                self.virtual_sells[symbol].remove(virtual_sell)
            elif virtual_sell['TP'] != 0 and history[-1]['Low'] + Config.spreads[symbol] <= virtual_sell['TP']:
                self.last_sell_closed[symbol] =\
                    self.virtual_close(virtual_sell, history[-1]['Time'], virtual_sell['TP'])
                self.virtual_sells[symbol].remove(virtual_sell)

    @staticmethod
    def virtual_close(virtual_position, close_time, close_price):
        return {'StartTime': virtual_position['StartTime'],
                'OpenPrice': virtual_position['OpenPrice'],
                'CloseTime': close_time,
                'ClosePrice': close_price, 'Symbol': virtual_position['Symbol'],
                'SL': virtual_position['SL'],
                'TP': virtual_position['TP'],
                'Volume': virtual_position['Volume'], 'Ticket': virtual_position['Ticket']}

    def re_entrance(self, history, data_time, symbol):
        config = self.configs[symbol]
        if config.re_entrance_enable:
            is_buy_closed, is_sell_closed = False, False
            start_index_position_buy, start_index_position_sell = 0, 0
            is_algorithm_signal = False
            profit_in_pip = 0
            if self.buy_open_positions_lens[symbol] > self.market.get_open_buy_positions_count(symbol) + len(
                    self.virtual_buys[symbol]):
                is_buy_closed = True
                start_index_position_buy = Outputs.index_date_v2(self.algorithm_histories[symbol],
                                                                 self.last_buy_closed[symbol]['OpenTime'])
                if start_index_position_buy == -1:
                    start_index_position_buy = len(self.algorithm_histories[symbol]) - 1
                if self.last_buy_closed[symbol]['Ticket'] == self.last_algorithm_signal_ticket[symbol]:
                    is_algorithm_signal = True
                position = self.last_buy_closed[symbol]
                profit_in_pip = (position['ClosePrice'] - position['OpenPrice']) * 10 ** Config.symbols_pip[
                    position['Symbol']] / 10
            if self.sell_open_positions_lens[symbol] > self.market.get_open_sell_positions_count(symbol) + len(
                    self.virtual_sells[symbol]):
                is_sell_closed = True
                start_index_position_sell = Outputs.index_date_v2(self.algorithm_histories[symbol],
                                                                  self.last_sell_closed[symbol]['OpenTime'])
                if start_index_position_sell == -1:
                    start_index_position_sell = len(self.algorithm_histories[symbol]) - 1
                if self.last_sell_closed[symbol]['Ticket'] == self.last_algorithm_signal_ticket[symbol]:
                    is_algorithm_signal = True
                position = self.last_sell_closed[symbol]
                profit_in_pip = (position['OpenPrice'] - position['ClosePrice']) * 10 ** Config.symbols_pip[
                    position['Symbol']] / 10

            signal_re_entrance, price_re_entrance =\
                self.re_entrance_algorithms[symbol].on_tick(self.algorithm_histories[symbol], is_buy_closed,
                                                            is_sell_closed, profit_in_pip, start_index_position_buy,
                                                            start_index_position_sell,
                                                            len(self.algorithm_histories[symbol]) - 1)

            stop_loss, take_profit_buy, stop_loss_buy, take_profit_sell, stop_loss_sell = \
                self.tp_sl(signal_re_entrance, price_re_entrance, symbol)

            # Account Management
            volume = self.account_managements[symbol].calculate(self.market.balance, symbol, price_re_entrance,
                                                                stop_loss)

            if signal_re_entrance == 1:  # re entrance buy signal
                if config.multi_position or (
                        not config.multi_position and self.market.get_open_buy_positions_count(symbol) == 0):
                    if not config.enable_max_trade_per_candle or \
                            (config.enable_max_trade_per_candle and self.trade_buy_in_candle_counts[
                                symbol] < config.max_trade_per_candle):
                        if not config.force_re_entrance_price and price_re_entrance <= history[-1]['Open']:
                            self.market.buy(data_time, history[-1]['Open'], symbol, take_profit_buy, stop_loss_buy,
                                            volume, self.last_ticket)
                            self.last_ticket += 1
                            self.trade_buy_in_candle_counts[symbol] += 1
                            self.re_entrance_algorithms[symbol].reset_triggers('buy')
                        elif history[-1]['Low'] <= price_re_entrance <= history[-1]['High']:
                            self.market.buy(data_time, price_re_entrance, symbol, take_profit_buy, stop_loss_buy,
                                            volume, self.last_ticket)
                            self.last_ticket += 1
                            self.trade_buy_in_candle_counts[symbol] += 1
                            self.re_entrance_algorithms[symbol].reset_triggers('buy')
            elif signal_re_entrance == -1:  # re entrance sell signal
                if config.multi_position or (
                        not config.multi_position and self.market.get_open_sell_positions_count(symbol) == 0):
                    if not config.enable_max_trade_per_candle or \
                            (config.enable_max_trade_per_candle and self.trade_sell_in_candle_counts[
                                symbol] < config.max_trade_per_candle):
                        if not config.force_re_entrance_price and price_re_entrance >= history[-1]['Open']:
                            self.market.sell(data_time, history[-1]['Open'], symbol, take_profit_sell, stop_loss_sell,
                                             volume, self.last_ticket)
                            self.last_ticket += 1
                            self.trade_sell_in_candle_counts[symbol] += 1
                            self.re_entrance_algorithms[symbol].reset_triggers('sell')
                        elif history[-1]['Low'] <= price_re_entrance <= history[-1]['High']:
                            self.market.sell(data_time, price_re_entrance, symbol, take_profit_sell, stop_loss_sell,
                                             volume, self.last_ticket)
                            self.last_ticket += 1
                            self.trade_sell_in_candle_counts[symbol] += 1
                            self.re_entrance_algorithms[symbol].reset_triggers('sell')

            self.buy_open_positions_lens[symbol] = self.market.get_open_buy_positions_count(symbol) + len(self.virtual_buys[symbol])
            self.sell_open_positions_lens[symbol] = self.market.get_open_sell_positions_count(symbol) + len(self.virtual_sells[symbol])

    def recovery(self, symbol, history, data_time):
        if self.configs[symbol].recovery_enable:
            for i in range(len(self.recovery_trades[symbol])):
                recovery_signal, modify_signals = self.recovery_algorithms[symbol].on_tick(self.recovery_trades[symbol][i])
                if recovery_signal['Signal'] == 1:
                    if recovery_signal['TP'] != 0:
                        recovery_signal['TP'] += history[-1]['Close']
                    trade = self.market.buy(data_time, recovery_signal['Price'], symbol, recovery_signal['TP'], 0,
                                            recovery_signal['Volume'], self.last_ticket)
                    if trade is not None:
                        self.last_ticket += 1
                        self.recovery_trades[symbol][i].append(trade)
                        for modify_signal in modify_signals:
                            if modify_signal['TP'] != 0:
                                modify_signal['TP'] += history[-1]['Close']
                            self.market.modify(modify_signal['Ticket'], modify_signal['TP'], 0)

                elif recovery_signal['Signal'] == -1:
                    if recovery_signal['TP'] != 0:
                        recovery_signal['TP'] += history[-1]['Close']
                    trade = self.market.sell(data_time, recovery_signal['Price'], symbol, recovery_signal['TP'], 0,
                                             recovery_signal['Volume'], self.last_ticket)
                    if trade is not None:
                        self.last_ticket += 1
                        self.recovery_trades[symbol][i].append(trade)
                        for modify_signal in modify_signals:
                            if modify_signal['TP']:
                                modify_signal['TP'] += history[-1]['Close']
                            self.market.modify(modify_signal['Ticket'], modify_signal['TP'], 0)

            recovery_trades_copy = copy.copy(self.recovery_trades[symbol])
            for i in range(len(recovery_trades_copy)):
                if (recovery_trades_copy[i][0]['Type'] == 'Buy' and
                    history[-1]['High'] > recovery_trades_copy[i][0]['TP'] != 0) or \
                        (recovery_trades_copy[i][0]['Type'] == 'Sell' and history[-1]['Low'] + Config.spreads[
                            symbol] < recovery_trades_copy[i][0]['TP'] != 0):
                    self.recovery_algorithms[symbol].tp_touched(recovery_trades_copy[i][0]['Ticket'])
                    self.recovery_trades[symbol].remove(recovery_trades_copy[i])
            self.recovery_algorithms[symbol].on_tick_end()


# Output Section
launcher = BackTestLauncher()
market_executed = launcher.run()
Simulation.get_output(market_executed)
