

from pandas import to_datetime
from time import sleep


class Execution:

    def __init__(self, _zmq):
        self._zmq = _zmq

    ##########################################################################

    def execute(self,
                  draw_param,
                  _delay=0.1,
                  _wbreak=40):

        _check = ''

        # Reset thread Data output
        self._zmq._set_response_(None)

        # Draw
        self._zmq.send_draw_request(draw_param)

        # While loop start time reference
        _ws = to_datetime('now')

        # While Data not received, sleep until timeout
        while self._zmq._valid_response_('zmq') == False:
            sleep(_delay)

            if (to_datetime('now') - _ws).total_seconds() > (_delay * _wbreak):
                break

        # If Data received, return DataFrame
        if self._zmq._valid_response_('zmq'):

            response = self._zmq._get_response_()
            if _check in response.keys():
                return response

        # Default
        return None

    ##########################################################################
