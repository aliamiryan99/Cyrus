import pandas as pd
from Simulation import Utility as ut

key = 1234512351

# symbols_dict = {'EURUSD': 0, 'GBPUSD': 1, 'NZDUSD': 2, 'USDCAD': 3, 'USDCHF': 4, 'USDJPY': 5, 'AUDUSD': 6}
# symbols_list = ['EURUSD', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY', 'AUDUSD']
# symbols_list = {'EURUSD': 5, 'GBPUSD': 5, 'NZDUSD': 5, 'USDCAD': 5, 'USDCHF': 5, 'USDJPY': 3, 'AUDUSD': 5}

symbols_dict = {'EURUSD': 0, 'GBPUSD': 1, 'NZDUSD': 2, 'AUDUSD': 3}
symbols_list = ['EURUSD', 'GBPUSD', 'NZDUSD', 'AUDUSD']
symbols_digit = {'EURUSD': 5, 'GBPUSD': 5, 'NZDUSD': 5, 'AUDUSD': 5}

SYMBOL = 0

def initialize():
    """
        this method get all config properties from inputs file
    """
    csv_config = pd.read_csv('strategy_config.csv')
    data_paths = []
    data_paths += ["Data/Major/EURUSD/" + csv_config['time input'][0] + ".csv"]
    data_paths += ["Data/Major/GBPUSD/" + csv_config['time input'][0] + ".csv"]
    data_paths += ["Data/Major/NZDUSD/" + csv_config['time input'][0] + ".csv"]
    # data_paths += ["Data/Major/USDCAD/" + csv_config['time input'][0] + ".csv"]
    # data_paths += ["Data/Major/USDCHF/" + csv_config['time input'][0] + ".csv"]
    # data_paths += ["Data/Major/USDJPY/" + csv_config['time input'][0] + ".csv"]
    data_paths += ["Data/Major/AUDUSD/" + csv_config['time input'][0] + ".csv"]
    #data_paths += ["Data/Major H1 to Month/XAUUSD/" + csv_config['time input'][0] + ".csv"]
    #data_paths += ["Data/Major H1 to Month/RAND/" + csv_config['time input'][0] + ".csv"]

    order_path = "../inputs/orders.csv"

    orders = pd.read_csv(order_path)
    stop_loss_begin = csv_config['stop loss'][0]
    take_profit_begin = csv_config['take profit'][0]
    volume_begin = csv_config['volume'][0]
    data_format = csv_config['date format'][0]
    print(csv_config['start date'][0])

    data = ut.csv_to_df(data_paths, date_format=data_format)

    return data, orders, stop_loss_begin, take_profit_begin, volume_begin


def calc_index(year, w, d, h4, h1, m30, m15, m5):
    return int(m5 + m15*3 + m30*6 + h1*12 + h4*48 + d*288 + w*1440 + year*365*1440)

def predict():
    # this method create a file with random predicts
    # with this format of orders[date, ticket, type, symbol, volume, T/P, S/L, price]

    data, orders, stop_loss_begin, take_profit_begin, volume_begin = initialize()
    predicts = []
    predict = []
    open_buy_orders = []
    open_sell_orders = []

    i_test = 0
    orders_size = orders.shape[0]
    for i in range(orders_size):
        row = orders.iloc[i]
        index_data = calc_index(row['Year'], row['W'], row['D'], row['H4'],
                                row['H1'], row['M30'], row['M15'], row['M5'])
        symbol = row['ins']
        price = row['price']
        take_profit = row['TP']
        stop_loss = row['SL']
        if symbol in symbols_list:
            action = 1
        else:
            action = -1
            price = 1/price
            take_profit = 1/take_profit
            stop_loss = 1/stop_loss
            symbol = symbol[-3:] + symbol[:3]

        print(row['Year'] , row['W'], row['D'], row['H4'],
                                row['H1'], row['M30'], row['M15'], row['M5'])
        print(f"symbol : {symbol} , index : {index_data}")
        row_data = data[symbols_dict[symbol]].iloc[index_data]
        price = round(price, symbols_digit[symbol])
        take_profit = round(take_profit, symbols_digit[symbol])
        stop_loss = round(stop_loss, symbols_digit[symbol])
        if action != 0:
            volume = round(volume_begin, 2)
            type = ''
            if action == 1:
                type = 'buy'
                # # open_buy_orders.append([i + key, 'close', symbol, volume, take_profit, stop_loss, 0])
                # if len(open_buy_orders) == treshhold:
                #     close_order = open_buy_orders[0]
                #     open_buy_orders.pop(0)
                #     close_order.insert(0, Data[symbols_dict[close_order[2]]].iloc[i]['GMT'])
                #     predicts.append(close_order)
            elif action == -1:
                type = 'sell'
                # # open_sell_orders.append([i + key, 'close', symbol, volume, take_profit, stop_loss, 0])
                # if len(open_sell_orders) == treshhold:
                #     close_order = open_sell_orders[0]
                #     open_sell_orders.pop(0)
                #     close_order.insert(0, Data[symbols_dict[close_order[2]]].iloc[i]['GMT'])
                #     predicts.append(close_order)

            predict += [row_data['GMT']]  # date
            predict += [i + key]  # ticket
            predict += [type]  # type
            predict += [symbol]  # symbol
            predict += [volume]  # volume
            predict += [take_profit]  # take profit
            predict += [stop_loss]  # stop los
            predict += [price]  # price

            predicts.append(predict)
            print(f'predict : {predict}')
            predict = []
    df = pd.DataFrame(predicts, columns=['date', 'ticket', 'type', 'symbol', 'volume', 'T/P', 'S/L', 'price'])
    df.to_hdf('Simulation/orders.h5', key='df', mode='w')
    return predicts

if __name__ == '__main__':
    predict()
