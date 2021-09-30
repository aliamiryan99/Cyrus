
# Append path for main project folder
import sys

sys.path.append('../../..')

# Import ZMQ-Strategy from relative path
from MetaTrader.MQTT_Strategy import DWX_ZMQ_Strategy
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


#############################################################################
# Class derived from DWZ_ZMQ_Strategy includes Data processor for PULL,SUB Data
#############################################################################

class OnlineTickDataWriter(DWX_ZMQ_Strategy):

    def __init__(self,
                 _name="Polaris",
                 _symbols=InstanceConfig.symbols,
                 _time_frame="D1",
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
        self._time_frame = _time_frame

        # Get Historical Data
        self.management_ratio = InstanceConfig.management_ratio
        self.algorithm_time_frame = InstanceConfig.algorithm_time_frame
        self.trailing_time_frame = InstanceConfig.trailing_time_frame

        time_frame = _time_frame
        time_frame_ratio = 1
        if time_frame in Config.secondary_timefarmes.keys():
            time_frame = Config.secondary_timefarmes[time_frame]
            algorithm_time_frame_ratio = Config.secondary_timefarmes_ratio[_time_frame]

        self._histories = {}
        self.tick_history = {}
        self._time_identifiers = {}
        for i in range(len(_symbols)):
            symbol = _symbols[i]
            self._zmq._DWX_MTX_SEND_HIST_REQUEST_(_symbol=symbol,
                                                  _timeframe=Config.timeframes_dic[time_frame],
                                                  _count=InstanceConfig.history_size * time_frame_ratio)
            sleep(2)
            self._histories[symbol] = self._zmq._History_DB[symbol+'_'+time_frame]
            for item in self._histories[symbol]:
                item['Time'] = datetime.strptime(item['Time'], Config.date_format)
            if time_frame != self.algorithm_time_frame:
                self._histories[symbol] = self.aggregate_data(self._histories[symbol], self.algorithm_time_frame)
            self._time_identifiers[symbol] = Functions.get_time_id(self._histories[symbol][-1]['Time'],
                                                                   self._time_frame)
            self.tick_history[symbol] = {'Time': [], 'Ask': [], 'Bid': []}

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
        pass

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
        time = datetime.strptime(time, Config.tick_date_format)

        self.tick_history[symbol]['Time'].append(time)
        self.tick_history[symbol]['Bid'].append(bid)
        self.tick_history[symbol]['Ask'].append(ask)

        # Update History
        self.update_history(time, symbol, bid)

    ##########################################################################
    def update_history(self, time, symbol, bid):
        time_identifier = Functions.get_time_id(time, self._time_frame)

        if self._time_identifiers[symbol] != time_identifier:
            # New Candle Open Section
            self._time_identifiers[symbol] = time_identifier
            last_candle = {"Time": time, "Open": bid, "High": bid,
                           "Low": bid, "Close": bid, "Volume": 1}
            self._histories[symbol].append(last_candle)
            self._histories[symbol].pop(0)
            print(symbol)
            print(pd.DataFrame(self._histories[symbol][-2:-1]))
            print("________________________________________________________________________________")
            self.write_history_tick(symbol, self._histories[symbol][-2]['Time'])
        else:
            # Update Last Candle Section
            self.update_candle_with_tick(self._histories[symbol][-1], bid)
            # Signal Section

    def write_history_tick(self, symbol, time: datetime):
        time_str = time.strftime("%Y.%m.%d %H.%M.%S")
        pd.DataFrame(self.tick_history[symbol]).to_csv(f"MetaTrader/TickData/{symbol}-{time_str}.csv", index=False)
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
    print('Loading Data Writer...')
    launcher = OnlineTickDataWriter(_symbols=['EURUSD.I'], _time_frame="H1")

    # Starts example execution
    print('Running Data Writer...')
    launcher.run()

    # Waits example termination
    print('Data writer is running...')
    while not launcher.isFinished():
        sleep(1)
