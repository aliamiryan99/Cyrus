import copy

import pandas as pd
from Simulation import Utility as ut
from Strategy.Config import Config

key = 1234512351

symbols_dict = {'EURUSD': 0, 'GBPUSD': 1, 'NZDUSD': 2, 'USDCAD': 3, 'USDCHF': 4, 'USDJPY': 5, 'AUDUSD': 6}
symbols_list = ['EURUSD', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY', 'AUDUSD']
symbols_digit = {'EURUSD': 5, 'GBPUSD': 5, 'NZDUSD': 5, 'USDCAD': 5, 'USDCHF': 5, 'USDJPY': 3, 'AUDUSD': 5}


SYMBOL = 0

def initialize():
    """
        this method get all config properties from inputs file
    """
    time_frame = Config.time_frame

    sl = Config.sl
    tp = Config.tp
    volume = Config.volume
    date_format = Config.date_format

    order_path = []
    order_path += ["inputs/signal/orders.csv"]

    orders = ut.csv_to_df(order_path, date_format=date_format)
    orders = orders[0]
    return orders, sl, tp, volume


def predict():
    # this method create a file with random predicts
    # with this format of orders[date, ticket, type, symbol, volume, T/P, S/L, price]

    orders, sl, tp, volume = initialize()
    predicts = []
    predict = []

    open_buy_orders = []
    open_sell_orders = []

    orders_size = orders.shape[0]
    if Config.DEBUG:
        print(orders)
    for i in range(orders_size):
        row = orders.iloc[i]
        symbol = row['Symbol']
        price = row['Price']
        take_profit = price
        stop_loss = price
        action = 0
        if row['Order'] == 'buy':
            action = 1
            take_profit += tp * 10 ** -symbols_digit[symbol]
            stop_loss -= sl * 10 ** -symbols_digit[symbol]
        if row['Order'] == 'sell':
            take_profit -= tp * 10 ** -symbols_digit[symbol]
            stop_loss += sl * 10 ** -symbols_digit[symbol]
            action = -1
        price = round(price, symbols_digit[symbol])
        if Config.closing_strategy == "TP_SL":
            take_profit = round(take_profit, symbols_digit[symbol])
            stop_loss = round(stop_loss, symbols_digit[symbol])
        elif Config.closing_strategy == "onReverse":
            take_profit = 0
            stop_loss = 0
        if action != 0:
            volume = round(volume, 2)
            type = ''
            if action == 1:
                type = 'buy'
                if Config.closing_strategy == "onReverse":
                    origin_sell_orders = copy.copy(open_sell_orders)
                    for close_order in origin_sell_orders:
                        if close_order[2] == symbol:
                            close_order.insert(0, row['GMT'])
                            predicts.append(close_order)
                            open_sell_orders.remove(close_order)
                if len(open_buy_orders) + len(open_sell_orders) < Config.max_trades or Config.max_trades == 0:
                    open_buy_orders.append([i + key, 'close', symbol, volume, take_profit, stop_loss, 0])
            elif action == -1:
                type = 'sell'
                if Config.closing_strategy == "onReverse":
                    origin_buy_orders = copy.copy(open_buy_orders)
                    for close_order in origin_buy_orders:
                        if close_order[2] == symbol:
                            close_order.insert(0, row['GMT'])
                            predicts.append(close_order)
                            open_buy_orders.remove(close_order)
                    if len(open_buy_orders) + len(open_sell_orders) < Config.max_trades or Config.max_trades == 0:
                        open_sell_orders.append([i + key, 'close', symbol, volume, take_profit, stop_loss, 0])

            if len(open_buy_orders) + len(open_sell_orders) < Config.max_trades or Config.max_trades == 0:
                predict += [row['GMT']]  # date
                predict += [i + key]  # ticket
                predict += [type]  # type
                predict += [symbol]  # symbol
                predict += [volume]  # volume
                predict += [take_profit]  # take profit
                predict += [stop_loss]  # stop los
                predict += [price]  # price

                predicts.append(predict)
                if Config.DEBUG:
                    print(f'predict : {predict}')
                predict = []
    df = pd.DataFrame(predicts, columns=['date', 'ticket', 'type', 'symbol', 'volume', 'T/P', 'S/L', 'price'])
    if Config.DEBUG:
        print(df)
    df.to_hdf('Simulation/orders.h5', key='df', mode='w')
    return predicts
