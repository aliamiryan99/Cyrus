# -*- coding: utf-8 -*-
"""
    DWX_ZMQ_Strategy.py
    --
    @author: Darwinex Labs (www.darwinex.com)
    
    Copyright (c) 2019 onwards, Darwinex. All rights reserved.
    
    Licensed under the BSD 3-Clause License, you may not use this file except 
    in compliance with the License. 
    
    You may obtain a copy of the License at:    
    https://opensource.org/licenses/BSD-3-Clause
"""

from MetaTrader.api.DWX_ZeroMQ_Connector_v2_0_1_RC8 import DWX_ZeroMQ_Connector
from MetaTrader.examples.template.modules.DWX_ZMQ_Execution import DWX_ZMQ_Execution
from MetaTrader.examples.template.modules.DWX_ZMQ_Reporting import DWX_ZMQ_Reporting

class DWX_ZMQ_Strategy(object):
    
    def __init__(self, _name="DEFAULT_STRATEGY",    # Name 
                 _symbols=[('EURUSD',0.01),     # List of (Symbol,Lotsize) tuples
                           ('GBPUSD',0.01)],
                 _broker_gmt=3,                 # Darwinex GMT offset
                 _pulldata_handlers = [],       # Handlers to process Data received through PULL port.
                 _subdata_handlers = [],        # Handlers to process Data received through SUB port.
                 _verbose=False):               # Print ZeroMQ messages
                 
        self._name = _name
        self._symbols = _symbols
        self._broker_gmt = _broker_gmt
        
        # Not entirely necessary here.
        self._zmq = DWX_ZeroMQ_Connector(_pulldata_handlers=_pulldata_handlers,
                                         _subdata_handlers=_subdata_handlers,
                                         _verbose=_verbose)
        
        # Modules
        self._execution = DWX_ZMQ_Execution(self._zmq)
        self._reporting = DWX_ZMQ_Reporting(self._zmq)
        
    ##########################################################################
    
    def _run_(self):
        
        """
        Enter strategy logic here
        """
         
    ##########################################################################
    def take_order(self, type, symbol, volume, tp, sl):
        order = self._zmq._generate_default_order_dict()
        order['_symbol'] = symbol
        order['_lots'] = volume
        order['_TP'] = tp
        order['_SL'] = sl
        trade =  self._execution._execute_(order)
        return trade

    def buy(self, symbol, volume, tp, sl):
        return self.take_order(0, symbol, volume, tp, sl)

    def sell(self, symbol, volume, tp, sl):
        return self.take_order(1, symbol, volume, tp, sl)

    def close(self, ticket):
        self._zmq._DWX_MTX_CLOSE_TRADE_BY_TICKET_(ticket)

    def get_open_positions(self):
        return self._reporting._get_open_trades_()
