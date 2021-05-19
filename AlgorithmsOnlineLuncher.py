
# Append path for main project folder
import sys

sys.path.append('../../..')

# Import ZMQ-Strategy from relative path
from MetaTrader.DWX_ZMQ_Strategy import DWX_ZMQ_Strategy
from MetaTrader.Config import Config
from MetaTrader.InstanceConfig import InstanceConfig
from MetaTrader.Utility import *

from Shared.Variables import Variables
from Shared.Functions import Functions
#############################################################################
# Other required imports
#############################################################################

import pandas as pd
from threading import Thread, Lock
from time import sleep
from datetime import datetime
import copy


#############################################################################
# Class derived from DWZ_ZMQ_Strategy includes Data processor for PULL,SUB Data
#############################################################################

class OnlineLauncher(DWX_ZMQ_Strategy):

    def __init__(self,
                 _name="Polaris",
                 _symbols=InstanceConfig.symbols,
                 _delay=0.1,
                 _broker_gmt=3,
                 _verbose=False):

        # call DWX_ZMQ_Strategy constructor and passes itself as Data processor for handling
        # received Data on PULL and SUB ports
        super().__init__(_name,
                         _symbols,
                         _broker_gmt,
                         [self],  # Registers itself as handler of pull Data via self.onPullData()
                         [self],  # Registers itself as handler of sub Data via self.onSubData()
                         _verbose)

        # This strategy's variables
        self._symbols = _symbols
        self._delay = _delay
        self._verbose = _verbose
        self._finished = False

        # Shared Variables
        Variables.config = Config

        # Get Historical Data
        self.management_ratio = InstanceConfig.management_ratio
        self.algorithm_time_frame = InstanceConfig.algorithm_time_frame
        self.trailing_time_frame = InstanceConfig.trailing_time_frame

        algorithm_time_frame = self.algorithm_time_frame
        algorithm_time_frame_ratio = 1
        if self.algorithm_time_frame in Config.secondary_timefarmes.keys():
            algorithm_time_frame = Config.secondary_timefarmes[self.algorithm_time_frame]
            algorithm_time_frame_ratio = Config.secondary_timefarmes_ratio[self.algorithm_time_frame]
        trailing_time_frame = self.trailing_time_frame
        trailing_time_frame_ratio = 1
        if self.trailing_time_frame in Config.secondary_timefarmes.keys():
            trailing_time_frame = Config.secondary_timefarmes[self.trailing_time_frame]
            trailing_time_frame_ratio = Config.secondary_timefarmes_ratio[self.trailing_time_frame]

        self.configs = {}
        self._histories = {}
        self._trailing_histories = {}
        self._algorithms = {}
        self._close_modes = {}
        self._tp_sl_tools = {}
        self._trailing_tools = {}
        self._re_entrance_algorithms = {}
        self._recovery_algorithms = {}
        self._account_managements = {}
        self._time_identifiers = {}
        self._trailing_time_identifiers = {}
        self.open_buy_trades = {}
        self.open_sell_trades = {}
        self.last_buy_closed = {}
        self.last_sell_closed = {}
        self.is_buy_closed = {}
        self.is_sell_closed = {}
        self.last_algorithm_signal_ticket = {}
        self.is_algorithm_signal = {}
        self.trade_buy_in_candle_counts = {}
        self.trade_sell_in_candle_counts = {}
        self.pre_bid_tick_price = {}
        self.close_sent_cnt = {}
        self.virtual_buys = {}
        self.virtual_sells = {}
        self.re_entrance_sent = {}
        self.recovery_trades = {}
        self.recovery_signal_sent = {}
        self.recovery_trades_index = {}
        self.recovery_modify_list = {}
        for i in range(len(_symbols)):
            symbol =_symbols[i]
            self._zmq._DWX_MTX_SEND_HIST_REQUEST_(_symbol=symbol,
                                                  _timeframe=Config.timeframes_dic[algorithm_time_frame],
                                                  _count=InstanceConfig.history_size * algorithm_time_frame_ratio)
            sleep(1)
            self._histories[symbol] = self._zmq._History_DB[symbol+'_'+algorithm_time_frame]
            for item in self._histories[symbol]:
                item['Time'] = datetime.strptime(item['Time'], Config.date_format)
            if algorithm_time_frame != self.algorithm_time_frame:
                self._histories[symbol] = self.aggregate_data(self._histories[symbol], self.algorithm_time_frame)
            instance_config = InstanceConfig(symbol, self._histories[symbol], InstanceConfig.algorithm_name,
                                             InstanceConfig.repairment_name, InstanceConfig.recovery_name,
                                             InstanceConfig.close_mode, InstanceConfig.tp_sl_name,
                                             InstanceConfig.trailing_name, InstanceConfig.account_management_name,
                                             self.management_ratio[i])
            self._algorithms[symbol] = instance_config.algorithm
            self._close_modes[symbol] = instance_config.close_mode
            self._tp_sl_tools[symbol] = instance_config.tp_sl_tool
            self._trailing_tools[symbol] = instance_config.trailing_tool
            self._re_entrance_algorithms[symbol] = instance_config.repairment_algorithm
            self._recovery_algorithms[symbol] = instance_config.recovery_algorithm
            self._account_managements[symbol] = instance_config.account_management
            self._time_identifiers[symbol] = Functions.get_time_id(self._histories[symbol][-1]['Time'],
                                                                   self.algorithm_time_frame)
            self.open_buy_trades[symbol] = []
            self.open_sell_trades[symbol] = []
            self.last_buy_closed[symbol] = {}
            self.last_sell_closed[symbol] = {}
            self.is_buy_closed[symbol] = False
            self.is_sell_closed[symbol] = False
            self.last_algorithm_signal_ticket[symbol] = -1
            self.is_algorithm_signal[symbol] = False
            self.trade_buy_in_candle_counts[symbol] = 0
            self.trade_sell_in_candle_counts[symbol] = 0
            self.pre_bid_tick_price[symbol] = 0
            self.close_sent_cnt[symbol] = 0
            self.virtual_buys[symbol] = []
            self.virtual_sells[symbol] = []
            self.re_entrance_sent[symbol] = False
            self.recovery_trades[symbol] = []
            self.recovery_signal_sent[symbol] = False
            self.recovery_trades_index[symbol] = -1
            self.recovery_modify_list[symbol] = []
            self.configs[symbol] = instance_config

        for i in range(len(_symbols)):
            symbol = _symbols[i]
            self._zmq._DWX_MTX_SEND_HIST_REQUEST_(_symbol=symbol,
                                                  _timeframe=Config.timeframes_dic[trailing_time_frame],
                                                  _count=InstanceConfig.history_size * trailing_time_frame_ratio)
            sleep(0.5)
            self._trailing_histories[symbol] = self._zmq._History_DB[symbol + '_' + trailing_time_frame]
            for item in self._trailing_histories[symbol]:
                item['Time'] = datetime.strptime(item['Time'], Config.date_format)
            if trailing_time_frame != self.trailing_time_frame:
                self._trailing_histories[symbol] = self.aggregate_data(self._trailing_histories[symbol], self.trailing_time_frame)
            self._trailing_time_identifiers[symbol] = Functions.get_time_id(self._trailing_histories[symbol][-1]['Time'],
                                                                       self.trailing_time_frame)

        self._zmq._DWX_MTX_CLOSE_ALL_TRADES_()
        self.balance = self._reporting._get_balance()
        self.equity = self._reporting._get_equity()
        for symbol in self._symbols:
            print(symbol)
            print(pd.DataFrame(self._histories[symbol][-10:]))
            print("Trailing")
            print(pd.DataFrame(self._trailing_histories[symbol][-10:]))
        print("_________________________________________________________________________")

        # lock for acquire/release of ZeroMQ connector
        self._lock = Lock()

    ##########################################################################
    def isFinished(self):
        """ Check if execution finished"""
        return self._finished

    ##########################################################################
    def onPullData(self, data):
        """
        Callback to process new Data received through the PULL port
        """
        if data['_action'] == 'GET_BALANCE':
            self.balance = list(data['_balance'])[0]
        if data['_action'] == 'GET_EQUITY':
            self.equity = list(data['_equity'])[0]
        if data['_action'] == 'EXECUTION':
            data['_open_time'] = datetime.strptime(data['_open_time'], Config.date_order_format)
            symbol = data['_symbol']
            self.re_entrance_sent[symbol] = False
            if data['_type'] == 0:  # buy
                data['_type'] = 'Buy'
                data = self.convert_open_position(data)
                self.open_buy_trades[symbol].append(data)
                self.trade_buy_in_candle_counts[symbol] += 1
                self.take_recovery_signal(symbol, data, 'Buy')
            elif data['_type'] == 1:  # sell
                data['_type'] = 'Sell'
                data = self.convert_open_position(data)
                self.open_sell_trades[data['Symbol']].append(data)
                self.trade_sell_in_candle_counts[data['Symbol']] += 1
                self.take_recovery_signal(symbol, data, 'Sell')
            if self.is_algorithm_signal[data['Symbol']]:
                self.last_algorithm_signal_ticket[data['Symbol']] = data['Ticket']
            self.is_algorithm_signal[data['Symbol']] = False
            print("Order Executed : ")
            print(data)
            print("________________________________________________________________________________")
        if data['_action'] == 'CLOSE':
            for trade in self.open_buy_trades[data['_symbol']]:
                if data['_ticket'] == trade['Ticket']:
                    self.open_buy_trades[data['_symbol']].remove(trade)
                    self.is_buy_closed[data['_symbol']] = True
                    data['_open_time'] = trade['_open_time']
                    data['_open_price'] = trade['_open_price']
                    data = self.convert_close_position(data)
                    self.last_buy_closed[data['Symbol']] = data
                    self.close_sent_cnt[data['Symbol']] = 0
                    for recovery_trade in self.recovery_trades[data['Symbol']]:
                        if recovery_trade[0]['Ticket'] == data['Ticket']:
                            self.recovery_trades[data['Symbol']].remove(recovery_trade)
            for trade in self.open_sell_trades[data['_symbol']]:
                if data['_ticket'] == trade['_ticket']:
                    self.open_sell_trades[data['_symbol']].remove(trade)
                    self.is_sell_closed[data['_symbol']] = True
                    data['_open_time'] = trade['_open_time']
                    data['_open_price'] = trade['_open_price']
                    data = self.convert_close_position(data)
                    self.last_sell_closed[data['Symbol']] = data
                    self.close_sent_cnt[data['Symbol']] = 0
                    for recovery_trade in self.recovery_trades[data['Symbol']]:
                        if recovery_trade[0]['Ticket'] == data['Ticket']:
                            self.recovery_trades[data['Symbol']].remove(recovery_trade)
            print("Close Order Executed : ")
            print(data)
            print("________________________________________________________________________________")

    ##########################################################################
    def onSubData(self, data):
        """
        Callback to process new Data received through the SUB port
        """
        # split msg to get topic and message
        symbol, msg = data.split("&")
        # print('Input on Topic={} with Message={}'.format(symbol, msg))
        time, bid, ask = msg.split(';')
        bid = float(bid)
        ask = float(ask)
        max_bid_tick_price = max(bid, self.pre_bid_tick_price[symbol])
        min_bid_tick_price = min(bid, self.pre_bid_tick_price[symbol])
        self.pre_bid_tick_price[symbol] = bid
        time = datetime.strptime(time, Config.tick_date_format)

        # Update History
        signal, price = self.update_history(time, symbol, bid)

        # TP_SL Section
        stop_loss, take_profit_buy, stop_loss_buy, take_profit_sell, stop_loss_sell = \
            self.tp_sl(symbol, signal, ask - bid)

        # Account Management Section
        volume = 0
        if signal == 1 or signal == -1:
            volume = max(round(self._account_managements[symbol].calculate(self.balance, symbol, price, stop_loss),
                               Config.volume_digit), 10 ** -Config.volume_digit)

        # Algorithm Section
        self.algorithm_execute(signal, price, time, symbol, volume, take_profit_buy, stop_loss_buy, take_profit_sell,
                               stop_loss_sell, bid)

        # Trailing Stop Section
        self.trailing(symbol, time, bid, ask, min_bid_tick_price, max_bid_tick_price)

        # Virtual Positions Stop Loss And Take Profit Check
        self.virtual_check(symbol, time, bid, ask)

        # Re Entrance Algorithm Section
        self.re_entrance(symbol, min_bid_tick_price, max_bid_tick_price, bid, ask)

        # Recovery Algorithm Section
        self.recovery(symbol, ask, bid)

    ##########################################################################
    def update_history(self, time, symbol, bid):
        time_identifier = Functions.get_time_id(time, self.algorithm_time_frame)
        trailing_time_identifier = Functions.get_time_id(time, self.trailing_time_frame)

        if self._time_identifiers[symbol] != time_identifier:
            # New Candle Open Section
            self._time_identifiers[symbol] = time_identifier
            last_candle = {"Time": time, "Open": bid, "High": bid,
                           "Low": bid, "Close": bid, "Volume": 1}
            self._histories[symbol].append(last_candle)
            self._histories[symbol].pop(0)
            signal, price = self._algorithms[symbol].on_data(self._histories[symbol][-1], self.balance)
            self._recovery_algorithms[symbol].on_data(self._histories[symbol][-1])
            print(symbol)
            print(pd.DataFrame(self._histories[symbol][-2:-1]))
            print("________________________________________________________________________________")
        else:
            # Update Last Candle Section
            self.update_candle_with_tick(self._histories[symbol][-1], bid)
            # Signal Section
            signal, price = self._algorithms[symbol].on_tick()

        if self._trailing_time_identifiers[symbol] != trailing_time_identifier:
            # New Candle Open Section
            self._trailing_time_identifiers[symbol] = trailing_time_identifier
            last_candle = {"Time": time, "Open": bid, "High": bid,
                           "Low": bid, "Close": bid, "Volume": 1}
            self._trailing_histories[symbol].append(last_candle)
            self._trailing_histories[symbol].pop(0)
            self.trade_buy_in_candle_counts[symbol] = 0
            self.trade_sell_in_candle_counts[symbol] = 0
            self.re_entrance_sent[symbol] = False
            self._trailing_tools[symbol].on_data(self._trailing_histories[symbol][:-1])
            self._re_entrance_algorithms[symbol].on_data()
            self._reporting._get_balance()
            self._reporting._get_equity()
        else:
            # Update Last Candle Section
            self.update_candle_with_tick(self._trailing_histories[symbol][-1], bid)

        return signal, price

    def tp_sl(self, symbol, signal, spread):
        stop_loss, take_profit_buy, stop_loss_buy, take_profit_sell, stop_loss_sell = 0, 0, 0, 0, 0
        if signal == 1 or signal == -1:
            if self._close_modes[symbol] == 'tp_sl' or self._close_modes[symbol] == 'both':
                take_profit_buy, stop_loss_buy = self._tp_sl_tools[symbol].on_tick(self._histories[symbol], 'Buy')
                take_profit_sell, stop_loss_sell = self._tp_sl_tools[symbol].on_tick(self._histories[symbol], 'Sell')
                stop_loss = stop_loss_buy - spread if signal == 1 else stop_loss_sell + spread
                take_profit_buy = abs(int(take_profit_buy * 10 ** Config.symbols_pip[symbol]))
                stop_loss_buy = abs(int(stop_loss_buy * 10 ** Config.symbols_pip[symbol]))
                take_profit_sell = abs(int(take_profit_sell * 10 ** Config.symbols_pip[symbol]))
                stop_loss_sell = abs(int(stop_loss_sell * 10 ** Config.symbols_pip[symbol]))
        return stop_loss, take_profit_buy, stop_loss_buy, take_profit_sell, stop_loss_sell

    def algorithm_execute(self, signal, price, time, symbol, volume, take_profit_buy, stop_loss_buy, take_profit_sell,
                          stop_loss_sell, bid):
        if signal == 1:  # buy signal
            if self.configs[symbol].multi_position or\
                    (not self.configs[symbol].multi_position and len(self.open_buy_trades[symbol]) == 0):
                if not self.configs[symbol].enable_max_trade_per_candle or \
                        (self.configs[symbol].enable_max_trade_per_candle and self.trade_buy_in_candle_counts[
                            symbol] < self.configs[symbol].max_trade_per_candle):
                    region_price = self.configs[symbol].force_region * 10 ** -Config.symbols_pip[symbol]
                    if not self.configs[symbol].algorithm_force_price or \
                            (self.configs[symbol].algorithm_force_price and price - region_price <= bid <= price + region_price):
                        if not self.configs[symbol].algorithm_virtual_signal:
                            print(f"Buy Order Sent [{symbol}], [{volume}], [{take_profit_buy}], [{stop_loss_buy}]")
                            print("________________________________________________________________________________")
                            self.is_algorithm_signal[symbol] = True
                            self.buy(symbol, volume, take_profit_buy, stop_loss_buy)
                        else:
                            self.virtual_buys[symbol].append({'OpenTime': time, 'OpenPrice': price,
                                                              'Symbol': symbol, 'TP': take_profit_buy,
                                                              'SL': stop_loss_buy, 'Volume': volume,
                                                              'Ticket': -1})
                            self.last_algorithm_signal_ticket[symbol] = -1
                            self.trade_buy_in_candle_counts[symbol] += 1

        elif signal == -1:  # sell signal
            if self.configs[symbol].multi_position or\
                    (not self.configs[symbol].multi_position and len(self.open_sell_trades[symbol]) == 0):
                if not self.configs[symbol].enable_max_trade_per_candle or \
                        (self.configs[symbol].enable_max_trade_per_candle and self.trade_sell_in_candle_counts[
                            symbol] < self.configs[symbol].max_trade_per_candle):
                    region_price = self.configs[symbol].force_region * 10 ** -Config.symbols_pip[symbol]
                    if not self.configs[symbol].algorithm_force_price or \
                            (self.configs[symbol].algorithm_force_price and price - region_price <= bid <= price + region_price):
                        if not self.configs[symbol].algorithm_virtual_signal:
                            print(f"Sell Order Sent [{symbol}], [{volume}], [{take_profit_buy}], [{stop_loss_buy}]")
                            print("________________________________________________________________________________")
                            self.is_algorithm_signal[symbol] = True
                            self.sell(symbol, volume, take_profit_sell, stop_loss_sell)
                        else:
                            self.virtual_sells[symbol].append({'OpenTime': time, 'OpenPrice': price,
                                                               'Symbol': symbol, 'TP': take_profit_buy,
                                                               'SL': stop_loss_buy, 'Volume': volume,
                                                               'Ticket': -1})
                            self.last_algorithm_signal_ticket[symbol] = -1
                            self.trade_sell_in_candle_counts[symbol] += 1

    def trailing(self, symbol, time, bid, ask, min_bid_tick_price, max_bid_tick_price):
        if self._close_modes[symbol] == 'trailing' or self._close_modes[symbol] == 'both':
            open_buy_positions = copy.copy(self.open_buy_trades[symbol]) + self.virtual_buys[symbol]
            for position in open_buy_positions:
                if position['Symbol'] == symbol:
                    entry_point = 0
                    is_close, close_price = self._trailing_tools[symbol].on_tick(self._trailing_histories[symbol], entry_point, 'Buy', time)
                    if is_close and min_bid_tick_price <= close_price <= max_bid_tick_price:
                        region_price = self.configs[symbol].force_region * 10 ** -Config.symbols_pip[symbol]
                        if (self.configs[symbol].force_close_on_algorithm_price and
                            close_price - region_price <= bid <= close_price + region_price) or not self.configs[symbol].force_close_on_algorithm_price:
                            if position['Ticket'] != -1:
                                print(f"Close Order Sent [Buy], [{symbol}], [{position['Ticket']}]")
                                print(
                                    "________________________________________________________________________________")
                                self.close_sent_cnt[symbol] += 1
                                self.close(position['_ticket'])
                                if self.close_sent_cnt[symbol] > 15:
                                    self.open_buy_trades[symbol].remove(position)
                                    self.close_sent_cnt[symbol] = 0
                            else:
                                self.last_buy_closed[symbol] = OnlineLauncher.virtual_close(position, time, bid)
                                self.virtual_buys[symbol].remove(position)
                                self.is_buy_closed[symbol] = True
            open_sell_positions = copy.copy(self.open_sell_trades[symbol]) + self.virtual_sells[symbol]
            for position in open_sell_positions:
                if position['Symbol'] == symbol:
                    entry_point = 0
                    is_close, close_price = self._trailing_tools[symbol].on_tick(self._trailing_histories[symbol], entry_point, 'Sell', time)
                    if is_close and min_bid_tick_price <= close_price <= max_bid_tick_price:
                        region_price = self.configs[symbol].force_region * 10**-Config.symbols_pip[symbol]
                        if (self.configs[symbol].force_close_on_algorithm_price and
                                close_price - region_price <= bid <= close_price + region_price) or not self.configs[symbol].force_close_on_algorithm_price:
                            if position['Ticket'] != -1:
                                print(f"Close Order Sent [Sell], [{symbol}], [{position['Ticket']}]")
                                print(
                                    "________________________________________________________________________________")
                                self.close_sent_cnt[symbol] += 1
                                self.close(position['Ticket'])
                                if self.close_sent_cnt[symbol] > 15:
                                    self.open_sell_trades[symbol].remove(position)
                                    self.close_sent_cnt[symbol] = 0
                            else:
                                self.last_sell_closed[symbol] = OnlineLauncher.virtual_close(position, time, ask)
                                self.virtual_sells[symbol].remove(position)
                                self.is_sell_closed[symbol] = True

    def virtual_check(self, symbol, time, bid, ask):
        virtual_buys_copy = copy.copy(self.virtual_buys[symbol])
        for virtual_buy in virtual_buys_copy:
            if virtual_buy['SL'] != 0 and bid <= virtual_buy['SL']:
                self.last_buy_closed[symbol] = OnlineLauncher.virtual_close(virtual_buy, time, bid)
                self.virtual_buys[symbol].remove(virtual_buy)
                self.is_buy_closed[symbol] = True
            elif virtual_buy['TP'] != 0 and bid >= virtual_buy['TP']:
                self.last_buy_closed[symbol] = OnlineLauncher.virtual_close(virtual_buy, time, bid)
                self.virtual_buys[symbol].remove(virtual_buy)
                self.is_buy_closed[symbol] = True

        virtual_sells_copy = copy.copy(self.virtual_sells[symbol])
        for virtual_sell in virtual_sells_copy:
            if virtual_sell['SL'] != 0 and ask >= virtual_sell['SL']:
                self.last_sell_closed[symbol] = OnlineLauncher.virtual_close(virtual_sell, time, ask)
                self.virtual_sells[symbol].remove(virtual_sell)
                self.is_sell_closed[symbol] = True
            elif virtual_sell['TP'] != 0 and ask <= virtual_sell['TP']:
                self.last_sell_closed[symbol] = OnlineLauncher.virtual_close(virtual_sell, time, ask)
                self.virtual_sells[symbol].remove(virtual_sell)
                self.is_sell_closed[symbol] = True

    def re_entrance(self, symbol, min_bid_tick_price, max_bid_tick_price, bid, ask):
        if self.configs[symbol].re_entrance_enable:
            start_index_position_buy, start_index_position_sell = 0, 0
            profit_in_pip = 0
            if self.is_buy_closed[symbol]:
                start_index_position_buy = index_date_v2(self._histories[symbol],
                                                         self.last_buy_closed[symbol]['OpenTime'])
                if start_index_position_buy == -1:
                    start_index_position_buy = len(self._histories[symbol]) - 1
                position = self.last_buy_closed[symbol]
                profit_in_pip = (position['ClosePrice'] - position['OpenPrice']) * 10 ** Config.symbols_pip[symbol] / 10
            if self.is_sell_closed[symbol]:
                start_index_position_sell = index_date_v2(self._histories[symbol],
                                                          self.last_sell_closed[symbol]['OpenTime'])
                if start_index_position_sell == -1:
                    start_index_position_sell = len(self._histories[symbol]) - 1
                position = self.last_sell_closed[symbol]
                profit_in_pip = (position['OpenPrice'] - position['ClosePrice']) * 10 ** Config.symbols_pip[symbol] / 10

            signal_re_entrance, price_re_entrance =\
                self._re_entrance_algorithms[symbol].on_tick(self._histories[symbol], self.is_buy_closed[symbol],
                                                             self.is_sell_closed[symbol], profit_in_pip,
                                                             start_index_position_buy, start_index_position_sell,
                                                             len(self._histories[symbol]) - 1)
            if self.is_buy_closed[symbol]:
                self.is_buy_closed[symbol] = False
            if self.is_sell_closed[symbol]:
                self.is_sell_closed[symbol] = False

            stop_loss, take_profit_buy, stop_loss_buy, take_profit_sell, stop_loss_sell = \
                self.tp_sl(symbol, signal_re_entrance, ask - bid)

            volume = 0
            if signal_re_entrance == 1 or signal_re_entrance == -1:
                volume = max(round(self._account_managements[symbol].calculate(self.balance, symbol), 2), 0.01)

            if signal_re_entrance == 1:  # re entrance buy signal
                if self.configs[symbol].multi_position or\
                        (not self.configs[symbol].multi_position and len(self.open_buy_trades[symbol]) == 0 and
                        not self.is_algorithm_signal[symbol]):
                    if not self.configs[symbol].enable_max_trade_per_candle or \
                            (self.configs[symbol].enable_max_trade_per_candle and self.trade_buy_in_candle_counts[symbol] < self.configs[symbol].max_trade_per_candle):
                        if not self.configs[symbol].force_re_entrance_price or min_bid_tick_price <= price_re_entrance <= max_bid_tick_price:
                            if not self.re_entrance_sent[symbol]:
                                print(f"Re Entrance Buy Order Sent [{symbol}], [{volume}], [{take_profit_buy}], [{stop_loss_buy}]")
                                print("________________________________________________________________________________")
                                self.buy(symbol, volume, take_profit_buy, stop_loss_buy)
                                self.re_entrance_sent[symbol] = True
            elif signal_re_entrance == -1:  # re entrance sell signal
                if self.configs[symbol].multi_position or\
                        (not self.configs[symbol].multi_position and len(self.open_sell_trades[symbol]) == 0 and
                        not self.is_algorithm_signal[symbol]):
                    if not self.configs[symbol].enable_max_trade_per_candle or \
                            (self.configs[symbol].enable_max_trade_per_candle and self.trade_sell_in_candle_counts[
                                symbol] < self.configs[symbol].max_trade_per_candle):
                        if not self.configs[symbol].force_re_entrance_price or min_bid_tick_price <= price_re_entrance <= max_bid_tick_price:
                            if not self.re_entrance_sent[symbol]:
                                print(f"Re Entrance Sell Order Sent [{symbol}], [{volume}], [{take_profit_buy}], [{stop_loss_buy}]")
                                print("________________________________________________________________________________")
                                self.sell(symbol, volume, take_profit_sell, stop_loss_sell)
                                self.re_entrance_sent[symbol] = True

    def recovery(self, symbol, ask, bid):
        if self.configs[symbol].recovery_enable:
            for i in range(len(self.recovery_trades[symbol])):
                recovery_signal, modify_signals = self._recovery_algorithms[symbol].on_tick(self.recovery_trades[symbol][i])
                if recovery_signal['Signal'] == 1:
                    if recovery_signal['TP'] != 0:
                        recovery_signal['TP'] *= 10 ** Config.symbols_pip[symbol]
                    self.buy(symbol, recovery_signal['Volume'], recovery_signal['TP'], 0)
                    self.recovery_signal_sent[symbol] = True
                    self.recovery_trades_index[symbol] = i
                    self.recovery_modify_list[symbol] = modify_signals

                elif recovery_signal['Signal'] == -1:
                    if recovery_signal['TP'] != 0:
                        recovery_signal['TP'] *= -10 ** Config.symbols_pip[symbol]
                    self.sell(symbol, recovery_signal['Volume'], recovery_signal['TP'], 0)
                    self.recovery_signal_sent[symbol] = True
                    self.recovery_trades_index[symbol] = i
                    self.recovery_modify_list[symbol] = modify_signals

            recovery_trades_copy = copy.copy(self.recovery_trades[symbol])
            for i in range(len(recovery_trades_copy)):
                if (recovery_trades_copy[i][0]['Type'] == 'Buy' and
                    bid > recovery_trades_copy[i][0]['TP'] != 0) or \
                        (recovery_trades_copy[i][0]['Type'] == 'Sell' and ask < recovery_trades_copy[i][0]['TP'] != 0):
                    self._recovery_algorithms[symbol].tp_touched(recovery_trades_copy[i][0]['Ticket'])
                    self.recovery_trades[symbol].remove(recovery_trades_copy[i])
            self._recovery_algorithms[symbol].on_tick_end()

    def take_recovery_signal(self, symbol, data, type):
        if self.recovery_signal_sent[symbol]:
            self.recovery_trades[symbol][self.recovery_trades_index[symbol]].append(data)
            for modify_signal in self.recovery_modify_list[symbol]:
                if modify_signal['TP'] != 0:
                    modify_signal['TP'] *= 10 ** Config.symbols_pip[symbol]
                    if type == 'Sell':
                        modify_signal['TP'] *= -1
                self.modify(modify_signal['Ticket'], modify_signal['TP'], 0)
        elif self.configs[symbol].recovery_enable:
            self.recovery_trades[symbol].append([data])

    @staticmethod
    def aggregate_data(histories, time_frame):
        old_id = Functions.get_time_id(histories[0]['Time'], time_frame)
        new_history = [copy.deepcopy(histories[0])]
        for i in range(1, len(histories)):
            new_id = Functions.get_time_id(histories[i]['Time'], time_frame)
            if new_id != old_id:
                new_history.append(copy.deepcopy(histories[i]))
                old_id = new_id
            else:
                OnlineLauncher.update_candle_with_candle(new_history[-1], histories[i])
        return new_history

    @staticmethod
    def virtual_close(virtual_position, close_time, close_price):
        return {'_open_time': virtual_position['_open_time'],
                '_open_price': virtual_position['_open_price'],
                '_close_time': close_time,
                '_close_price': close_price, '_symbol': virtual_position['_symbol'],
                '_stop_loss': virtual_position['_stop_loss'],
                '_take_profit': virtual_position['_take_profit'],
                '_volume': virtual_position['_volume'], '_ticket': virtual_position['_ticket']}

    @staticmethod
    def convert_open_position(mt_position):
        return {'Symbol': mt_position['_symbol'], 'OpenTime': mt_position['_open_time'],
                'OpenPrice': mt_position['_open_price'], 'TP': mt_position['_tp'],
                'SL': mt_position['_sl'], 'Volume': mt_position['_volume'],
                'Ticket': mt_position['_ticket'], 'Type': mt_position['_type']}

    @staticmethod
    def convert_close_position(mt_position):
        return {'Symbol': mt_position['_symbol'], 'OpenTime': mt_position['_open_time'],
                'OpenPrice': mt_position['_open_price'], 'CloseTime': mt_position['_close_time'],
                'ClosePrice': mt_position['_close_price'], 'TP': mt_position['_take_profit'],
                'SL': mt_position['_stop_loss'], 'Volume': mt_position['_volume'], 'Ticket': mt_position['_ticket']}

    @staticmethod
    def update_candle_with_candle(candle, sub_candle):
        candle['High'] = max(candle['High'], sub_candle['High'])
        candle['Low'] = min(candle['Low'], sub_candle['Low'])
        candle['Close'] = sub_candle['Close']
        candle['Volume'] += sub_candle['Volume']

    @staticmethod
    def update_candle_with_tick(candle, tick):
        candle['High'] = max(candle['High'], tick)
        candle['Low'] = min(candle['Low'], tick)
        candle['Close'] = tick
        candle['Volume'] += 1

    ##########################################################################
    def run(self):
        """
        Starts price subscriptions
        """
        self._finished = False

        # Subscribe to all symbols in self._symbols to receive bid,ask prices
        self.__subscribe_to_price_feeds()

    ##########################################################################
    def stop(self):
        """
        unsubscribe from all market symbols and exits
        """

        # remove subscriptions and stop symbols price feeding
        try:
            # Acquire lock
            self._lock.acquire()
            self._zmq._DWX_MTX_UNSUBSCRIBE_ALL_MARKETDATA_REQUESTS_()
            print('Unsubscribing from all topics')

        finally:
            # Release lock
            self._lock.release()
            sleep(self._delay)

        try:
            # Acquire lock
            self._lock.acquire()
            self._zmq._DWX_MTX_SEND_TRACKPRICES_REQUEST_([])
            print('Removing symbols list')
            sleep(self._delay)
            self._zmq._DWX_MTX_SEND_TRACKRATES_REQUEST_([])
            print('Removing instruments list')

        finally:
            # Release lock
            self._lock.release()
            sleep(self._delay)

        self._finished = True

    ##########################################################################
    def __subscribe_to_price_feeds(self):
        """
        Starts the subscription to the self._symbols list setup during construction.
        1) Setup symbols in Expert Advisor through self._zmq._DWX_MTX_SUBSCRIBE_MARKETDATA_
        2) Starts price feeding through self._zmq._DWX_MTX_SEND_TRACKPRICES_REQUEST_
        """
        if len(self._symbols) > 0:
            # subscribe to all symbols price feeds
            for _symbol in self._symbols:
                try:
                    # Acquire lock
                    self._lock.acquire()
                    self._zmq._DWX_MTX_SUBSCRIBE_MARKETDATA_(_symbol)
                    print('Subscribed to {} price feed'.format(_symbol))

                finally:
                    # Release lock
                    self._lock.release()
                    sleep(self._delay)

            # configure symbols to receive price feeds
            try:
                # Acquire lock
                self._lock.acquire()
                self._zmq._DWX_MTX_SEND_TRACKPRICES_REQUEST_(self._symbols)
                print('Configuring price feed for {} symbols'.format(len(self._symbols)))

            finally:
                # Release lock
                self._lock.release()
                sleep(self._delay)


""" -----------------------------------------------------------------------------------------------
    -----------------------------------------------------------------------------------------------
    SCRIPT SETUP
    -----------------------------------------------------------------------------------------------
    -----------------------------------------------------------------------------------------------
"""
if __name__ == "__main__":

    # creates object with a predefined configuration: symbol list including EURUSD and GBPUSD
    print('Loading Algorithm...')
    launcher = OnlineLauncher()

    # Starts example execution
    print('Running Algorithm...')
    launcher.run()

    # Waits example termination
    print('Algorithm is running...')
    while not launcher.isFinished():
        sleep(1)
    print('Bye!!!')
