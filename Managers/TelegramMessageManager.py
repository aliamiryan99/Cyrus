
# Append path for main project folder
import sys

sys.path.append('../../..')

# Import ZMQ-Strategy from relative path
from MetaTrader.MetaTraderBase import MetaTraderBase
from Configuration.Trade.OnlineConfig import Config
from Configuration.Trade.InstanceConfig import InstanceConfig
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

import requests

#############################################################################
# Class derived from DWZ_ZMQ_Strategy includes Data processor for PULL,SUB Data
#############################################################################

token = "2079979459:AAG2YHeDckZS57c-fRjRz7rXv8v5OixEfvw"
channel_name = "@polarisIchimoku"
screen_shots_directory = "C:/Users/Polaris-Maju1/AppData/Roaming/MetaQuotes/Terminal/A0CD3313EC8ED5429A4908A9CEAB7D1B/MQL4/Files"


class OnlineMessagingLauncher(MetaTraderBase):

    def __init__(self,
                 connector="Polaris",
                 symbols=InstanceConfig.symbols,
                 w_break=100,
                 delay=0.1,
                 broker_gmt=3,
                 verbose=False):

        # call DWX_ZMQ_Strategy constructor and passes itself as Data processor for handling
        # received Data on PULL and SUB ports
        super().__init__(connector,
                         symbols,
                         broker_gmt,
                         [self],  # Registers itself as handler of pull Data via self.onPullData()
                         [self],  # Registers itself as handler of sub Data via self.onSubData()
                         verbose,
                         pull_port=32771,  # Port for Sending commands
                         push_port=32772,  # Port for Receiving responses
                         sub_port=32773)

        # This strategy's variables
        self.symbols = symbols
        self.delay = delay
        self.verbose = verbose
        self._finished = False

        # Shared Variables
        Variables.config = Config

        # Symbols Spread Convert To Price Value
        for key in Config.spreads.keys():
            Config.spreads[key] *= 10 ** -Config.symbols_pip[key]

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
        self.histories = {}
        self.trailing_histories = {}
        self.algorithms = {}
        self.close_modes = {}
        self.tp_sl_tools = {}
        self.trailing_tools = {}
        self.re_entrance_algorithms = {}
        self.recovery_algorithms = {}
        self.account_managements = {}
        self.time_identifiers = {}
        self.trailing_time_identifiers = {}
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
        self.ask, self.bid = {}, {}

        self.signal_time = {}
        self.signal_price = {}
        self.signal_tp = {}
        self.signal_sl = {}
        for i in range(len(symbols)):
            symbol =symbols[i]
            self.connector.send_hist_request(symbol=symbol,
                                             timeframe=Config.timeframes_dic[algorithm_time_frame],
                                             count=InstanceConfig.history_size * algorithm_time_frame_ratio)
            for i in range(w_break):
                sleep(delay)
                if symbol + '_' + algorithm_time_frame in self.connector.history_db.keys():
                    break
            self.histories[symbol] = self.connector.history_db[symbol+'_'+algorithm_time_frame]
            for item in self.histories[symbol]:
                item['Time'] = datetime.strptime(item['Time'], Config.date_format)
            if algorithm_time_frame != self.algorithm_time_frame:
                self.histories[symbol] = self.aggregate_data(self.histories[symbol], self.algorithm_time_frame)
            instance_config = InstanceConfig(symbol, self.histories[symbol], InstanceConfig.algorithm_name,
                                             InstanceConfig.repairment_name, InstanceConfig.recovery_name,
                                             InstanceConfig.close_mode, InstanceConfig.tp_sl_name,
                                             InstanceConfig.trailing_name, InstanceConfig.account_management_name,
                                             self.management_ratio[i])
            self.algorithms[symbol] = instance_config.algorithm
            self.close_modes[symbol] = instance_config.close_mode
            self.tp_sl_tools[symbol] = instance_config.tp_sl_tool
            self.trailing_tools[symbol] = instance_config.trailing_tool
            self.re_entrance_algorithms[symbol] = instance_config.repairment_algorithm
            self.recovery_algorithms[symbol] = instance_config.recovery_algorithm
            self.account_managements[symbol] = instance_config.account_management
            self.time_identifiers[symbol] = Functions.get_time_id(self.histories[symbol][-1]['Time'],
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
            self.ask[symbol] = 0
            self.bid[symbol] = 0
            self.signal_time[symbol] = 0
            self.signal_price[symbol] = 0
            self.signal_tp[symbol] = 0
            self.signal_sl[symbol] = 0

        for i in range(len(symbols)):
            symbol = symbols[i]
            self.connector.send_hist_request(symbol=symbol,
                                             timeframe=Config.timeframes_dic[trailing_time_frame],
                                             count=InstanceConfig.history_size * trailing_time_frame_ratio)
            for i in range(w_break):
                sleep(delay)
                if symbol + '_' + algorithm_time_frame in self.connector.history_db.keys():
                    break
            self.trailing_histories[symbol] = self.connector._History_DB[symbol + '_' + trailing_time_frame]
            for item in self.trailing_histories[symbol]:
                item['Time'] = datetime.strptime(item['Time'], Config.date_format)
            if trailing_time_frame != self.trailing_time_frame:
                self.trailing_histories[symbol] = self.aggregate_data(self.trailing_histories[symbol],
                                                                       self.trailing_time_frame)
            self.trailing_time_identifiers[symbol] = Functions.get_time_id(self.trailing_histories[symbol][-1]['Time'],
                                                                            self.trailing_time_frame)

        self.connector.close_all_trades()
        self.balance = self.reporting.get_balance()
        self.equity = self.reporting.get_equity()
        for symbol in self.symbols:
            print(symbol)
            print(pd.DataFrame(self.histories[symbol][-10:]))
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
        if '_action' in list(data.keys()):
            if data['_action'] == 'GET_BALANCE':
                self.balance = list(data['_balance'])[0]
            elif data['_action'] == 'GET_EQUITY':
                self.equity = list(data['_equity'])[0]
            elif data['_action'] == "TAKE_SCREEN_SHOOT":
                symbol = data['_symbol']
                if self.is_algorithm_signal[symbol] == 1:
                    print("Buy screen shoot taken")
                    print("________________________________________________________________________________")
                    message = f"Buy \nSymbol : {symbol} \nTime : {self.signal_time[symbol]} \nPrice : {self.signal_price[symbol]}\n"
                    tp_sl_line = False
                    if self.signal_tp[symbol] != 0:
                        message += f"TP: {self.signal_tp[symbol]} "
                        tp_sl_line = True
                    if self.signal_sl[symbol] != 0:
                        message += f"SL: {self.signal_sl[symbol]} "
                        tp_sl_line = True
                    if tp_sl_line:
                        message += "\n"
                    message += f"{InstanceConfig.tag}"
                    sleep(2)
                    self.send_telegram_photo(data['connector'])
                    self.send_telegram_message(message)
                elif self.is_algorithm_signal[data['_symbol']] == -1:
                    print("Sell screen shoot taken")
                    print("________________________________________________________________________________")
                    message = f"Sell \nSymbol : {symbol} \nTime : {self.signal_time[symbol]} \nPrice : {self.signal_price[symbol]}\n"
                    tp_sl_line = False
                    if self.signal_tp[symbol] != 0:
                        message += f"TP: {self.signal_tp[symbol]} "
                        tp_sl_line = True
                    if self.signal_sl[symbol] != 0:
                        message += f"SL: {self.signal_sl[symbol]} "
                        tp_sl_line = True
                    if tp_sl_line:
                        message += "\n"
                    message += f"{InstanceConfig.tag}"
                    sleep(2)
                    self.send_telegram_photo(data['connector'])
                    self.send_telegram_message(message)

        else:
            print(data)

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
        self.ask[symbol], self.bid[symbol] = ask, bid
        max_bid_tick_price = max(bid, self.pre_bid_tick_price[symbol])
        min_bid_tick_price = min(bid, self.pre_bid_tick_price[symbol])
        self.pre_bid_tick_price[symbol] = bid
        time = datetime.strptime(time, Config.tick_date_format)

        # Update History
        signal, price = self.update_history(time, symbol, bid)

        # TP_SL Section
        stop_loss, take_profit_buy, stop_loss_buy, take_profit_sell, stop_loss_sell = \
            self.tp_sl(symbol, signal, ask - bid)

        # Check TP_SL
        self.check_tp_sl(symbol, bid, ask)

        # Account Management Section
        volume = 0
        if signal == 1 or signal == -1:
            volume = max(round(self.account_managements[symbol].calculate(self.balance, symbol, price, stop_loss),
                               Config.volume_digit), 10 ** -Config.volume_digit)

        # Algorithm Section
        self.algorithm_execute(signal, price, time, symbol, volume, take_profit_buy, stop_loss_buy, take_profit_sell,
                               stop_loss_sell, bid)

    ##########################################################################
    def update_history(self, time, symbol, bid):
        time_identifier = Functions.get_time_id(time, self.algorithm_time_frame)
        trailing_time_identifier = Functions.get_time_id(time, self.trailing_time_frame)

        if self.time_identifiers[symbol] != time_identifier:
            # New Candle Open Section
            self.time_identifiers[symbol] = time_identifier
            last_candle = {"Time": time, "Open": bid, "High": bid,
                           "Low": bid, "Close": bid, "Volume": 1}
            self.histories[symbol].append(last_candle)
            self.histories[symbol].pop(0)
            signal, price = self.algorithms[symbol].on_data(self.histories[symbol][-1], self.balance)
            self.recovery_algorithms[symbol].on_data(self.histories[symbol][-1])
            print(symbol)
            print(pd.DataFrame(self.histories[symbol][-2:-1]))
            print("________________________________________________________________________________")
        else:
            # Update Last Candle Section
            self.update_candle_with_tick(self.histories[symbol][-1], bid)
            # Signal Section
            signal, price = self.algorithms[symbol].on_tick()

        if self.trailing_time_identifiers[symbol] != trailing_time_identifier:
            # New Candle Open Section
            self.trailing_time_identifiers[symbol] = trailing_time_identifier
            last_candle = {"Time": time, "Open": bid, "High": bid,
                           "Low": bid, "Close": bid, "Volume": 1}
            self.trailing_histories[symbol].append(last_candle)
            self.trailing_histories[symbol].pop(0)
            self.trade_buy_in_candle_counts[symbol] = 0
            self.trade_sell_in_candle_counts[symbol] = 0
            self.re_entrance_sent[symbol] = False
            self.trailing_tools[symbol].on_data(self.trailing_histories[symbol][:-1])
            self.re_entrance_algorithms[symbol].on_data()
        else:
            # Update Last Candle Section
            self.update_candle_with_tick(self.trailing_histories[symbol][-1], bid)

        return signal, price

    def check_tp_sl(self, symbol, bid, ask):
        open_buy_trades_copy = copy.copy(self.open_buy_trades[symbol])
        for open_buy_trade in open_buy_trades_copy:
            if open_buy_trade['TP'] != 0 and bid >= open_buy_trade['TP']:
                print(f"TP Hit \n Buy Order : {open_buy_trade}")
                print("________________________________________________________________________________")
                self.open_buy_trades[symbol].remove(open_buy_trade)
            elif open_buy_trade['SL'] != 0 and bid <= open_buy_trade['SL']:
                print(f"SL Hit \n Buy Order : {open_buy_trade}")
                print("________________________________________________________________________________")
                self.open_buy_trades[symbol].remove(open_buy_trade)
        open_sell_trades_copy = copy.copy(self.open_sell_trades[symbol])
        for open_sell_trade in open_sell_trades_copy:
            if open_sell_trade['TP'] != 0 and ask <= open_sell_trade['TP']:
                print(f"TP Hit \n Sell Order : {open_sell_trade}")
                print("________________________________________________________________________________")
                self.open_sell_trades[symbol].remove(open_sell_trade)
            if open_sell_trade['SL'] != 0 and ask >= open_sell_trade['SL']:
                print(f"SL Hit \n Sell Order : {open_sell_trade}")
                print("________________________________________________________________________________")
                self.open_sell_trades[symbol].remove(open_sell_trade)

    def tp_sl(self, symbol, signal, spread):
        stop_loss, take_profit_buy, stop_loss_buy, take_profit_sell, stop_loss_sell = 0, 0, 0, 0, 0
        if signal == 1 or signal == -1:
            if self.close_modes[symbol] == 'tp_sl' or self.close_modes[symbol] == 'both':
                take_profit_buy, stop_loss_buy = self.tp_sl_tools[symbol].on_tick(self.histories[symbol], 'Buy')
                take_profit_sell, stop_loss_sell = self.tp_sl_tools[symbol].on_tick(self.histories[symbol], 'Sell')
                stop_loss = stop_loss_buy - spread if signal == 1 else stop_loss_sell + spread
                take_profit_buy = abs(int(take_profit_buy * 10 ** Config.symbols_pip[symbol]))
                stop_loss_buy = abs(int(stop_loss_buy * 10 ** Config.symbols_pip[symbol]))
                take_profit_sell = abs(int(take_profit_sell * 10 ** Config.symbols_pip[symbol]))
                stop_loss_sell = abs(int(stop_loss_sell * 10 ** Config.symbols_pip[symbol]))
        return stop_loss, take_profit_buy, stop_loss_buy, take_profit_sell, stop_loss_sell

    def algorithm_execute(self, signal, price, time, symbol, volume, take_profit_buy, stop_loss_buy, take_profit_sell,
                          stop_loss_sell, bid):
        if self.configs[symbol].max_volume_enable:
            volume = min(volume, self.configs[symbol].max_volume_value)
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
                            self.is_algorithm_signal[symbol] = 1
                            self.signal_time[symbol] = time
                            self.signal_price[symbol] = price
                            self.signal_tp[symbol] = take_profit_buy
                            self.signal_sl[symbol] = stop_loss_buy

                            name = f"{symbol}_{InstanceConfig.algorithm_name}"
                            self.connector.take_screen_shot(name, _symbol=symbol)

                            # message = f"Buy \nSymbol : {symbol} \nTime : {time} \nPrice : {price} TP: {take_profit_buy} , SL: {stop_loss_buy}"
                            # self.send_telegram_message(message)
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
                            (self.configs[symbol].algorithm_force_price and price - region_price <= bid <= price +
                             region_price):
                        if not self.configs[symbol].algorithm_virtual_signal:
                            print(f"Sell Order Sent [{symbol}], [{volume}], [{take_profit_buy}], [{stop_loss_buy}]")
                            print("________________________________________________________________________________")
                            self.is_algorithm_signal[symbol] = -1
                            self.signal_time[symbol] = time
                            self.signal_price[symbol] = price
                            self.signal_tp[symbol] = take_profit_sell
                            self.signal_sl[symbol] = stop_loss_sell

                            name = f"{symbol}_{InstanceConfig.algorithm_name}"
                            self.connector.take_screen_shot(name, _symbol=symbol)

                            # message = f"Sell \nSymbol : {symbol} \nTime : {time} \nPrice : {price} TP: {take_profit_sell} , SL: {stop_loss_sell}"
                            # self.send_telegram_message(message)
                        else:
                            self.virtual_sells[symbol].append({'OpenTime': time, 'OpenPrice': price,
                                                               'Symbol': symbol, 'TP': take_profit_buy,
                                                               'SL': stop_loss_buy, 'Volume': volume,
                                                               'Ticket': -1})
                            self.last_algorithm_signal_ticket[symbol] = -1
                            self.trade_sell_in_candle_counts[symbol] += 1

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
                OnlineMessagingLauncher.update_candle_with_candle(new_history[-1], histories[i])
        return new_history

    @staticmethod
    def convert_open_position(mt_position):
        position = {'Symbol': mt_position['_symbol'], 'OpenTime': mt_position['_open_time'],
                    'OpenPrice': mt_position['_open_price'], 'Volume': mt_position['_volume'],
                    'Ticket': mt_position['_ticket'], 'Type': mt_position['_type']}
        if '_tp' in list(mt_position.keys()):
            position['TP'] = mt_position['_tp']
        else:
            position['TP'] = 0
        if '_sl' in list(mt_position.keys()):
            position['SL'] = mt_position['_sl']
        else:
            position['SL'] = 0
        return position

    @staticmethod
    def convert_close_position(mt_position):
        position = {'Symbol': mt_position['_symbol'], 'OpenTime': mt_position['_open_time'],
                    'OpenPrice': mt_position['_open_price'], 'CloseTime': mt_position['_close_time'],
                    'ClosePrice': mt_position['_close_price'], 'Volume': mt_position['_close_lots'], 'Ticket': mt_position['_ticket']}
        if '_take_profit' in list(mt_position.keys()):
            position['TP'] = mt_position['_take_profit']
        else:
            position['TP'] = 0
        if '_stop_loss' in list(mt_position.keys()):
            position['SL'] = mt_position['_stop_loss']
        else:
            position['SL'] = 0
        return position

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

    @staticmethod
    def send_telegram_message(message):
        request_url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={channel_name}&text={message}"
        requests.get(request_url)

    @staticmethod
    def send_telegram_photo(name):
        url = f"https://api.telegram.org/bot{token}/"
        requests.post(url + 'sendPhoto', data={'chat_id': channel_name},
                      files={'photo': open(f"{screen_shots_directory}/{name}.png", 'rb')})

    ##########################################################################
    def run(self):
        """
        Starts price subscriptions
        """
        self._finished = False

        # Subscribe to all symbols in self.symbols to receive bid,ask prices
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
            self.connector.unsubscribe_all_market_data_request()
            print('Unsubscribing from all topics')

        finally:
            # Release lock
            self._lock.release()
            sleep(self.delay)

        try:
            # Acquire lock
            self._lock.acquire()
            self.connector.send_track_price_request([])
            print('Removing symbols list')
            sleep(self.delay)
            self.connector.send_track_rates_request([])
            print('Removing instruments list')

        finally:
            # Release lock
            self._lock.release()
            sleep(self.delay)

        self._finished = True

    ##########################################################################
    def __subscribe_to_price_feeds(self):
        """
        Starts the subscription to the self.symbols list setup during construction.
        1) Setup symbols in Expert Advisor through self.connector._DWX_MTX_SUBSCRIBE_MARKETDATA_
        2) Starts price feeding through self.connector._DWX_MTX_SEND_TRACKPRICES_REQUEST_
        """
        if len(self.symbols) > 0:
            # subscribe to all symbols price feeds
            for _symbol in self.symbols:
                try:
                    # Acquire lock
                    self._lock.acquire()
                    self.connector.unsubscribe_market_data(_symbol)
                    print('Subscribed to {} price feed'.format(_symbol))

                finally:
                    # Release lock
                    self._lock.release()
                    sleep(self.delay)

            # configure symbols to receive price feeds
            try:
                # Acquire lock
                self._lock.acquire()
                self.connector.send_track_price_request(self.symbols)
                print('Configuring price feed for {} symbols'.format(len(self.symbols)))

            finally:
                # Release lock
                self._lock.release()
                sleep(self.delay)


""" -----------------------------------------------------------------------------------------------
    -----------------------------------------------------------------------------------------------
    SCRIPT SETUP
    -----------------------------------------------------------------------------------------------
    -----------------------------------------------------------------------------------------------
"""
if __name__ == "__main__":

    # creates object with a predefined configuration: symbol list including EURUSD and GBPUSD
    print('Loading Algorithm...')
    launcher = OnlineMessagingLauncher()

    # Starts example execution
    print('Running Algorithm...')
    launcher.run()

    # Waits example termination
    print('Algorithm is running...')
    while not launcher.isFinished():
        sleep(1)
