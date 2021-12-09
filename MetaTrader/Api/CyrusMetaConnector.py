
import zmq
from time import sleep
from pandas import DataFrame
from threading import Thread
from datetime import datetime
from datetime import timedelta


class CyrusMetaConnector:

    def __init__(self,
                 client_id='CyrusMetaConnector',  # Unique ID for this client
                 host='localhost',  # Host to connect to
                 protocol='tcp',  # Connection protocol
                 push_port=32768,  # Port for Sending commands
                 pull_port=32769,  # Port for Receiving responses
                 sub_port=32770,  # Port for Subscribing for prices
                 _delimiter=';',
                 pull_data_handlers=None,  # Handlers to process Data received through PULL port.
                 sub_data_handlers=None,  # Handlers to process Data received through SUB port.
                 verbose=True,  # String delimiter
                 poll_timeout=10000,  # ZMQ Poller Timeout (ms)
                 sleep_delay=0.01,  # 1 ms for time.sleep()
                 _monitor=False):  # Experimental ZeroMQ Socket Monitoring

        ######################################################################

        # Strategy Status (if this is False, ZeroMQ will not listen for Data)
        if pull_data_handlers is None:
            pull_data_handlers = []
        self.active = True
        # Client ID
        self.client_id = client_id
        # ZeroMQ Host
        self.host = host
        # Connection Protocol
        self.protocol = protocol
        # ZeroMQ Context
        self.zmq_context = zmq.Context()
        # TCP Connection URL Template
        self.url = self.protocol + "://" + self.host + ":"
        # Handlers for received Data (pull and sub ports)
        self.pull_data_handlers = pull_data_handlers
        self.sub_data_handlers = sub_data_handlers
        # Ports for PUSH, PULL and SUB sockets respectively
        self.push_port = push_port
        self.pull_port = pull_port
        self.sub_port = sub_port
        # Create Sockets
        self.push_socket = self.zmq_context.socket(zmq.PUSH)
        self.push_socket.setsockopt(zmq.SNDHWM, 1)
        self.push_socket_status = {'state': True, 'latest_event': 'N/A'}

        self.pull_socket = self.zmq_context.socket(zmq.PULL)
        self.pull_socket.setsockopt(zmq.RCVHWM, 1)
        self.pull_socket_status = {'state': True, 'latest_event': 'N/A'}

        self.sub_socket = self.zmq_context.socket(zmq.SUB)
        # Bind PUSH Socket to send commands to MetaTrader
        self.push_socket.connect(self.url + str(self.push_port))
        print("[INIT] Ready to send commands to METATRADER (PUSH): " + str(self.push_port))
        # Connect PULL Socket to receive command responses from MetaTrader
        self.pull_socket.connect(self.url + str(self.pull_port))
        print("[INIT] Listening for responses from METATRADER (PULL): " + str(self.pull_port))
        # Connect SUB Socket to receive market Data from MetaTrader
        print("[INIT] Listening for market Data from METATRADER (SUB): " + str(self.sub_port))
        self.sub_socket.connect(self.url + str(self.sub_port))
        # Initialize POLL set and register PULL and SUB sockets
        self.poller = zmq.Poller()
        self.poller.register(self.pull_socket, zmq.POLLIN)
        self.poller.register(self.sub_socket, zmq.POLLIN)
        # Start listening for responses to commands and new market Data
        self.string_delimiter = _delimiter
        # BID/ASK Market Input Subscription Threads ({SYMBOL: Thread})
        self.market_data_thread = None
        # Market Input Dictionary by Symbol (holds tick Data)
        self.market_data_db = {}  # {SYMBOL: {TIMESTAMP: (BID, ASK)}}
        # History Input Dictionary by Symbol (holds historic Data of the last HIST request for each symbol)
        self.history_db = {}  # {SYMBOL_TF: [{'time': TIME, 'open': OPEN_PRICE, 'high': HIGH_PRICE,
        #               'low': LOW_PRICE, 'close': CLOSE_PRICE, 'tick_volume': TICK_VOLUME,
        #               'spread': SPREAD, 'real_volume': REAL_VOLUME}, ...]}
        # Temporary Order STRUCT for convenience wrappers later.
        self.temp_order_dict = self.generate_default_order_dict()
        # Thread returns the most recently received DATA block here
        self.thread_data_output = None
        # Verbosity
        self.verbose = verbose
        # ZMQ Poller Timeout
        self.poll_timeout = poll_timeout
        # Global Sleep Delay
        self.sleep_delay = sleep_delay
        # Begin polling for PULL / SUB Data
        self.market_data_thread = Thread(target=self.poll_data,
                                         args=(self.string_delimiter,
                                               self.poll_timeout,))
        self.market_data_thread.daemon = True
        self.market_data_thread.start()

        self.spend_time = datetime.now() - datetime.now()
        self.sleep_time = datetime.now() - datetime.now()
        self.socket_time = datetime.now() - datetime.now()
        self.receive_time = datetime.now() - datetime.now()
        self.hnd_time = datetime.now() - datetime.now()

        self.wait_time = datetime.now() - datetime.now()

    def shutdown(self):

        # Set INACTIVE
        self.active = False

        # Get all threads to shutdown
        if self.market_data_thread is not None:
            self.market_data_thread.join()

        # Unregister sockets from Poller
        self.poller.unregister(self.pull_socket)
        self.poller.unregister(self.sub_socket)
        print("\n++ [KERNEL] Sockets unregistered from ZMQ Poller()! ++")

        # Terminate context
        self.zmq_context.destroy(0)
        print("\n++ [KERNEL] ZeroMQ Context Terminated.. shut down safely complete! :)")

    """
    Set Status (to enable/disable strategy manually)
    """
    def set_status(self, _new_status=False):

        self.active = _new_status
        print("\n**\n[KERNEL] Setting Status to {} - Deactivating Threads.. please wait a bit.\n**".format(_new_status))

    """
    Function to send commands to MetaTrader (PUSH)
    """
    def remote_send(self, _socket, _data):

        if self.push_socket_status['state'] == True:
            try:
                _socket.send_string(_data, zmq.DONTWAIT)
            except zmq.error.Again:
                print(f"Push data timeout , data : {_data}")
                sleep(self.sleep_delay)
        else:
            print('\n[KERNEL] NO HANDSHAKE ON PUSH SOCKET.. Cannot SEND Data')

    def get_response(self):
        return self.thread_data_output

    def set_response(self, resp=None):
        self.thread_data_output = resp

    def valid_response(self, input='zmq'):
        # Valid Data types
        _types = (dict, DataFrame)

        # If _input = 'zmq', assume self._zmq.thread_data_output
        if isinstance(input, str) and input == 'zmq':
            return isinstance(self.get_response(), _types)
        else:
            return isinstance(input, _types)

    """
    Function to retrieve Data from MetaTrader (PULL)
    """
    def remote_recv(self, _socket):
        if self.pull_socket_status['state'] == True:
            try:
                msg = _socket.recv_string(zmq.DONTWAIT)
                return msg
            except zmq.error.Again:
                print("\nResource timeout.. please try again.")
                sleep(self.sleep_delay)
        else:
            print('\r[KERNEL] NO HANDSHAKE ON PULL SOCKET.. Cannot READ Data', end='', flush=True)

        return None

    def send_tick_received(self):
        msg = "{}".format('TICK_RECEIVED')

        self.remote_send(self.push_socket, msg)

    def get_symbol_request(self):
        msg = "{}".format('GET_SYMBOL')

        self.remote_send(self.push_socket, msg)

    def get_bars_cnt_request(self):
        msg = "{}".format('GET_BARS')

        self.remote_send(self.push_socket, msg)

    def get_time_frame_request(self):
        msg = "{}".format('GET_TIMEFRAME')

        self.remote_send(self.push_socket, msg)

    def send_draw_request(self, params):
        msg = "{};".format('DRAW')
        msg += params

        self.remote_send(self.push_socket, msg)

    def send_clear_request(self):
        msg = "{}".format('CLEAR')

        self.remote_send(self.push_socket, msg)

    def send_delete_request(self, params):
        msg = "{};".format('DELETE')
        msg += params

        self.remote_send(self.push_socket, msg)

    def new_trade(self, order=None):
        if order is None:
            order = self.generate_default_order_dict()

        # Execute
        self.send_command(**order)

    # _SL and _TP given in points. _price is only used for pending orders.
    def modify_by_ticket(self, ticket, sl, tp, price=0):

        try:
            self.temp_order_dict['_action'] = 'MODIFY'
            self.temp_order_dict['_ticket'] = ticket
            self.temp_order_dict['_SL'] = sl
            self.temp_order_dict['_TP'] = tp
            self.temp_order_dict['_price'] = price

            # Execute
            self.send_command(**self.temp_order_dict)

        except KeyError:
            print("[ERROR] Order Ticket {} not found!".format(ticket))

    def close_by_ticket(self, ticket):

        try:
            self.temp_order_dict['_action'] = 'CLOSE'
            self.temp_order_dict['_ticket'] = ticket

            self.send_command(**self.temp_order_dict)

        except KeyError:
            print("[ERROR] Order Ticket {} not found!".format(ticket))

    def close_partial_by_ticket(self, ticket, lots):

        try:
            self.temp_order_dict['_action'] = 'CLOSE_PARTIAL'
            self.temp_order_dict['_ticket'] = ticket
            self.temp_order_dict['_lots'] = lots

            self.send_command(**self.temp_order_dict)

        except KeyError:
            print("[ERROR] Order Ticket {} not found!".format(ticket))

    def close_trades_by_magic(self, magic):

        try:
            self.temp_order_dict['_action'] = 'CLOSE_MAGIC'
            self.temp_order_dict['_magic'] = magic

            # Execute
            self.send_command(**self.temp_order_dict)

        except KeyError:
            pass

    # CLOSE ALL TRADES
    def close_all_trades(self):

        try:
            self.temp_order_dict['_action'] = 'CLOSE_ALL'

            # Execute
            self.send_command(**self.temp_order_dict)

        except KeyError:
            pass

    # GET OPEN TRADES
    def get_all_open_trades(self):

        try:
            self.temp_order_dict['_action'] = 'GET_OPEN_TRADES'

            # Execute
            self.send_command(**self.temp_order_dict)

        except KeyError:
            pass

    # DEFAULT ORDER DICT
    def generate_default_order_dict(self):
        return ({'_action': 'OPEN',
                 '_type': 0,
                 '_symbol': 'EURUSD',
                 '_price': 0.0,
                 '_SL': 500,  # sl/tp in POINTS, not pips.
                 '_TP': 500,
                 '_comment': self.client_id,
                 '_lots': 0.01,
                 '_magic': 123456,
                 '_ticket': 0})

    # Take Screen Shoot
    def take_screen_shot(self, name, symbol):
        msg = "{};{};{}".format('TAKE_SCREEN_SHOOT', symbol, name)

        self.remote_send(self.push_socket, msg)

    """
    Function to construct messages for sending HIST commands to MetaTrader
    Because of broker GMT offset _end time might have to be modified.
    """

    def send_hist_request(self, symbol, timeframe, count):
        msg = "{};{};{};{}".format('HIST', symbol, timeframe, count)

        self.remote_send(self.push_socket, msg)

    def send_balance_request(self):
        msg = "{}".format('GET_BALANCE')

        self.remote_send(self.push_socket, msg)

    def send_equity_request(self):
        msg = "{}".format('GET_EQUITY')

        self.remote_send(self.push_socket, msg)

    def set_scale_request(self, symbol, scale):
        msg = "{};{};{}".format('SET_SCALE', symbol, scale)

        self.remote_send(self.push_socket, msg)

    def set_speed_request(self, speed):
        msg = "{};{}".format("SET_SPEED", speed)

        self.remote_send(self.push_socket, msg)
    """
    Function to construct messages for sending TRACK_PRICES commands to 
    MetaTrader for real-time price updates
    """

    def send_track_price_request(self, symbols):
        msg = 'TRACK_PRICES'
        for s in symbols:
            msg = msg + ";{}".format(s)

        self.remote_send(self.push_socket, msg)
    
    """
    Function to construct messages for sending TRACK_RATES commands to 
    MetaTrader for OHLC
    """

    def send_track_rates_request(self, _instruments):  # [('EURUSD_M1', 'EURUSD', 1)]
        msg = 'TRACK_RATES'
        for i in _instruments:
            msg = msg + ";{};{}".format(i[1], i[2])

        self.remote_send(self.push_socket, msg)
    
    """
    Function to construct messages for sending Trade commands to MetaTrader
    """

    def send_command(self, _action='OPEN', _type=0, _symbol='EURUSD', _price=0.0, _SL=50, _TP=50,
                     _comment="Python-to-MT", _lots=0.01, _magic=123456, _ticket=0):

        msg = "{};{};{};{};{};{};{};{};{};{};{}".format('TRADE', _action, _type, _symbol, _price,
                                                         _SL, _TP, _comment, _lots, _magic, _ticket)

        self.remote_send(self.push_socket, msg)

    """
    Function to check Poller for new reponses (PULL) and market Data (SUB)
    """

    def poll_data(self, string_delimiter=';', poll_timeout=1000):
        sleep(self.sleep_delay)

        while self.active:

            start_time = datetime.now()
            sockets = dict(self.poller.poll(poll_timeout))
            self.socket_time += datetime.now() - start_time

            # Process response to commands sent to MetaTrader
            if self.pull_socket in sockets and sockets[self.pull_socket] == zmq.POLLIN:

                if self.pull_socket_status['state'] == True:

                    # msg = self.pull_socket.recv_string(zmq.DONTWAIT)
                    msg = self.remote_recv(self.pull_socket)

                    # If Data is returned, store as pandas Series
                    if msg != '' and msg is not None:
                        # try:
                        _data = eval(msg)
                        if '_action' in _data and _data['_action'] == 'HIST':
                            _symbol = _data['_symbol']
                            if '_data' in _data.keys():
                                if _symbol not in self.history_db.keys():
                                    self.history_db[_symbol] = {}
                                self.history_db[_symbol] = _data['_data']
                            else:
                                print(
                                    'No Data found. MT4 often needs multiple requests when accessing Data of symbols without open charts.')
                                print('message: ' + msg)

                        # invokes Data handlers on pull port
                        for hnd in self.pull_data_handlers:
                            hnd.on_pull_data(_data)

                        self.thread_data_output = _data
                        if self.verbose:
                            print(_data)  # default logic

                else:
                    print('\r[KERNEL] NO HANDSHAKE on PULL SOCKET.. Cannot READ Data.', end='', flush=True)

            # Receive new market Data from MetaTrader
            if self.sub_socket in sockets and sockets[self.sub_socket] == zmq.POLLIN:

                try:
                    receive_start_time = datetime.now()
                    msg = self.sub_socket.recv_string(zmq.DONTWAIT)

                    if msg != "":

                        self.receive_time += datetime.now() - receive_start_time

                        # invokes Data handlers on sub port
                        hnd_t = datetime.now()
                        for hnd in self.sub_data_handlers:
                            hnd.on_sub_data(msg)
                        self.hnd_time += datetime.now() - hnd_t
                        self.wait_time = datetime.now() - datetime.now()

                except zmq.error.Again:
                    pass  # resource temporarily unavailable, nothing to print

            self.spend_time += datetime.now() - start_time
            self.wait_time += datetime.now() - start_time

        print("\n++ [KERNEL] poll_data() Signing Out ++")

    """
    Function to subscribe to given Symbol's BID/ASK feed from MetaTrader
    """
    def subscribe_market_data(self, symbol, string_delimiter=';'):
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, symbol)

        print("[KERNEL] Subscribed to {} BID/ASK updates. See self.market_data_db.".format(symbol))

    """
    Function to unsubscribe to given Symbol's BID/ASK feed from MetaTrader
    """
    def unsubscribe_market_data(self, symbol):
        self.sub_socket.setsockopt_string(zmq.UNSUBSCRIBE, symbol)
        print("\n**\n[KERNEL] Unsubscribing from " + symbol + "\n**\n")

    """
    Function to unsubscribe from ALL MetaTrader Symbols
    """
    def unsubscribe_all_market_data_request(self):
        for symbol in self.market_data_db.keys():
            self.unsubscribe_market_data(symbol=symbol)
