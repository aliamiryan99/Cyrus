
import zmq
from time import sleep
from pandas import DataFrame, Timestamp
from threading import Thread

# 30-07-2019 10:58 CEST
from zmq.utils.monitor import recv_monitor_message
from datetime import datetime


class ChartToolConnector:

    """
    Setup ZeroMQ -> MetaTrader Connector
    """

    def __init__(self,
                 _ClientID='cyrus_chart_tool_engine',    # Unique ID for this client
                 _host='localhost',         # Host to connect to
                 _protocol='tcp',           # Connection protocol
                 _PUSH_PORT=32771,          # Port for Sending commands
                 _PULL_PORT=32772,          # Port for Receiving responses
                 _SUB_PORT=32773,           # Port for Subscribing for prices
                 _delimiter=';',
                 _pulldata_handlers=[],   # Handlers to process Data received through PULL port.
                 _subdata_handlers=[],    # Handlers to process Data received through SUB port.
                 _verbose=True,             # String delimiter
                 _poll_timeout=1000,        # ZMQ Poller Timeout (ms)
                 _sleep_delay=0.0001,        # 0.1 ms for time.sleep()
                 _monitor=False):           # Experimental ZeroMQ Socket Monitoring

        ######################################################################

        # Strategy Status (if this is False, ZeroMQ will not listen for Data)
        self._ACTIVE = True

        # Client ID
        self._ClientID = _ClientID

        # ZeroMQ Host
        self._host = _host

        # Connection Protocol
        self._protocol = _protocol

        # ZeroMQ Context
        self._ZMQ_CONTEXT = zmq.Context()

        # TCP Connection URL Template
        self._URL = self._protocol + "://" + self._host + ":"

        # Handlers for received Data (pull and sub ports)
        self._pulldata_handlers = _pulldata_handlers
        self._subdata_handlers = _subdata_handlers

        # Ports for PUSH, PULL and SUB sockets respectively
        self._PUSH_PORT = _PUSH_PORT
        self._PULL_PORT = _PULL_PORT
        self._SUB_PORT = _SUB_PORT

        # Create Sockets
        self._PUSH_SOCKET = self._ZMQ_CONTEXT.socket(zmq.PUSH)
        self._PUSH_SOCKET.setsockopt(zmq.SNDHWM, 1)
        self._PUSH_SOCKET_STATUS = {'state': True, 'latest_event': 'N/A'}

        self._PULL_SOCKET = self._ZMQ_CONTEXT.socket(zmq.PULL)
        self._PULL_SOCKET.setsockopt(zmq.RCVHWM, 1)
        self._PULL_SOCKET_STATUS = {'state': True, 'latest_event': 'N/A'}

        self._SUB_SOCKET = self._ZMQ_CONTEXT.socket(zmq.SUB)

        # Bind PUSH Socket to send commands to MetaTrader
        self._PUSH_SOCKET.connect(self._URL + str(self._PUSH_PORT))
        print("[INIT] Ready to send commands to METATRADER (PUSH): " + str(self._PUSH_PORT))

        # Connect PULL Socket to receive command responses from MetaTrader
        self._PULL_SOCKET.connect(self._URL + str(self._PULL_PORT))
        print("[INIT] Listening for responses from METATRADER (PULL): " + str(self._PULL_PORT))

        # Connect SUB Socket to receive market Data from MetaTrader
        print("[INIT] Listening for market Data from METATRADER (SUB): " + str(self._SUB_PORT))
        self._SUB_SOCKET.connect(self._URL + str(self._SUB_PORT))

        # Initialize POLL set and register PULL and SUB sockets
        self._poller = zmq.Poller()
        self._poller.register(self._PULL_SOCKET, zmq.POLLIN)
        self._poller.register(self._SUB_SOCKET, zmq.POLLIN)

        # Start listening for responses to commands and new market Data
        self._string_delimiter = _delimiter

        # BID/ASK Market Input Subscription Threads ({SYMBOL: Thread})
        self._MarketData_Thread = None

        # Socket Monitor Threads
        self._PUSH_Monitor_Thread = None
        self._PULL_Monitor_Thread = None

        # Market Input Dictionary by Symbol (holds tick Data)
        self._Market_Data_DB = {}   # {SYMBOL: {TIMESTAMP: (BID, ASK)}}

        # History Input Dictionary by Symbol (holds historic Data of the last HIST request for each symbol)
        self._History_DB = {}   # {SYMBOL_TF: [{'time': TIME, 'open': OPEN_PRICE, 'high': HIGH_PRICE,
                                #               'low': LOW_PRICE, 'close': CLOSE_PRICE, 'tick_volume': TICK_VOLUME,
                                #               'spread': SPREAD, 'real_volume': REAL_VOLUME}, ...]}

        # Thread returns the most recently received DATA block here
        self._thread_data_output = None

        # Verbosity
        self._verbose = _verbose

        # ZMQ Poller Timeout
        self._poll_timeout = _poll_timeout

        # Global Sleep Delay
        self._sleep_delay = _sleep_delay

        # Begin polling for PULL / SUB Data
        self._MarketData_Thread = Thread(target=self.poll_data,
                                         args=(self._string_delimiter,
                                               self._poll_timeout,))
        self._MarketData_Thread.daemon = True
        self._MarketData_Thread.start()

        self.spend_time = datetime.now() - datetime.now()
        self.sleep_time = datetime.now() - datetime.now()
        self.socket_time = datetime.now() - datetime.now()
        self.receive_time = datetime.now() - datetime.now()
        self.hnd_time = datetime.now() - datetime.now()

        ###########################################
        # Enable/Disable ZeroMQ Socket Monitoring #
        ###########################################
        if _monitor == True:

            # ZeroMQ Monitor Event Map
            self._MONITOR_EVENT_MAP = {}

            print("\n[KERNEL] Retrieving ZeroMQ Monitor Event Names:\n")

            for name in dir(zmq):
                if name.startswith('EVENT_'):
                    value = getattr(zmq, name)
                    print(f"{value}\t\t:\t{name}")
                    self._MONITOR_EVENT_MAP[value] = name

            print("\n[KERNEL] Socket Monitoring ChartConfig -> DONE!\n")

            # Disable PUSH/PULL sockets and let MONITOR events control them.
            self._PUSH_SOCKET_STATUS['state'] = False
            self._PULL_SOCKET_STATUS['state'] = False

            # PUSH
            self._PUSH_Monitor_Thread = Thread(target=self.event_monitor,
                                               args=("PUSH",
                                                     self._PUSH_SOCKET.get_monitor_socket(),))

            self._PUSH_Monitor_Thread.daemon = True
            self._PUSH_Monitor_Thread.start()

            # PULL
            self._PULL_Monitor_Thread = Thread(target=self.event_monitor,
                                               args=("PULL",
                                                     self._PULL_SOCKET.get_monitor_socket(),))

            self._PULL_Monitor_Thread.daemon = True
            self._PULL_Monitor_Thread.start()

    ##########################################################################

    def shutdown(self):

        # Set INACTIVE
        self._ACTIVE = False

        # Get all threads to shutdown
        if self._MarketData_Thread is not None:
            self._MarketData_Thread.join()

        if self._PUSH_Monitor_Thread is not None:
            self._PUSH_Monitor_Thread.join()

        if self._PULL_Monitor_Thread is not None:
            self._PULL_Monitor_Thread.join()

        # Unregister sockets from Poller
        self._poller.unregister(self._PULL_SOCKET)
        self._poller.unregister(self._SUB_SOCKET)
        print("\n++ [KERNEL] Sockets unregistered from ZMQ Poller()! ++")

        # Terminate context
        self._ZMQ_CONTEXT.destroy(0)
        print("\n++ [KERNEL] ZeroMQ Context Terminated.. shut down safely complete! :)")

    ##########################################################################

    """
    Set Status (to enable/disable strategy manually)
    """
    def _setStatus(self, _new_status=False):

        self._ACTIVE = _new_status
        print("\n**\n[KERNEL] Setting Status to {} - Deactivating Threads.. please wait a bit.\n**".format(_new_status))

    ##########################################################################

    """
    Function to send commands to MetaTrader (PUSH)
    """
    def remote_send(self, _socket, _data):

        if self._PUSH_SOCKET_STATUS['state'] == True:
            try:
                _socket.send_string(_data, zmq.DONTWAIT)
            except zmq.error.Again:
                print("\nResource timeout.. please try again.")
                sleep(self._sleep_delay)
        else:
            print('\n[KERNEL] NO HANDSHAKE ON PUSH SOCKET.. Cannot SEND Data')

    ##########################################################################

    def _get_response_(self):
        return self._thread_data_output

    ##########################################################################

    def _set_response_(self, _resp=None):
        self._thread_data_output = _resp

    ##########################################################################

    def _valid_response_(self, _input='zmq'):

        # Valid Data types
        _types = (dict, DataFrame)

        # If _input = 'zmq', assume self._zmq._thread_data_output
        if isinstance(_input, str) and _input == 'zmq':
            return isinstance(self._get_response_(), _types)
        else:
            return isinstance(_input, _types)

        # Default
        return False

    ##########################################################################

    """
    Function to retrieve Data from MetaTrader (PULL)
    """
    def remote_recv(self, _socket):

        if self._PULL_SOCKET_STATUS['state'] == True:
            try:
                msg = _socket.recv_string(zmq.DONTWAIT)
                return msg
            except zmq.error.Again:
                print("\nResource timeout.. please try again.")
                sleep(self._sleep_delay)
        else:
            print('\r[KERNEL] NO HANDSHAKE ON PULL SOCKET.. Cannot READ Data', end='', flush=True)

        return None

    ##########################################################################

    """
    Function to get current symbol
    """
    def get_symbol_request(self):
        _msg = "{}".format('GET_SYMBOL')

        self.remote_send(self._PUSH_SOCKET, _msg)

    """
        Function to get bars count
    """
    def get_bars_cnt_request(self):
        _msg = "{}".format('GET_BARS')

        self.remote_send(self._PUSH_SOCKET, _msg)

    """
            Function to get period of time_frame
    """
    def get_time_frame_request(self):
        _msg = "{}".format('GET_TIMEFRAME')

        self.remote_send(self._PUSH_SOCKET, _msg)

    """
    Function to construct messages for sending HIST commands to MetaTrader
    """
    def send_hist_request(self,
                                 _symbol='EURUSD',
                                 _timeframe=1440,
                                 _count = 1):
                                 #_end='2019.01.04 17:05:00'):

        _msg = "{};{};{};{}".format('HIST',
                                     _symbol,
                                     _timeframe,
                                     _count)

        # Send via PUSH Socket
        self.remote_send(self._PUSH_SOCKET, _msg)

    """
    Function to construct messages for sending DRAW commands to MetaTrader
    """
    def send_draw_request(self, params):
        _msg = "{};".format('DRAW')
        _msg += params

        self.remote_send(self._PUSH_SOCKET, _msg)

    """
        Function to Clear Chart
    """

    def send_clear_request(self):
        _msg = "{}".format('CLEAR')

        self.remote_send(self._PUSH_SOCKET, _msg)

    """
        Function to Delete Objects
    """

    def send_delete_request(self, params):
        _msg = "{};".format('DELETE')
        _msg += params

        self.remote_send(self._PUSH_SOCKET, _msg)

    ##########################################################################
    """
    Function to construct messages for sending TRACK_PRICES commands to 
    MetaTrader for real-time price updates
    """

    def send_track_price_request(self, _symbols=['EURUSD']):
        _msg = 'TRACK_PRICES'
        for s in _symbols:
            _msg = _msg + ";{}".format(s)

        # Send via PUSH Socket
        self.remote_send(self._PUSH_SOCKET, _msg)

    ##########################################################################
    """
    Function to construct messages for sending TRACK_RATES commands to 
    MetaTrader for OHLC
    """

    def send_track_rates_request(self, _instruments=[('EURUSD_M1', 'EURUSD', 1)]):
        _msg = 'TRACK_RATES'
        for i in _instruments:
            _msg = _msg + ";{};{}".format(i[1], i[2])

        # Send via PUSH Socket
        self.remote_send(self._PUSH_SOCKET, _msg)

    ##########################################################################

    """
    Function to check Poller for new reponses (PULL) and market Data (SUB)
    """

    def poll_data(self,
                           string_delimiter=';',
                           poll_timeout=1000):

        sleep(0.01)

        while self._ACTIVE:

            start_time = datetime.now()
            sockets = dict(self._poller.poll(poll_timeout))
            self.socket_time += datetime.now() - start_time

            # Process response to commands sent to MetaTrader
            if self._PULL_SOCKET in sockets and sockets[self._PULL_SOCKET] == zmq.POLLIN:

                if self._PULL_SOCKET_STATUS['state'] == True:

                        # msg = self._PULL_SOCKET.recv_string(zmq.DONTWAIT)
                        msg = self.remote_recv(self._PULL_SOCKET)

                        # If Data is returned, store as pandas Series
                        if msg != '' and msg != None:
                            # try:
                            _data = eval(msg)
                            if '_action' in _data and _data['_action'] == 'HIST':
                                _symbol = _data['_symbol']
                                if '_data' in _data.keys():
                                    if _symbol not in self._History_DB.keys():
                                        self._History_DB[_symbol] = {}
                                    self._History_DB[_symbol] = _data['_data']
                                else:
                                    print('No Data found. MT4 often needs multiple requests when accessing Data of symbols without open charts.')
                                    print('message: ' + msg)

                            # invokes Data handlers on pull port
                            for hnd in self._pulldata_handlers:
                                hnd.on_pull_data(_data)

                            self._thread_data_output = _data
                            if self._verbose:
                                print(_data)  # default logic

                            # except Exception as ex:
                            #     _exstr = "Exception Type {0}. Args:\n{1!r}"
                            #     _msg = _exstr.format(type(ex).__name__, ex.args)
                            #     print(_msg)

                else:
                    print('\r[KERNEL] NO HANDSHAKE on PULL SOCKET.. Cannot READ Data.', end='', flush=True)

            # Receive new market Data from MetaTrader
            if self._SUB_SOCKET in sockets and sockets[self._SUB_SOCKET] == zmq.POLLIN:

                try:
                    receive_start_time = datetime.now()
                    msg = self._SUB_SOCKET.recv_string(zmq.DONTWAIT)

                    if msg != "":

                        # _timestamp = str(Timestamp.now('UTC'))[:-6]
                        # _symbol, _data = msg.split("&")
                        # if len(_data.split(string_delimiter)) == 3:
                        #     _time, _bid, _ask = _data.split(string_delimiter)
                        #
                        #     if self._verbose:
                        #         print("\n[" + _symbol + "] " + _timestamp + " (" + _bid + "/" + _ask + ") BID/ASK")
                        #
                        #     # Update Market Input DB
                        #     if _symbol not in self._Market_Data_DB.keys():
                        #         self._Market_Data_DB[_symbol] = {}
                        #
                        #     self._Market_Data_DB[_symbol][_timestamp] = (float(_bid), float(_ask))
                        #
                        # elif len(_data.split(string_delimiter)) == 8:
                        #     _time, _open, _high, _low, _close, _tick_vol, _spread, _real_vol = _data.split(string_delimiter)
                        #     if self._verbose:
                        #         print("\n[" + _symbol + "] " + _timestamp + " (" + _time + "/" + _open + "/" + _high + "/" + _low + "/" + _close + "/" + _tick_vol + "/" + _spread + "/" + _real_vol + ") TIME/OPEN/HIGH/LOW/CLOSE/TICKVOL/SPREAD/VOLUME")
                        #     # Update Market Rate DB
                        #     if _symbol not in self._Market_Data_DB.keys():
                        #         self._Market_Data_DB[_symbol] = {}
                        #     self._Market_Data_DB[_symbol][_timestamp] = (int(_time), float(_open), float(_high), float(_low), float(_close), int(_tick_vol), int(_spread), int(_real_vol))
                        self.receive_time += datetime.now() - receive_start_time

                        # invokes Data handlers on sub port
                        hnd_t = datetime.now()
                        for hnd in self._subdata_handlers:
                            hnd.on_sub_data(msg)
                        self.hnd_time += datetime.now() - hnd_t

                except zmq.error.Again:
                    pass # resource temporarily unavailable, nothing to print
                except ValueError:
                    pass # No Data returned, passing iteration.
                except UnboundLocalError:
                    pass # _symbol may sometimes get referenced before being assigned.

            self.spend_time += datetime.now() - start_time

        print("\n++ [KERNEL] _DWX_ZMQ_Poll_Data_() Signing Out ++")

    ##########################################################################

    """
        Function to subscribe to given Symbol's BID/ASK feed from MetaTrader
    """

    def subscribe_market_data(self, _symbol='EURUSD', string_delimiter=';'):

        # Subscribe to SYMBOL first.
        self._SUB_SOCKET.setsockopt_string(zmq.SUBSCRIBE, _symbol)

        print("[KERNEL] Subscribed to {} BID/ASK updates. See self._Market_Data_DB.".format(_symbol))

    """
    Function to unsubscribe to given Symbol's BID/ASK feed from MetaTrader
    """

    def unsubscribe_market_data(self, _symbol):

        self._SUB_SOCKET.setsockopt_string(zmq.UNSUBSCRIBE, _symbol)
        print("\n**\n[KERNEL] Unsubscribing from " + _symbol + "\n**\n")

    """
    Function to unsubscribe from ALL MetaTrader Symbols
    """

    def unsubscribe_all_market_data_request(self):

        # 31-07-2019 12:22 CEST
        for _symbol in self._Market_Data_DB.keys():
            self.unsubscribe_market_data(_symbol=_symbol)

    def event_monitor(self,
                                socket_name,
                                monitor_socket):

        # 05-08-2019 11:21 CEST
        while self._ACTIVE:

            sleep(self._sleep_delay) # poll timeout is in ms, sleep() is s.

            # while monitor_socket.poll():
            while monitor_socket.poll(self._poll_timeout):

                try:
                    evt = recv_monitor_message(monitor_socket, zmq.DONTWAIT)
                    evt.update({'description': self._MONITOR_EVENT_MAP[evt['event']]})

                    # print(f"\r[{socket_name} Socket] >> {evt['description']}", end='', flush=True)
                    print(f"\n[{socket_name} Socket] >> {evt['description']}")

                    # Set socket status on HANDSHAKE
                    if evt['event'] == 4096:        # EVENT_HANDSHAKE_SUCCEEDED

                        if socket_name == "PUSH":
                            self._PUSH_SOCKET_STATUS['state'] = True
                            self._PUSH_SOCKET_STATUS['latest_event'] = 'EVENT_HANDSHAKE_SUCCEEDED'

                        elif socket_name == "PULL":
                            self._PULL_SOCKET_STATUS['state'] = True
                            self._PULL_SOCKET_STATUS['latest_event'] = 'EVENT_HANDSHAKE_SUCCEEDED'

                        # print(f"\n[{socket_name} Socket] >> ..ready for action!\n")

                    else:
                        # Update 'latest_event'
                        if socket_name == "PUSH":
                            self._PUSH_SOCKET_STATUS['state'] = False
                            self._PUSH_SOCKET_STATUS['latest_event'] = evt['description']

                        elif socket_name == "PULL":
                            self._PULL_SOCKET_STATUS['state'] = False
                            self._PULL_SOCKET_STATUS['latest_event'] = evt['description']

                    if evt['event'] == zmq.EVENT_MONITOR_STOPPED:

                        # Reinitialize the socket
                        if socket_name == "PUSH":
                            monitor_socket = self._PUSH_SOCKET.get_monitor_socket()
                        elif socket_name == "PULL":
                            monitor_socket = self._PULL_SOCKET.get_monitor_socket()

                except Exception as ex:
                    _exstr = "Exception Type {0}. Args:\n{1!r}"
                    _msg = _exstr.format(type(ex).__name__, ex.args)
                    print(_msg)

        # Close Monitor Socket
        monitor_socket.close()

        print(f"\n++ [KERNEL] {socket_name} _DWX_ZMQ_EVENT_MONITOR_() Signing Out ++")

