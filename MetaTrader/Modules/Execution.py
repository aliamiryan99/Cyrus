
from pandas import to_datetime
from time import sleep
from MetaTrader.Api.CyrusMetaConnector import CyrusMetaConnector


class Execution:
    
    def __init__(self, zmq:CyrusMetaConnector):
        self.zmq = zmq
    
    ##########################################################################
    
    def trade_execute(self, exec_dict, verbose=False,  delay=0.01, w_break=100):
        
        check = ''
        
        # Reset thread Data output
        self.zmq.set_response(None)
        
        # OPEN TRADE
        if exec_dict['_action'] == 'OPEN':
            
            check = '_action'
            self.zmq.new_trade(order=exec_dict)
            
        # CLOSE TRADE
        elif exec_dict['_action'] == 'CLOSE':
            
            check = '_response_value'
            self.zmq.close_by_ticket(exec_dict['_ticket'])

        # MODIFY TRADE
        elif exec_dict['_action'] == 'MODIFY':
            self.zmq.modify_by_ticket(exec_dict['_ticket'], exec_dict['_SL'], exec_dict['_TP'])
            
        if verbose:
            print('\n[{}] {} -> MetaTrader'.format(exec_dict['_comment'],
                                                   str(exec_dict)))
            
        # While loop start time reference            
        ws = to_datetime('now')
        
        # While Data not received, sleep until timeout
        while self.zmq.get_response() is None:
            sleep(delay)
            
            if (to_datetime('now') - ws).total_seconds() > (delay * w_break):
                break
        
        # If Data received, return DataFrame
        if self.zmq.get_response() is not None:

            response = self.zmq.get_response()
            if check in response.keys():
                return response

    def draw_execute(self, params, delay=0.01, w_break=10, type="DRAW"):
        check = ''

        self.zmq.set_response(None)

        # Draw
        if type == "DRAW":
            self.zmq.send_draw_request(params)
        elif type == "DELETE":
            self.zmq.send_delete_request(params)

        ws = to_datetime('now')

        # While Data not received, sleep until timeout
        while self.zmq.get_response() is None:
            sleep(delay)

            if (to_datetime('now') - ws).total_seconds() > (delay * w_break):
                break

        # If Data received, return DataFrame
        if self.zmq.get_response() is not None:

            response = self.zmq.get_response()
            if check in response.keys():
                return response
