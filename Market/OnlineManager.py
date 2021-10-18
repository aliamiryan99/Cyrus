
# Append path for main project folder
import sys

sys.path.append('../../..')

# Import ZMQ-Strategy from relative path
from MetaTrader.MQTT_Strategy import DWX_ZMQ_Strategy
from Configuration.Trade.OnlineConfig import Config
from Configuration.Trade.MarketConfig import MarketConfig
from MetaTrader.Utility import *

from Shared.Variables import Variables
from Shared.Functions import Functions

from Market.MetaTrader import MetaTrader
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

class OnlineManager(DWX_ZMQ_Strategy):

    def __init__(self,
                 _name="Polaris",
                 _symbols=MarketConfig.symbols,
                 _delay=0.1,
                 _wbreak=40,
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

        # Symbols Spread Convert To Price Value
        for key in Config.spreads.keys():
            Config.spreads[key] *= 10 ** -Config.symbols_pip[key]

        # Get Historical Data
        self.time_frame = MarketConfig.time_frame

        time_frame = self.time_frame
        time_frame_ratio = 1
        if self.time_frame in Config.secondary_timefarmes.keys():
            time_frame = Config.secondary_timefarmes[self.time_frame]
            time_frame_ratio = Config.secondary_timefarmes_ratio[self.time_frame]

        self.configs = {}
        self._histories = {}
        self._ask_histories = {}
        self._strategies = {}
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
        self.ask, self.bid = {}, {}

        self.market = MetaTrader(self)

        for i in range(len(_symbols)):
            symbol =_symbols[i]
            self._zmq._DWX_MTX_SEND_HIST_REQUEST_(_symbol=symbol,
                                                  _timeframe=Config.timeframes_dic[time_frame],
                                                  _count=MarketConfig.history_size * time_frame_ratio)
            for i in range(_wbreak):
                sleep(_delay)
                if symbol+'_'+time_frame in self._zmq._History_DB.keys():
                    break
            self._histories[symbol] = self._zmq._History_DB[symbol+'_'+time_frame]
            for item in self._histories[symbol]:
                item['Time'] = datetime.strptime(item['Time'], Config.date_format)
            if time_frame != self.time_frame:
                self._histories[symbol] = self.aggregate_data(self._histories[symbol], self.time_frame)

            self._ask_histories[symbol] = self.add_spread(self._histories[symbol], symbol)

            market_config = MarketConfig(self.market, symbol, self._histories[symbol], self._ask_histories[symbol],
                                         MarketConfig.strategy_name)
            self._strategies[symbol] = market_config.strategy
            self._time_identifiers[symbol] = Functions.get_time_id(self._histories[symbol][-1]['Time'],
                                                                   self.time_frame)
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
            self.configs[symbol] = market_config
            self.ask[symbol] = 0
            self.bid[symbol] = 0

        self._zmq._DWX_MTX_CLOSE_ALL_TRADES_()
        self.balance = self._reporting._get_balance()
        self.equity = self._reporting._get_equity()
        for symbol in self._symbols:
            print(symbol)
            print(pd.DataFrame(self._histories[symbol][-10:]))
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
            elif data['_action'] == 'EXECUTION':
                data['_open_time'] = datetime.strptime(data['_open_time'], Config.date_order_format)
                symbol = data['_symbol']
                if data['_type'] == 0:  # buy
                    data['_type'] = 'Buy'
                    data = self.convert_open_position(data)
                    self.open_buy_trades[symbol].append(data)
                    self.trade_buy_in_candle_counts[symbol] += 1
                elif data['_type'] == 1:  # sell
                    data['_type'] = 'Sell'
                    data = self.convert_open_position(data)
                    self.open_sell_trades[data['Symbol']].append(data)
                    self.trade_sell_in_candle_counts[data['Symbol']] += 1
                if self.is_algorithm_signal[data['Symbol']]:
                    self.last_algorithm_signal_ticket[data['Symbol']] = data['Ticket']
                self.is_algorithm_signal[data['Symbol']] = False
                print("Order Executed : ")
                print(data)
                print("________________________________________________________________________________")
            elif data['_action'] == 'CLOSE':
                data['_close_time'] = datetime.strptime(data['_close_time'], Config.date_order_format)
                found = False
                if data['_response'] != 'NOT_FOUND':
                    for trade in self.open_buy_trades[data['_symbol']]:
                        if data['_ticket'] == trade['Ticket']:
                            self.open_buy_trades[data['_symbol']].remove(trade)
                            self.is_buy_closed[data['_symbol']] = True
                            data['_open_time'] = trade['OpenTime']
                            data['_open_price'] = trade['OpenPrice']
                            data = self.convert_close_position(data)
                            self.last_buy_closed[data['Symbol']] = data
                            self.close_sent_cnt[data['Symbol']] = 0
                            found = True
                    if not found:
                        for trade in self.open_sell_trades[data['_symbol']]:
                            if data['_ticket'] == trade['Ticket']:
                                self.open_sell_trades[data['_symbol']].remove(trade)
                                self.is_sell_closed[data['_symbol']] = True
                                data['_open_time'] = trade['OpenTime']
                                data['_open_price'] = trade['OpenPrice']
                                data = self.convert_close_position(data)
                                self.last_sell_closed[data['Symbol']] = data
                                self.close_sent_cnt[data['Symbol']] = 0
                    print("Close Order Executed : ")
                    print(data)
                    print("________________________________________________________________________________")
            elif data['_action'] == 'MODIFY':
                if data['_response'] == 'FOUND':
                    found = False
                    for trade in self.open_buy_trades[data['_symbol']]:
                        if data['_ticket'] == trade['Ticket']:
                            trade['TP'] = data['_tp']
                            trade['SL'] = data['_sl']
                            found = True
                            print(f"Order Modified : {trade}")
                            print("________________________________________________________________________________")
                    if not found:
                        for trade in self.open_sell_trades[data['_symbol']]:
                            if data['_ticket'] == trade['Ticket']:
                                trade['TP'] = data['_tp']
                                trade['SL'] = data['_sl']
                                print(f"Order Modified : {trade}")
                                print("________________________________________________________________________________")
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
        self.pre_bid_tick_price[symbol] = bid
        time = datetime.strptime(time, Config.tick_date_format)

        # Update History
        self.update_history(time, symbol, bid, ask)

        # Check TP_SL
        self.check_tp_sl(symbol, bid, ask)

    ##########################################################################

    def update_history(self, time, symbol, bid, ask):
        time_identifier = Functions.get_time_id(time, self.time_frame)

        if self._time_identifiers[symbol] != time_identifier:
            # New Candle Open Section
            self._time_identifiers[symbol] = time_identifier
            last_candle = {"Time": time, "Open": bid, "High": bid,
                           "Low": bid, "Close": bid, "Volume": 1}
            last_ask_candle = {"Time": time, "Open": ask, "High": ask,
                                "Low": ask, "Close": ask, "Volume": 1}
            self._histories[symbol].append(last_candle)
            self._histories[symbol].pop(0)
            self._ask_histories[symbol].append(last_ask_candle)
            self._ask_histories[symbol].pop(0)
            self._strategies[symbol].on_data(self._histories[symbol][-1], self._ask_histories[symbol][-1])
            self._reporting._get_balance()
            self._reporting._get_equity()
            self.trade_buy_in_candle_counts[symbol] = 0
            self.trade_sell_in_candle_counts[symbol] = 0
            print(symbol)
            print("BID")
            print(pd.DataFrame(self._histories[symbol][-2:-1]))
            print("________________________________________________________________________________")
            print("ASK")
            print(pd.DataFrame(self._ask_histories[symbol][-2:-1]))
            print("________________________________________________________________________________")
        else:
            # Update Last Candle Section
            self.update_candle_with_tick(self._histories[symbol][-1], bid)
            self.update_candle_with_tick(self._ask_histories[symbol][-1], ask)
            # Signal Section
            self._strategies[symbol].on_tick()

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
                OnlineManager.update_candle_with_candle(new_history[-1], histories[i])
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

    @staticmethod
    def add_spread(history, symbol):
        ask_history = []
        for i in range(len(history)):
            candle = history[i]
            s = Config.spreads[symbol]
            ask_history.append({"Time": candle['Time'], "Open": candle['Open'] + s, "High": candle['High'] + s,
                                "Low": candle['Low'] + s, "Close": candle['Close'] + s, "Volume": candle['Volume']})
        return ask_history