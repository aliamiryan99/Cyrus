from pandas import DataFrame, to_datetime
from time import sleep
from MetaTrader.Api.CyrusMetaConnector import CyrusMetaConnector


class Reporting:

    def __init__(self, zmq: CyrusMetaConnector):
        self.zmq = zmq

    def get_open_trades(self, delay=0.01, w_break=10):
        # Reset Data output
        self.zmq.set_response(None)

        # Get open trades from MetaTrader
        self.zmq.get_all_open_trades()

        # While loop start time reference
        _ws = to_datetime('now')

        # While Data not received, sleep until timeout
        while self.zmq.get_response() is None:
            sleep(delay)
            if (to_datetime('now') - _ws).total_seconds() > (delay * w_break):
                break

        # If Data received, return DataFrame
        if self.zmq.get_response() is None:
            response = self.zmq.get_response()

            if ('_trades' in response.keys()
                    and len(response['_trades']) > 0):
                _df = DataFrame(data=response['_trades'].values())
                _df['ticket'] = response['_trades'].keys()
                return _df

    def get_balance(self, delay=0.01, w_break=100):
        # Reset Data output
        self.zmq.set_response(None)

        # Get open trades from MetaTrader
        self.zmq.send_balance_request()

        # While loop start time reference
        _ws = to_datetime('now')

        # While Data not received, sleep until timeout
        while self.zmq.get_response() is None:
            sleep(delay)
            if (to_datetime('now') - _ws).total_seconds() > (delay * w_break):
                break

        # If Data received, return DataFrame
        if self.zmq.get_response() is not None:

            response = self.zmq.get_response()

            if '_balance' in response.keys():
                return list(response['_balance'])[0]

        # Default
        return 0

    def get_equity(self, delay=0.01, w_break=10):
        # Reset Data output
        self.zmq.set_response(None)

        # Get open trades from MetaTrader
        self.zmq.send_equity_request()

        # While loop start time reference
        _ws = to_datetime('now')

        # While Data not received, sleep until timeout
        while self.zmq.get_response() is None:
            sleep(delay)

            if (to_datetime('now') - _ws).total_seconds() > (delay * w_break):
                break

        # If Data received, return DataFrame
        if self.zmq.get_response() is not None:
            response = self.zmq.get_response()

            if '_equity' in response.keys():
                return list(response['_equity'])[0]

        # Default
        return 0

    def get_curr_symbol(self, delay=0.1, w_break=20):
        # Reset Data output
        self.zmq.set_response(None)

        # Get Symbol
        self.zmq.get_symbol_request()

        # While loop start time reference
        _ws = to_datetime('now')

        # While Data not received, sleep until timeout
        while self.zmq.get_response() is None:

            sleep(delay)

            if (to_datetime('now') - _ws).total_seconds() > (delay * w_break):
                break

        # If Data received, return symbol
        if self.zmq.get_response() is not None:

            response = self.zmq.get_response()

            if '_symbol' in response.keys():
                return response['_symbol']

        # Default
        return 0

    def get_bars_cnt(self, delay=0.1, w_break=20):
        # Reset Data output
        self.zmq.set_response(None)

        # Get Symbol
        self.zmq.get_bars_cnt_request()

        # While loop start time reference
        _ws = to_datetime('now')

        # While Data not received, sleep until timeout
        while self.zmq.get_response() is None:

            sleep(delay)

            if (to_datetime('now') - _ws).total_seconds() > (delay * w_break):
                break

        # If Data received, return symbol
        if self.zmq.get_response() is not None:

            response = self.zmq.get_response()

            if '_bars' in response.keys():
                return response['_bars']

        # Default
        return 0

    def get_period(self, delay=0.1, w_break=20):
        # Reset Data output
        self.zmq.set_response(None)

        # Get Symbol
        self.zmq.get_time_frame_request()

        # While loop start time reference
        _ws = to_datetime('now')

        # While Data not received, sleep until timeout
        while self.zmq.get_response() is None:

            sleep(delay)

            if (to_datetime('now') - _ws).total_seconds() > (delay * w_break):
                break

        # If Data received, return symbol
        if self.zmq.get_response() is not None:

            response = self.zmq.get_response()

            if '_period' in response.keys():
                return response['_period']

        # Default
        return 0
