
from pandas import to_datetime
from time import sleep
from MetaTrader.Api.CyrusMetaConnector import CyrusMetaConnector


class Execution:
    
    def __init__(self, connector:CyrusMetaConnector):
        self.connector = connector
    
    ##########################################################################
    
    def trade_execute(self, exec_dict, verbose=False,  delay=0.01, w_break=100):
        
        check = ''
        
        # Reset thread Data output
        self.connector.set_response(None)
        
        # OPEN TRADE
        if exec_dict['_action'] == 'OPEN':
            
            check = '_action'
            self.connector.new_trade(order=exec_dict)
            
        # CLOSE TRADE
        elif exec_dict['_action'] == 'CLOSE':
            
            check = '_response_value'
            self.connector.close_by_ticket(exec_dict['_ticket'])

        # MODIFY TRADE
        elif exec_dict['_action'] == 'MODIFY':
            self.connector.modify_by_ticket(exec_dict['_ticket'], exec_dict['_SL'], exec_dict['_TP'])
            
        if verbose:
            print('\n[{}] {} -> MetaTrader'.format(exec_dict['_comment'],
                                                   str(exec_dict)))
            
        # While loop start time reference            
        ws = to_datetime('now')
        
        # While Data not received, sleep until timeout
        while self.connector.get_response() is None:
            sleep(delay)
            
            if (to_datetime('now') - ws).total_seconds() > (delay * w_break):
                break
        
        # If Data received, return DataFrame
        if self.connector.get_response() is not None:

            response = self.connector.get_response()
            if check in response.keys():
                return response

    def draw_execute(self, params, delay=0.01, w_break=10, type="DRAW"):
        check = ''

        self.connector.set_response(None)

        # Draw
        if type == "DRAW":
            self.connector.send_draw_request(params)
        elif type == "DELETE":
            self.connector.send_delete_request(params)

        ws = to_datetime('now')

        # While Data not received, sleep until timeout
        while self.connector.get_response() is None:
            sleep(delay)

            if (to_datetime('now') - ws).total_seconds() > (delay * w_break):
                break

        # If Data received, return DataFrame
        if self.connector.get_response() is not None:

            response = self.connector.get_response()
            if check in response.keys():
                return response

    def screenshot_execute(self,  name, symbol, delay=0.01, w_break=200):
        check = ''

        self.connector.set_response(None)

        self.connector.take_screen_shot(name, symbol)

        ws = to_datetime('now')
        # While Data not received, sleep until timeout
        while self.connector.get_response() is None:
            sleep(delay)

            if (to_datetime('now') - ws).total_seconds() > (delay * w_break):
                break

        # If Data received, return DataFrame
        if self.connector.get_response() is not None:

            response = self.connector.get_response()
            if check in response.keys():
                return response

    def set_settings_execute(self, symbol, value, type, delay=0.01, w_break=20):
        check = ''

        self.connector.set_response(None)
        
        if type == "Scale":
            self.connector.set_scale_request(symbol, value)
        elif type == "Speed":
            self.connector.set_speed_request(value)
        elif type == "CandleDelay":
            self.connector.set_start_candle_delay_request(value)

        ws = to_datetime('now')
        # While Data not received, sleep until timeout
        while self.connector.get_response() is None:
            sleep(delay)

            if (to_datetime('now') - ws).total_seconds() > (delay * w_break):
                break

        # If Data received, return DataFrame
        if self.connector.get_response() is not None:

            response = self.connector.get_response()
            if check in response.keys():
                return response