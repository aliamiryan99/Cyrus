import random as rand
import pandas as pd
from datetime import datetime
from Simulation import Outputs, Utility as ut

symbols = ['EUROUSD', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY', 'AUDUSD']
symbols_label = {'EUROUSD': 0, 'GBPUSD': 1, 'NZDUSD': 2, 'USDCAD': 3, 'USDCHF': 4, 'USDJPY': 5, 'AUDUSD': 6}
key = 1234512351


def initialize():
    """
        this method get all config properties from inputs file
    """
    csv_config = pd.read_csv('strategy_config.csv')
    data_paths = []
    data_paths += ["Data/Major H1 to Month/EUROUSD/" + csv_config['time input'][0] + ".csv"]
    data_paths += ["Data/Major H1 to Month/GBPUSD/" + csv_config['time input'][0] + ".csv"]
    data_paths += ["Data/Major H1 to Month/NZDUSD/" + csv_config['time input'][0] + ".csv"]
    data_paths += ["Data/Major H1 to Month/USDCAD/" + csv_config['time input'][0] + ".csv"]
    data_paths += ["Data/Major H1 to Month/USDCHF/" + csv_config['time input'][0] + ".csv"]
    data_paths += ["Data/Major H1 to Month/USDJPY/" + csv_config['time input'][0] + ".csv"]
    #data_paths += ["Data/Major H1 to Month/AUDUSD/" + csv_config['time input'][0] + ".csv"]
    data = ut.csv_to_df(data_paths)

    stop_loss_begin = csv_config['stop loss begin'][0]
    stop_loss_end = csv_config['stop loss end'][0]
    take_profit_begin = csv_config['take profit begin'][0]
    take_profit_end = csv_config['take profit end'][0]
    volume_begin = csv_config['volume begin'][0]
    volume_end = csv_config['volume end'][0]
    predict_period = csv_config['predict period'][0]
    start_date = datetime.strptime(csv_config['start date'][0], '%d.%m.%Y %H:%M:%S.%f')
    end_date = datetime.strptime(csv_config['end date'][0], '%d.%m.%Y %H:%M:%S.%f')

    return data, predict_period, stop_loss_begin, stop_loss_end, take_profit_begin, take_profit_end, volume_begin, \
           volume_end, start_date, end_date


def predict():
    # this method create a file with random predicts
    # with this format of orders[date, ticket, type, symbol, volume, T/P, S/L, price(for pending orders only)]
    data, predict_period, stop_loss_begin, stop_loss_end, take_profit_begin, \
    take_profit_end, volume_begin, volume_end, start_date, end_date = initialize()
    predict_period = int(predict_period)
    start = Outputs.index_date(data, start_date)
    end = Outputs.index_date(data, end_date)
    predicts = []
    predict = []
    row = None
    open_orders = []
    modify_orders = []
    open_buy_orders = []
    open_sell_orders = []

    # strategies
    cnt_min = 0
    cnt_max = 0

    pre_row = None

    symbol = 1
    next_action = 0
    for i in range(start, end, predict_period):
        row = data[symbol].iloc[i]
        action = rand.randint(-1, 1)
        if action != 0:
            volume = round(rand.randint(volume_begin * 100, volume_end * 100) / 100, 2)
            take_profit = round(rand.randint(take_profit_begin * 100000, take_profit_end * 100000) / 100000, 5)
            stop_loss = round(rand.randint(stop_loss_begin * 100000, stop_loss_end * 100000) / 100000, 5)
            type = ''
            price = 0
            if action == 1:
                price = row['Open'] + 0.00005
                type = 'buy_limit'
                take_profit = price + take_profit
                stop_loss = price - stop_loss
                open_buy_orders.append([i + key, 'buy_stop', symbols[symbol], volume, take_profit, stop_loss, price])
                if len(open_buy_orders) > 10:
                    close_order = open_buy_orders[0]
                    open_buy_orders.pop(0)
                    close_order.insert(0, data[symbols_label[close_order[2]]].iloc[i]['GMT'])
                    predicts.append(close_order)
            elif action == -1:
                price = row['Open'] - 0.00005
                type = 'sell_limit'
                take_profit = price - take_profit
                stop_loss = price + stop_loss
                open_sell_orders.append([i + key, 'sell_stop', symbols[symbol], volume, take_profit, stop_loss, price])
                if len(open_sell_orders) > 10:
                    close_order = open_sell_orders[0]
                    open_sell_orders.pop(0)
                    close_order.insert(0, data[symbols_label[close_order[2]]].iloc[i]['GMT'])
                    predicts.append(close_order)

            predict += [row['GMT']]  # date
            predict += [i + key]  # ticket
            predict += [type]  # type
            predict += [symbols[symbol]]  # symbol
            predict += [volume]  # volume
            predict += [take_profit]  # take profit
            predict += [stop_loss]  # stop los
            predict += [price]  # pending order price

            predicts.append(predict)
            print(f'predict : {predict}')
            predict = []

    df = pd.DataFrame(predicts, columns=['date', 'ticket', 'type', 'symbol', 'volume', 'T/P', 'S/L', 'price'])
    print(df)
    df.to_hdf('Simulation/orders.h5', key='df', mode='w')


if __name__ == '__main__':
    predict()
