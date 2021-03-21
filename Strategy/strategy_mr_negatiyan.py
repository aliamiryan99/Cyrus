import pandas as pd
from datetime import datetime
from Simulation import Outputs, Utility as ut

symbols = ['EURUSD', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY', 'AUDUSD', 'XAUUSD', 'RANDUSD']
symbols_label = {'EURUSD': 0, 'GBPUSD': 1, 'NZDUSD': 2, 'USDCAD': 3, 'USDCHF': 4, 'USDJPY': 5, 'AUDUSD': 6, 'XAUUSD': 7, 'RANDUSD': 8}
key = 1234512351

SYMBOL = 0
TAKE_PROFIT = 0.0060
STOP_LOSS = 0.0090

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
    data_paths += ["Data/Major H1 to Month/AUDUSD/" + csv_config['time input'][0] + ".csv"]
    #data_paths += ["Data/Major H1 to Month/XAUUSD/" + csv_config['time input'][0] + ".csv"]
    #data_paths += ["Data/Major H1 to Month/RAND/" + csv_config['time input'][0] + ".csv"]

    #Data = ut.csv_to_df(data_paths, date_format="%Y-%m-%d %H:%M:%S")       # for h1
    data = ut.csv_to_df(data_paths, date_format="%Y/%m/%d %H:%M:%S")       # for day

    test_paths = []
    test_paths += ["tests/negatian/EURUSD_Signals.csv"]
    test_paths += ["tests/negatian/GBPUSD_Signals.csv"]
    test_paths += ["tests/negatian/NZDUSD_Signals.csv"]
    test_paths += ["tests/negatian/USDCAD_Signals.csv"]
    test_paths += ["tests/negatian/USDCHF_Signals.csv"]
    test_paths += ["tests/negatian/USDJPY_Signals.csv"]
    test_paths += ["tests/negatian/AUDUSD_Signals.csv"]

    test = pd.read_csv(test_paths[SYMBOL])
    test['GMT'] = pd.to_datetime(test['GMT'], format='%d-%b-%Y %H:%M:%S')
    test = test.drop_duplicates(subset='GMT')
    test = test.sort_values(['GMT'])
    stop_loss_begin = csv_config['stop loss'][0]
    take_profit_begin = csv_config['take profit'][0]
    volume_begin = csv_config['volume'][0]
    print(csv_config['start date'][0])
    start_date = datetime.strptime(csv_config['start date'][0], '%Y-%m-%d')
    end_date = datetime.strptime(csv_config['end date'][0], '%Y-%m-%d')

    return data, test, stop_loss_begin, take_profit_begin, volume_begin, start_date, end_date

def predict():
    # this method create a file with random predicts
    # with this format of orders[date, ticket, type, symbol, volume, T/P, S/L, price]

    data, test, stop_loss_begin, take_profit_begin, volume_begin, start_date, end_date = initialize()
    start = Outputs.index_date(data[SYMBOL], start_date)
    end = Outputs.index_date(data[SYMBOL], end_date)
    predicts = []
    predict = []
    row = None
    open_buy_orders = []
    open_sell_orders = []

    print(f"{start_date}, {end_date}")
    print(f"{start}, {end}")

    treshhold = 50



    i_test = 0
    for i in range(start, end):
        row = data[SYMBOL].iloc[i]
        if i_test == test.shape[0]:
            break
        row_test = test.iloc[i_test]
        if row['GMT'] == row_test['GMT'] and i_test < test.shape[0]:
            action = row_test['type']
            if action == 'sell':
                action = 1
            elif action == 'buy':
                action = -1
            price = row_test['price']
            i_test += 1
            if i_test == test.shape[0]:
                break
            row_test = test.iloc[i_test]
            if action != 0:
                volume = round(volume_begin, 2)
                type = ''
                if action == 1:
                    take_profit = price + TAKE_PROFIT
                    stop_loss = price - STOP_LOSS
                    type = 'buy'
                    #open_buy_orders.append([i + key, 'buy_stop', symbols[SYMBOL], volume, take_profit, stop_loss, 0])
                    if len(open_buy_orders) == treshhold:
                        close_order = open_buy_orders[0]
                        open_buy_orders.pop(0)
                        close_order.insert(0, data[symbols_label[close_order[2]]].iloc[i]['GMT'])
                        predicts.append(close_order)
                elif action == -1:
                    take_profit = price - TAKE_PROFIT
                    stop_loss = price + STOP_LOSS
                    type = 'sell'
                    #open_sell_orders.append([i + key, 'sell_stop', symbols[SYMBOL], volume, take_profit, stop_loss, 0])
                    if len(open_sell_orders) == treshhold:
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
                predict += [price]  # price

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
    df.to_hdf('Simulation/orders.h5', key='df', mode='w')
    return predicts

if __name__ == '__main__':
    predict()
