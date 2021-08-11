

from MetaTraderChartTool.BasicChartTools import BasicChartTools
from Configuration.Tools.MetaTraderRealTimeToolsConfig import ChartConfig
from Configuration.Trade.OnlineConfig import Config

#############################################################################
# Other required imports
#############################################################################

from threading import Thread, Lock
from time import sleep
from datetime import datetime
import pandas as pd

from Shared.Functions import Functions


#############################################################################
# Class derived from ChartTools includes Data processor for PULL,SUB Data
#############################################################################

class MetaTraderRealTimeToolsManager(BasicChartTools):

    def __init__(self,
                 _name="Polaris",
                 _delay=0.1,
                 _broker_gmt=3,
                 _verbose=False):

        super().__init__([self],  # Registers itself as handler of pull Data via self.onPullData()
                         [self],  # Registers itself as handler of sub Data via self.onSubData()
                         _verbose)
        print("Connected")
        # This strategy's variables
        self._delay = _delay
        self._verbose = _verbose
        self._finished = False

        # Get Historical Data

        symbol = self.reporting.get_curr_symbol()

        if symbol == 0:
            self.connector.shutdown()
            super().__init__([], [], _verbose)
            symbol = self.reporting.get_curr_symbol()

        self.time_frame = ChartConfig.time_frame
        self.symbol = symbol

        self.connector.send_hist_request(_symbol=symbol,
                                          _timeframe=Config.timeframes_dic[self.time_frame],
                                          _count=ChartConfig.candles)
        sleep(2)
        self.history = self.connector._History_DB[symbol + '_' + self.time_frame]
        for item in self.history:
            item['Time'] = datetime.strptime(item['Time'], ChartConfig.date_format)
        print(pd.DataFrame(self.history))

        self._time_identifier = Functions.get_time_id(self.history[-1]['Time'], self.time_frame)

        self.chart_config = ChartConfig(self, self.history, ChartConfig.tool_name)
        self.tool = self.chart_config.tool

        # lock for acquire/release of ZeroMQ connector
        self._lock = Lock()

    def on_pull_data(self, msg):
        pass

    def on_sub_data(self, msg):
        # split msg to get topic and message
        symbol, data = msg.split("&")
        # print('Input on Topic={} with Message={}'.format(symbol, msg))
        time, bid, ask = data.split(';')
        bid = float(bid)
        ask = float(ask)
        time = datetime.strptime(time, Config.tick_date_format)

        self.update_history(time, symbol, bid)
        ##########################################################################

    def update_history(self, time, symbol, bid):
        time_identifier = Functions.get_time_id(time, self.time_frame)

        if self._time_identifier != time_identifier:
            # New Candle Open Section
            self._time_identifier = time_identifier
            last_candle = {"Time": time, "Open": bid, "High": bid,
                           "Low": bid, "Close": bid, "Volume": 1}
            self.history.append(last_candle)
            self.history.pop(0)
            self.tool.on_data(self.history[-1])
            print(symbol)
            print(pd.DataFrame(self.history[-2:-1]))
            print("________________________________________________________________________________")
        else:
            # Update Last Candle Section
            self.update_candle_with_tick(self.history[-1], bid)
            # Signal Section
            self.tool.on_tick()

    @staticmethod
    def update_candle_with_tick(candle, tick):
        candle['High'] = max(candle['High'], tick)
        candle['Low'] = min(candle['Low'], tick)
        candle['Close'] = tick
        candle['Volume'] += 1

    def run(self):
        self.subscribe_to_price_feeds()

    ##########################################################################
    def subscribe_to_price_feeds(self):
        """
        Starts the subscription to the self._symbols list setup during construction.
        1) Setup symbols in Expert Advisor through self._zmq._DWX_MTX_SUBSCRIBE_MARKETDATA_
        2) Starts price feeding through self._zmq._DWX_MTX_SEND_TRACKPRICES_REQUEST_
        """
        # subscribe to all symbols price feeds
        try:
            # Acquire lock
            self._lock.acquire()
            self.connector.subscribe_market_data(self.symbol)
            print('Subscribed to {} price feed'.format(self.symbol))

        finally:
            # Release lock
            self._lock.release()
            sleep(self._delay)

        # configure symbols to receive price feeds
        try:
            # Acquire lock
            self._lock.acquire()
            self.connector.send_track_price_request([self.symbol])
            print('Configuring price feed for {}'.format(self.symbol))

        finally:
            # Release lock
            self._lock.release()
            sleep(self._delay)

    ##########################################################################
    def is_finished(self):
        """ Check if execution finished"""
        return self._finished


""" -----------------------------------------------------------------------------------------------
    -----------------------------------------------------------------------------------------------
    SCRIPT SETUP
    -----------------------------------------------------------------------------------------------
    -----------------------------------------------------------------------------------------------
"""
if __name__ == "__main__":

    # creates object with a predefined configuration: symbol list including EURUSD and GBPUSD
    print('Loading ...')
    launcher = MetaTraderRealTimeToolsManager()

    print('Running')
    launcher.run()

    print('Chart tool is running...')
    while not launcher.is_finished():
        sleep(1)