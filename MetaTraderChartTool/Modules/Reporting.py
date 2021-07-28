# -*- coding: utf-8 -*-
"""
    MQTT_Reporting.py
    --
    @author: Darwinex Labs (www.darwinex.com)

    Copyright (c) 2019 onwards, Darwinex. All rights reserved.

    Licensed under the BSD 3-Clause License, you may not use this file except
    in compliance with the License.

    You may obtain a copy of the License at:
    https://opensource.org/licenses/BSD-3-Clause
"""

from pandas import DataFrame, to_datetime
from time import sleep


class Reporting:

    def __init__(self, _zmq):
        self._zmq = _zmq

    ##########################################################################

    def get_curr_symbol(self, _delay=0.1, _wbreak=10):
        # Reset Data output
        self._zmq._set_response_(None)

        # Get Symbol
        self._zmq.get_symbol_request()

        # While loop start time reference
        _ws = to_datetime('now')

        # While Data not received, sleep until timeout
        while self._zmq._valid_response_('zmq') == False:

            sleep(_delay)

            if (to_datetime('now') - _ws).total_seconds() > (_delay * _wbreak):
                break

        # If Data received, return symbol
        if self._zmq._valid_response_('zmq'):

            _response = self._zmq._get_response_()

            if ('_symbol' in _response.keys()):
                return _response['_symbol']

        # Default
        return 0
