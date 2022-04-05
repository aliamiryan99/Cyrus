

from MetaTrader.MetaTraderBase import MetaTraderBase
from Configuration.Tools.MetaTraderRealTimeToolsConfig import ChartConfig
from Configuration.Trade.OnlineConfig import Config

#############################################################################
# Other required imports
#############################################################################

from threading import Lock
from time import sleep
from datetime import datetime
import pandas as pd
import copy

from Shared.Functions import Functions
from Shared.Variables import Variables


#############################################################################
# Class derived from ChartTools includes Data processor for PULL,SUB Data
#############################################################################


class MetaTraderRealTimeToolsManager(MetaTraderBase):

    def __init__(self, w_break=4000, delay=0.01, broker_gmt=3, verbose=False):

        super().__init__(pull_data_handlers=[self],  # Registers itself as handler of pull Data via self.onPullData()
                         sub_data_handlers=[self],  # Registers itself as handler of sub Data via self.onSubData()
                         verbose=verbose, broker_gmt=broker_gmt)
        print("Connected")

        # This strategy's variables
        self.delay = delay
        self.verbose = verbose
        self.w_break = w_break
        self._finished = False

        Variables.config = Config

        self.start_time = datetime.now()
        self.spend_time = datetime.now() - datetime.now()

    def on_pull_data(self, data):
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
                    self.open_buy_trades.append(data)
                elif data['_type'] == 1:  # sell
                    data['_type'] = 'Sell'
                    data = self.convert_open_position(data)
                    self.open_sell_trades.append(data)
                print("Order Executed : ")
                print(data)
                print("________________________________________________________________________________")
            elif data['_action'] == 'CLOSE':
                if data['_response'] != 'NOT_FOUND':
                    data['_close_time'] = datetime.strptime(data['_close_time'], Config.date_order_format)
                    found = False
                    for trade in self.open_buy_trades:
                        if data['_ticket'] == trade['Ticket']:
                            self.open_buy_trades.remove(trade)
                            data['_open_time'] = trade['OpenTime']
                            data['_open_price'] = trade['OpenPrice']
                            data = self.convert_close_position(data)
                            found = True
                    if not found:
                        for trade in self.open_sell_trades:
                            if data['_ticket'] == trade['Ticket']:
                                self.open_sell_trades.remove(trade)
                                data['_open_time'] = trade['OpenTime']
                                data['_open_price'] = trade['OpenPrice']
                                data = self.convert_close_position(data)
                    print("Close Order Executed : ")
                    print(data)
                    print("________________________________________________________________________________")
            elif data['_action'] == 'MODIFY':
                if data['_response'] == 'FOUND':
                    found = False
                    for trade in self.open_buy_trades:
                        if data['_ticket'] == trade['Ticket']:
                            trade['TP'] = data['_tp']
                            trade['SL'] = data['_sl']
                            found = True
                            print(f"Order Modified : {trade}")
                            print("________________________________________________________________________________")
                    if not found:
                        for trade in self.open_sell_trades:
                            if data['_ticket'] == trade['Ticket']:
                                trade['TP'] = data['_tp']
                                trade['SL'] = data['_sl']
                                print(f"Order Modified : {trade}")
                                print(
                                    "________________________________________________________________________________")
        else:
            print(data)

    def on_sub_data(self, msg):
        # split msg to get topic and message
        start_sub = datetime.now()
        symbol, data = msg.split("&")
        # print('Input on Topic={} with Message={}'.format(symbol, msg))
        time, bid, ask = data.split(';')
        bid = float(bid)
        ask = float(ask)
        time = datetime.strptime(time, Config.tick_date_format)

        self.check_tp_sl(bid, ask)

        self.update_history(time, symbol, bid, ask)
        self.spend_time += (datetime.now() - start_sub)
        ##########################################################################

    def update_history(self, time, symbol, bid, ask):
        time_identifier = Functions.get_time_id(time, self.time_frame)

        if self.time_identifier != time_identifier:
            # New Candle Open Section
            self.time_identifier = time_identifier
            last_candle = {"Time": time, "Open": bid, "High": bid,
                           "Low": bid, "Close": bid, "Volume": 1}
            self.history.append(last_candle)
            self.history.pop(0)
            self.tool.on_data(self.history[-1])
            self.connector.send_balance_request()
            print(symbol)
            print(pd.DataFrame(self.history[-2:-1]))
            print(f"SocketTime {self.connector.socket_time}")
            print(f"ReceiveTime {self.connector.receive_time}")
            print(f"HndTime {self.connector.hnd_time}")
            print(f"TotalTime {datetime.now() - self.start_time}")
            print("________________________________________________________________________________")
        else:
            # Update Last Candle Section
            self.update_candle_with_tick(self.history[-1], bid)
            # Signal Section
            self.tool.on_tick(time, bid, ask)

    def run(self, params=None):
        # Get Historical Data
        symbol = self.reporting.get_curr_symbol()

        if symbol == 0:
            self.connector.shutdown()
            super().__init__(pull_data_handlers=[self],
                             # Registers itself as handler of pull Data via self.onPullData()
                             sub_data_handlers=[self],  # Registers itself as handler of sub Data via self.onSubData()
                             verbose=self.verbose, broker_gmt=self.broker_gmt)
            symbol = self.reporting.get_curr_symbol()

        if symbol == 0:
            self.meta_trader_connection = False
        else:
            self.meta_trader_connection = True
            self.time_frame = ChartConfig.time_frame
            if ChartConfig.auto_time_frame:
                period = self.reporting.get_period()
                self.time_frame = Config.timeframes_dic_rev[period]
                ChartConfig.time_frame = self.time_frame

            self.symbol = symbol

            self.connector.history_db = {}
            self.connector.send_hist_request(symbol=symbol, timeframe=Config.timeframes_dic[self.time_frame],
                                             count=ChartConfig.candles)

            ws = pd.to_datetime('now')
            while symbol + '_' + self.time_frame not in self.connector.history_db.keys():
                sleep(self.delay)
                if (pd.to_datetime('now') - ws).total_seconds() > (self.delay * self.w_break):
                    break

            self.history = self.connector.history_db[symbol + '_' + self.time_frame]


            for item in self.history:
                item['Time'] = datetime.strptime(item['Time'], ChartConfig.date_format)
            print(pd.DataFrame(self.history))

            self.time_identifier = Functions.get_time_id(self.history[-1]['Time'], self.time_frame)

            Variables.config = Config

            self.chart_config = ChartConfig(self, self.history, symbol, ChartConfig.tool_name, params)
            self.tool = self.chart_config.tool

            # lock for acquire/release of ZeroMQ connector
            self._lock = Lock()

            self.subscribe_to_price_feeds()

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
            sleep(self.delay)

        # configure symbols to receive price feeds
        try:
            # Acquire lock
            self._lock.acquire()
            self.connector.send_track_price_request([self.symbol])
            print('Configuring price feed for {}'.format(self.symbol))

        finally:
            # Release lock
            self._lock.release()
            sleep(self.delay)

    ##########################################################################

    def check_tp_sl(self, bid, ask):
        open_buy_trades_copy = copy.copy(self.open_buy_trades)
        for open_buy_trade in open_buy_trades_copy:
            if open_buy_trade['TP'] != 0 and bid >= open_buy_trade['TP']:
                print(f"TP Hit \n Buy Order : {open_buy_trade}")
                print("________________________________________________________________________________")
                self.open_buy_trades.remove(open_buy_trade)
            elif open_buy_trade['SL'] != 0 and bid <= open_buy_trade['SL']:
                print(f"SL Hit \n Buy Order : {open_buy_trade}")
                print("________________________________________________________________________________")
                self.open_buy_trades.remove(open_buy_trade)
        open_sell_trades_copy = copy.copy(self.open_sell_trades)
        for open_sell_trade in open_sell_trades_copy:
            if open_sell_trade['TP'] != 0 and ask <= open_sell_trade['TP']:
                print(f"TP Hit \n Sell Order : {open_sell_trade}")
                print("________________________________________________________________________________")
                self.open_sell_trades.remove(open_sell_trade)
            if open_sell_trade['SL'] != 0 and ask >= open_sell_trade['SL']:
                print(f"SL Hit \n Sell Order : {open_sell_trade}")
                print("________________________________________________________________________________")
                self.open_sell_trades.remove(open_sell_trade)

    @staticmethod
    def update_candle_with_tick(candle, tick):
        candle['High'] = max(candle['High'], tick)
        candle['Low'] = min(candle['Low'], tick)
        candle['Close'] = tick
        candle['Volume'] += 1

    def is_finished(self):
        """ Check if execution finished"""
        return self._finished

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
                    'ClosePrice': mt_position['_close_price'], 'Volume': mt_position['_close_lots'],
                    'Ticket': mt_position['_ticket']}
        if '_take_profit' in list(mt_position.keys()):
            position['TP'] = mt_position['_take_profit']
        else:
            position['TP'] = 0
        if '_stop_loss' in list(mt_position.keys()):
            position['SL'] = mt_position['_stop_loss']
        else:
            position['SL'] = 0
        return position


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
        sleep(100)
