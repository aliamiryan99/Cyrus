
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
import os


#############################################################################
# Class derived from DWZ_ZMQ_Strategy includes Data processor for PULL,SUB Data
#############################################################################

class OnlineTickDataWriter(MetaTraderBase):

    def __init__(self,
                 name="Polaris",
                 symbols=InstanceConfig.symbols,
                 time_frame="D1",
                 w_break=1000,
                 delay=0.01,
                 broker_gmt=3,
                 verbose=False):

        # call DWX_ZMQ_Strategy constructor and passes itself as Data processor for handling
        # received Data on PULL and SUB ports
        super().__init__(name,
                         symbols,
                         broker_gmt,
                         [self],  # Registers itself as handler of pull Data via self.onPullData()
                         [self],  # Registers itself as handler of sub Data via self.onSubData()
                         verbose)

        # This strategy's variables
        symbol = self.reporting.get_curr_symbol()
        if symbol is not 0:
            symbols = [symbol]
            self.symbols = [symbol]
        self.delay = delay
        self.verbose = verbose
        self._finished = False

        # Get Historical Data
        self.management_ratio = InstanceConfig.management_ratio
        self.algorithm_time_frame = InstanceConfig.algorithm_time_frame
        self.trailing_time_frame = InstanceConfig.trailing_time_frame

        period = self.reporting.get_period()
        time_frame = Config.timeframes_dic_rev[period]

        self.time_frame = time_frame
        time_frame_ratio = 1
        if time_frame in Config.secondary_timefarmes.keys():
            time_frame = Config.secondary_timefarmes[time_frame]
            algorithm_time_frame_ratio = Config.secondary_timefarmes_ratio[time_frame]

        self.histories = {}
        self.tick_history = {}
        self.time_identifiers = {}
        for i in range(len(symbols)):
            symbol = symbols[i]
            self.connector.send_hist_request(symbol=symbol, timeframe=Config.timeframes_dic[time_frame],
                                             count=InstanceConfig.history_size * time_frame_ratio)
            for i in range(w_break):
                sleep(delay)
                if symbol + '_' + time_frame in self.connector.history_db.keys():
                    break
            self.histories[symbol] = self.connector.history_db[symbol+'_'+time_frame]
            for item in self.histories[symbol]:
                item['Time'] = datetime.strptime(item['Time'], Config.date_format)
            # if time_frame != self.algorithm_time_frame:
            #     self.histories[symbol] = self.aggregate_data(self.histories[symbol], self.algorithm_time_frame)
            self.time_identifiers[symbol] = Functions.get_time_id(self.histories[symbol][-1]['Time'],
                                                                   self.time_frame)
            self.tick_history[symbol] = {'Time': [], 'Ask': [], 'Bid': []}

        self.output_dir = f"Data/MetaTrader/{symbol}/TickData/"
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)

        history_dir = f"Data/MetaTrader/{symbol}/{time_frame}/"
        if not os.path.isdir(history_dir):
            os.makedirs(history_dir)

        time_start = self.histories[symbol][0]['Time'].strftime("%Y.%m.%d %H.%M.%S")
        time_end = self.histories[symbol][-1]['Time'].strftime("%Y.%m.%d %H.%M.%S")
        pd.DataFrame(self.histories[symbol]).to_csv(f"{history_dir}{time_start}_{time_end}.csv", index=False)

        for symbol in self.symbols:
            print(symbol)
            print(pd.DataFrame(self.histories[symbol]))
        print("_________________________________________________________________________")

        # lock for acquire/release of ZeroMQ connector
        self._lock = Lock()

    ##########################################################################
    def isFinished(self):
        """ Check if execution finished"""
        return self._finished

    ##########################################################################
    def on_pull_data(self, data):
        """
        Callback to process new Data received through the PULL port
        """
        pass

    ##########################################################################
    def on_sub_data(self, data):
        """
        Callback to process new Data received through the SUB port
        """
        # split msg to get topic and message
        symbol, msg = data.split("&")
        # print('Input on Topic={} with Message={}'.format(symbol, msg))
        time, bid, ask = msg.split(';')
        bid = float(bid)
        ask = float(ask)
        time = datetime.strptime(time, Config.tick_date_format)

        self.tick_history[symbol]['Time'].append(time)
        self.tick_history[symbol]['Bid'].append(bid)
        self.tick_history[symbol]['Ask'].append(ask)

        # Update History
        self.update_history(time, symbol, bid)

    ##########################################################################
    def update_history(self, time, symbol, bid):
        time_identifier = Functions.get_time_id(time, self.time_frame)

        if self.time_identifiers[symbol] != time_identifier:
            # New Candle Open Section
            self.time_identifiers[symbol] = time_identifier
            last_candle = {"Time": time, "Open": bid, "High": bid,
                           "Low": bid, "Close": bid, "Volume": 1}
            self.histories[symbol].append(last_candle)
            self.histories[symbol].pop(0)
            print(symbol)
            print(pd.DataFrame(self.histories[symbol][-2:-1]))
            print("________________________________________________________________________________")
            self.write_history_tick(symbol, self.histories[symbol][-2]['Time'])
        else:
            # Update Last Candle Section
            self.update_candle_with_tick(self.histories[symbol][-1], bid)
            # Signal Section

    def write_history_tick(self, symbol, time: datetime):
        time_str = time.strftime("%Y.%m.%d %H.%M.%S")
        pd.DataFrame(self.tick_history[symbol]).to_csv(f"{self.output_dir}{time_str}.csv", index=False)
        self.clear_history_tick(symbol)

    def clear_history_tick(self, symbol):
        self.tick_history[symbol]['Time'] = []
        self.tick_history[symbol]['Bid'] = []
        self.tick_history[symbol]['Ask'] = []

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
                OnlineTickDataWriter.update_candle_with_candle(new_history[-1], histories[i])
        return new_history

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
                    self.connector.subscribe_market_data(_symbol)
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
    print('Loading Data Writer...')
    launcher = OnlineTickDataWriter(symbols=['EURUSD.I'], time_frame="H1")

    # Starts example execution
    print('Running Data Writer...')
    launcher.run()

    # Waits example termination
    print('Data writer is running...')
    while not launcher.isFinished():
        sleep(1)
