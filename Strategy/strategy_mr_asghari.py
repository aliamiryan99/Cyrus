import pandas as pd
from datetime import datetime
from Simulation import Outputs, Utility as ut

symbols = ['EUROUSD', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY', 'AUDUSD']
symbols_label = {'EUROUSD': 0, 'GBPUSD': 1, 'NZDUSD': 2, 'USDCAD': 3, 'USDCHF': 4, 'USDJPY': 5, 'AUDUSD': 6}
key = 1234512351

SYMBOL = 0

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
    data = ut.csv_to_df(data_paths, date_format="%Y-%m-%d %H:%M:%S")

    test = ut.csv_to_df(["test.csv"], date_format="%Y-%m-%d %H:%M:%S")
    test = test[0]
    stop_loss_begin = csv_config['stop loss'][0]
    take_profit_begin = csv_config['take profit'][0]
    volume_begin = csv_config['volume'][0]
    print(csv_config['start date'][0])
    start_date = datetime.strptime(csv_config['start date'][0], '%Y-%m-%d')
    end_date = datetime.strptime(csv_config['end date'][0], '%Y-%m-%d')

    return data, test, stop_loss_begin, take_profit_begin, volume_begin, start_date, end_date

def predict():
    # this method create a file with random predicts
    # with this format of orders[date, ticket, type, symbol, volume, T/P, S/L, price(for pending orders only)]
    data, test, stop_loss_begin, take_profit_begin, volume_begin, start_date, end_date = initialize()
    start = Outputs.index_date(data, start_date)
    end = Outputs.index_date(data, end_date)
    predicts = []
    predict = []
    row = None
    open_buy_orders = []
    open_sell_orders = []

    print(f"{start_date}, {end_date}")
    print(f"{start}, {end}")
    # strategies
    cnt_min = 0
    cnt_max = 0

    treshhold = 9

    next_action = 0
    i_test = 0
    for i in range(start, end):
        row = data[SYMBOL].iloc[i]
        row_test = test.iloc[i_test]
        if row['GMT'] == row_test['GMT']:
            action = row_test['winner']
            i_test += 1
            if action != 0:
                volume = round(volume_begin, 2)
                take_profit = 0.005
                stop_loss = 0.005
                type = ''
                if action == 1:
                    type = 'buy'
                    take_profit = row['Open'] + take_profit
                    stop_loss = row['Open'] - stop_loss
                    open_buy_orders.append([i + key, 'close', symbols[SYMBOL], volume, take_profit, stop_loss, 0])
                    if len(open_buy_orders) == treshhold:
                        close_order = open_buy_orders[0]
                        open_buy_orders.pop(0)
                        close_order.insert(0, data[symbols_label[close_order[2]]].iloc[i]['GMT'])
                        predicts.append(close_order)
                elif action == -1:
                    type = 'sell'
                    take_profit = row['Open'] - take_profit
                    stop_loss = row['Open'] + stop_loss
                    open_sell_orders.append([i + key, 'close', symbols[SYMBOL], volume, take_profit, stop_loss, 0])
                    if len(open_sell_orders) == 0:
                        close_order = open_sell_orders[0]
                        open_sell_orders.pop(0)
                        close_order.insert(0, data[symbols_label[close_order[2]]].iloc[i]['GMT'])
                        predicts.append(close_order)

                predict += [row['GMT']]  # date
                predict += [i + key]  # ticket
                predict += [type]  # type
                predict += [symbols[SYMBOL]]  # symbol
                predict += [volume]  # volume
                predict += [take_profit]  # take profit
                predict += [stop_loss]  # stop los
                predict += [0]  # price

                predicts.append(predict)
                print(f'predict : {predict}')
                predict = []
    for order in open_buy_orders:
        order.insert(0, row['GMT'])
        predicts.append(order)
    for order in open_sell_orders:
        order.insert(0, row['GMT'])
        predicts.append(order)
    df = pd.DataFrame(predicts, columns=['date', 'ticket', 'type', 'symbol', 'volume', 'T/P', 'S/L', 'price'])
    print(df)
    df.to_hdf('Simulation/orders.h5', key='df', mode='w')

if __name__ == '__main__':
    predict()
