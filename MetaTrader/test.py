
from MetaTrader.api.DWX_ZeroMQ_Connector_v2_0_1_RC8 import DWX_ZeroMQ_Connector
from MetaTrader.modules.DWX_ZMQ_Reporting import DWX_ZMQ_Reporting
from MetaTrader.modules.DWX_ZMQ_Execution import DWX_ZMQ_Execution
from MetaTrader.Config import Config
from datetime import datetime

from time import sleep
import copy

_zmq = DWX_ZeroMQ_Connector()
_reporting = DWX_ZMQ_Reporting(_zmq)
_executor = DWX_ZMQ_Execution(_zmq)

def get_data(symbol, time_frame, history_size):
    _zmq._DWX_MTX_SEND_HIST_REQUEST_(_symbol=symbol,
                                          _timeframe=Config.timeframes_dic[time_frame],
                                          _count=history_size)
    sleep(0.5)
    _histories = _zmq._History_DB[symbol + '_' + time_frame]
    for item in _histories:
        item['Time'] = datetime.strptime(item['Time'], Config.date_format)
    return _histories

def get_identifier(time, time_frame):
    identifier = time.day
    if time_frame == "H12":
        identifier = time.hour // 12
    if time_frame == "H4":
        identifier = time.hour // 4
    if time_frame == "H1":
        identifier = time.hour
    if time_frame == "M30":
        identifier = time.minute // 30
    if time_frame == "M15":
        identifier = time.minute // 15
    if time_frame == "M5":
        identifier = time.minute // 5
    if time_frame == "M1":
        identifier = time.minute
    return identifier

def aggregate_data(histories, time_frame):
    old_id = get_identifier(histories[0]['Time'], time_frame)
    new_history = []
    new_history.append(copy.deepcopy(histories[0]))
    for i in range(1, len(histories)):
        new_id = get_identifier(histories[i]['Time'], time_frame)
        if new_id != old_id:
            new_history.append(copy.deepcopy(histories[i]))
            old_id = new_id
        else:
            new_history[-1]['High'] = max(new_history[-1]['High'], histories[i]['High'])
            new_history[-1]['Low'] = max(new_history[-1]['Low'], histories[i]['Low'])
            new_history[-1]['Close'] = histories[i]['Close']
    return new_history


def take_order(type, symbol, volume, tp, sl):
    order = _zmq._generate_default_order_dict()
    order['_type'] = type
    order['_symbol'] = symbol
    order['_lots'] = volume
    order['_TP'] = tp
    order['_SL'] = sl
    return _executor._execute_(order)

def buy(symbol, volume, tp, sl):
    return take_order(0, symbol, volume, tp, sl)

def sell(symbol, volume, tp, sl):
    return take_order(1, symbol, volume, tp, sl)

def close(ticket):
    _zmq._DWX_MTX_CLOSE_TRADE_BY_TICKET_(ticket)

def get_open_orders():
    return _reporting._get_open_trades_()

def get_balance():
    return _reporting._get_balance()


buy("EURUSD.I", 0.01, 0, -200)