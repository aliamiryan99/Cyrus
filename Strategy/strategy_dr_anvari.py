import pandas as pd
from datetime import datetime
from Simulation import Outputs, Utility as ut
from Strategy.Config import Config

key = 1
symbols_list = ['EURUSD', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY', 'AUDUSD']
symbols_dict = {'EURUSD': 0, 'GBPUSD': 1, 'NZDUSD': 2, 'USDCAD': 3, 'USDCHF': 4, 'USDJPY': 5, 'AUDUSD': 6}
symbols_digit = {'EURUSD': 5, 'GBPUSD': 5, 'NZDUSD': 5, 'USDCAD': 5, 'USDCHF': 5, 'USDJPY': 3, 'AUDUSD': 5}

symbols_enable = {'EURUSD': 1, 'GBPUSD': 1, 'NZDUSD': 1, 'USDCAD': 0, 'USDCHF': 0, 'USDJPY': 1, 'AUDUSD': 1}


def initialize():
    """
        this method get all config properties from inputs file
    """
    time_frame = Config.time_frame
    data_paths = []
    data_paths += ["Data/Major/EURUSD/" + time_frame + ".csv"]
    data_paths += ["Data/Major/GBPUSD/" + time_frame + ".csv"]
    data_paths += ["Data/Major/NZDUSD/" + time_frame + ".csv"]
    data_paths += ["Data/Major/USDCAD/" + time_frame + ".csv"]
    data_paths += ["Data/Major/USDCHF/" + time_frame + ".csv"]
    data_paths += ["Data/Major/USDJPY/" + time_frame + ".csv"]
    data_paths += ["Data/Major/AUDUSD/" + time_frame + ".csv"]
    data = ut.csv_to_df(data_paths)

    stop_loss_begin = Config.sl
    take_profit_begin = Config.tp
    volume_begin = Config.volume
    date_foramt = Config.date_format
    start_date = datetime.strptime(Config.start_date, date_foramt)
    end_date = datetime.strptime(Config.end_date, date_foramt)

    return data, stop_loss_begin, take_profit_begin, volume_begin, start_date, end_date, date_foramt

def strategyDr_Anvari1(row, pre_row, i, start, candles_treshhold, cnt_max, cnt_min):
    next_action = 0
    if i != start:
        if cnt_max > candles_treshhold:
            if row['Close'] > max(pre_row['Open'], pre_row['Close']):
                next_action = 1
                cnt_max = 0
        if max(row['Open'], row['Close']) < max(pre_row['Open'], pre_row['Close']):
            if cnt_max == 0:
                cnt_max = 2
            else:
                cnt_max += 1
        else:
            cnt_max = 0
        if cnt_min > candles_treshhold:
            if row['Close'] < min(pre_row['Open'], pre_row['Close']):
                next_action = -1
                cnt_min = 0
        if min(row['Open'], row['Close']) > min(pre_row['Open'], pre_row['Close']):
            if cnt_min == 0:
                cnt_min = 2
            else:
                cnt_min += 1
        else:
            cnt_min = 0

    return cnt_min, cnt_max, next_action

def strategyDr_Anvari2(row, pre_row, i, start, candles_treshhold, cnt_max, cnt_min):
    next_action = 0
    if i != start:
        if max(row['Open'], row['Close']) < max(pre_row['Open'], pre_row['Close']):
            if cnt_max == 0:
                cnt_max = 2
            else:
                cnt_max += 1
        else:
            cnt_max = 0
        if row['High'] > max(pre_row['Open'], pre_row['Close']):
            if cnt_max > candles_treshhold:
                next_action = 1
                cnt_max = 0
        if min(row['Open'], row['Close']) > min(pre_row['Open'], pre_row['Close']):
            if cnt_min == 0:
                cnt_min = 2
            else:
                cnt_min += 1
        else:
            cnt_min = 0
        if row['Low'] < min(pre_row['Open'], pre_row['Close']):
            if cnt_min > candles_treshhold:
                next_action = -1
                cnt_min = 0
    return cnt_min, cnt_max, next_action

def predict():
    # this method create a file with random predicts
    # with this format of orders[date, ticket, type, symbol, volume, T/P, S/L, price(for pending orders only)]
    data, stop_loss_begin, take_profit_begin, volume_begin, start_date, end_date, date_foramt = initialize()
    global key
    predicts = []
    for symbol in symbols_list:
        if symbols_enable[symbol]:
            start = Outputs.index_date(data[symbols_dict[symbol]], start_date)
            end = Outputs.index_date(data[symbols_dict[symbol]], end_date)
            predict = []
            row = None
            open_buy_orders = []
            open_sell_orders = []

            print(f"{start_date}, {end_date}")
            print(f"{start}, {end}")
            # strategies
            cnt_min = 0
            cnt_max = 0

            candles_treshhold = 5

            pre_row = None

            symbol_i = symbols_dict[symbol]
            next_action = 0
            past_action = 0
            for i in range(start, end):
                row = data[symbol_i].iloc[i]
                action = next_action
                cnt_min, cnt_max, next_action = strategyDr_Anvari1(row, pre_row, i, start, candles_treshhold, cnt_max, cnt_min)
                pre_row = row
                if action != 0:
                    volume = round(volume_begin, 2)
                    sd = symbols_digit[symbol]
                    take_profit = round(take_profit_begin/10**sd, sd)
                    stop_loss = round(stop_loss_begin/10**sd, sd)
                    type = ''
                    if action == 1:
                        type = 'buy'
                        take_profit = row['Open'] + take_profit
                        stop_loss = row['Open'] - stop_loss
                        open_buy_orders.append([key, 'close', symbol, volume, take_profit, stop_loss, 0])
                        while len(open_sell_orders) != 0:
                            close_order = open_sell_orders[0]
                            open_sell_orders.pop(0)
                            close_order.insert(0, data[symbols_dict[close_order[2]]].iloc[i]['GMT'])
                            predicts.append(close_order)
                    elif action == -1:
                        type = 'sell'
                        take_profit = row['Open'] - take_profit
                        stop_loss = row['Open'] + stop_loss
                        open_sell_orders.append([key, 'close', symbol, volume, take_profit, stop_loss, 0])
                        while len(open_buy_orders) != 0:
                            close_order = open_buy_orders[0]
                            open_buy_orders.pop(0)
                            close_order.insert(0, data[symbols_dict[close_order[2]]].iloc[i]['GMT'])
                            predicts.append(close_order)


                    predict += [row['GMT']]  # date
                    predict += [key]  # ticket
                    predict += [type]  # type
                    predict += [symbol]  # symbol
                    predict += [volume]  # volume
                    predict += [take_profit]  # take profit
                    predict += [stop_loss]  # stop los
                    predict += [0]  # price

                    key += 1
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
