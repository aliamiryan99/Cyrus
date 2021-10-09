"""
    Class Simulation:
        A Simulation for forex market
        _____________________________________________
        Attributes:
            public:
                balance : float ,
                equity : float ,
                profit : float ,
            private:
                leverage : int
                open_buy_positions : ListOfDictionary{ 'OpenTime' 'Type', 'OpenPrice', 'Symbol', 'TP',
                'SL', 'Volume', 'close_volume', 'Ticket' } ,
                open_sell_position : ListOfDictionary{ 'OpenTime', 'OpenPrice', 'Symbol', 'TP',
                'SL', 'Volume', 'close_volume', 'Ticket' } ,
                closed_buy_positions : ListOfDictionary{ 'OpenTime', 'OpenPrice', 'CloseTime', 'ClosePrice',
                 'CloseType', 'Symbol', 'SL', 'TP', 'Volume', 'Ticket'  } ,
                closed_sell_positions : ListOfDictionary{ 'OpenTime', 'OpenPrice', 'CloseTime', 'ClosePrice',
                 'CloseType', 'Symbol', 'SL', 'TP', 'Volume', 'Ticket'  } ,
                open_buy_limits : ListOfDictionary{'OpenTime', 'Price', 'Symbol', 'TP' 'SL',
                 'Volume', 'Ticket' } ,
                open_sell_limits : ListOfDictionary{'OpenTime', 'Price', 'Symbol', 'TP' 'SL',
                 'Volume', 'Ticket' } ,
        Methods:
            public:
                take_order (date, price, symbol, tp, sl, volume, ticket) : void
                    open a buy or sell position according to symbol or reversed symbol
                buy (start_time, start_price, symbol, take_profit, stop_loss, volume, ticket) : void
                    open a buy position
                sell (start_time, start_price, symbol, take_profit, stop_loss, volume, ticket) : void
                    open a sell position
                modify (ticket, take_profit, stop_loss) : void
                    change tp and sl of specific position according to ticket
                buy_limit (GMT, price, symbol, take_profit, stop_loss, volume, ticket) : void
                    open a buy limit order
                sell_limit (GMT, price, symbol, take_profit, stop_loss, volume, ticket) : void
                    open a sell limit order
                close (type, position, gmt, price, volume, ticket, p='Manual Close') : void # type is 'Buy' or 'Sell'
                    close specific position according to ticket
                close_all_symbol (t, symbol, gmt, price, p='Manual Close') : void
                    close all open positions of specific symbol
                close_all (date, order) : void
                    close all open positions at open candle of date
                get_margin () : float
                get_free_margin () : float
                get_margin_level () : float
                get_open_positions_count () : int
                get_closed_positions_count () : int
            private:
                update (time) : void
                    update Simulation -> like check TPs and SLs
                update_history () : void
                    update balance, equity and ... histories
                exit () : void
                    close all open positions and check TPs and SLs
                adjust_time (time, time_frame) : datetime
                    for changing the input times to our Data formats time
                cal_margin (type, symbol, price, volume) : float
                    calculate margin for input position
                cal_profit (type, symbol, price_open, price_close, volume) : float
                    calculate profit for input position
                order_possible (price, volume, symbol) : bool
                    check if we haven't enough money
                get_equity (i) : void
                    update self.equity
                check_zero_equity (i) : void
                    check if our equity reach 0.05 of initilize balance then we can't countinue
                get_position (ticket) : Dictionary
                stop_loss_check (i) : void
                    check stop loss of open positions
                take_profit_check (i) : void
                    check tack profit of open positions
                pending_orders_check (i) : void
                    check buy limits and sell limits
                get_closed_positions () : ListOfDictionary
                get_total_profit (i) : float


"""


from tqdm import tqdm
import os

from Simulation import Utility as ut
from datetime import datetime
import pandas as pd
from bokeh.io import output_file
from Simulation import Candlestick
from Simulation import Outputs
import copy

from Configuration.Trade.BackTestConfig import Config
from Configuration.Trade.InstanceConfig import InstanceConfig
from Configuration.Trade.MarketConfig import MarketConfig

from Shared.Functions import Functions

DEBUG = Config.DEBUG

SYMBOL = 0

predict = []
balance_history = []
equity_history = []
margin_history = []
free_margin_history = []
equity_percent_history = []
profit_history = []
predicts = []
positions = []
data = []
data_shows = []

df_profit_history, df_equity_percent_history, df_free_margin_history = 0, 0, 0
df_margin_history, df_equity_history = 0, 0
df_balance_history, positions_df, total_profit, wins = 0, 0, 0, 0
total, len_data, test_years, difference = 0, 0, 0, 0
simulation, start_date, end_date, date_format, risk, time_frame_input, time_frame_show = 0, 0, 0, 0, 1, 0, 0
output_dir = ""


symbols_dict = Config.symbols_dict
symbols_list = Config.symbols_list
symbols_pip = Config.symbols_pip
symbols_show = Config.symbols_show
symbols_pip_value = Config.symbols_pip_value
symbols_with_usd = Config.symbols_with_usd
spreads = Config.spreads
for key in spreads.keys():
    spreads[key] *= 10**-symbols_pip[key]

volume_digit = Config.volume_digit

initial_balance = 0


class Simulation:

    def __init__(self, leverage=100, balance=1000, start_time=None, end_time=None):
        self.total_profit_or_loss = 0
        self.balance = balance
        self.equity = balance
        self.margin = 0
        self.profit = 0
        self.call_margin = False
        global initial_balance
        initial_balance = balance
        self.closed_buy_positions = []
        self.open_buy_positions = []
        self.closed_sell_positions = []
        self.open_sell_positions = []
        self.open_buy_limits = []  # include:
        self.open_sell_limits = []  # include: { Start GMT, limit_price, symbol, take profit, stop loss,
        # volume, ticket }
        self.leverage = leverage
        self.start_index = {}
        self.start_index_show = {}
        for symbol in symbols_list:
            if start_time is not None:
                self.start_index[symbol] = Outputs.index_date_v3(data[symbols_dict[symbol]], start_time)
                self.start_index_show[symbol] = Outputs.index_date_v2(data_shows[symbols_dict[symbol]], start_time)
            else:
                self.start_index[symbol] = 0
                self.start_index_show[symbol] = 0
        self.end_index = {}
        self.end_index_show = {}
        for symbol in symbols_list:
            if end_time is not None:
                self.end_index[symbol] = Outputs.index_date_v3(data[symbols_dict[symbol]], end_time)
                self.end_index_show[symbol] = Outputs.index_date_v2(data_shows[symbols_dict[symbol]], end_time)
            else:
                self.end_index[symbol] = 0
                self.end_index_show[symbol] = 0
        self.last_index = {}
        self.last_index_show = {}
        for symbol in symbols_list:
            self.last_index[symbol] = self.start_index[symbol]
            self.last_index_show[symbol] = self.start_index_show[symbol]

    def update(self, time):
        time = self.adjust_time(time, time_frame_input)
        date = data[0]['Time'][self.last_index[symbols_list[0]]]
        if time > date:
            i = self.last_index[symbols_list[0]]
            date_show = data_shows[0][self.last_index_show[symbols_list[0]]]['Time']
            if time > date_show:
                self.update_history(i, date_show)
                for symbol in symbols_list:
                    self.last_index_show[symbol] += 1
            self.check_positions()
            for symbol in symbols_list:
                self.last_index[symbol] += 1
            if DEBUG:
                print(f"updated : {time}, {i}")

    def update_history(self, index, date):
        # save history
        equity = self.get_equity()
        balance_history.append([index, date, self.balance])
        margin_history.append([index, date, self.get_margin()])
        equity_history.append([index, date, equity])
        free_margin_history.append([index, date, self.get_free_margin()])
        equity_percent_history.append([index, date, (equity / initial_balance) * 100])
        n_profit, wins, total = self.get_total_profit()
        profit_history.append([index, date, n_profit - self.profit])
        self.profit = n_profit

    def check_positions(self):
        # check positions
        self.take_profit_check()
        self.stop_loss_check()
        self.pending_orders_check()
        self.check_zero_equity()

    def exit(self):
        last_index = self.last_index[symbols_list[0]]
        last_time = data[0]['Time'][last_index]
        if DEBUG:
            print(f"exit {last_time}")
        self.update(last_time)
        self.close_all("exit Simulation")
        self.update_history(last_index, last_time)

    def adjust_time(self, time, time_frame):
        if time_frame == "M5":
            time = time.replace(minute=(time.minute // 5) * 5)
        elif time_frame == "M15":
            time = time.replace(minute=(time.minute // 15) * 15)
        elif time_frame == "M30":
            time = time.replace(minute=(time.minute // 30) * 30)
        elif time_frame == "H1":
            time = time.replace(minute=0)
        elif time_frame == "H4":
            time = time.replace(minute=0, hour=(time.hour // 4) * 4)
        elif time_frame == "D":
            time = time.replace(minute=0, hour=0)
        return time

    def cal_margin(self, type, symbol, price, volume):
        LOT = symbols_pip_value[symbol]
        if type == 'Buy':
            if symbol[:3] == 'USD':
                return round(volume * LOT / self.leverage, volume_digit)  # margin
            else:
                return round((volume * LOT) * price / self.leverage, volume_digit)  # margin

        elif type == 'Sell':
            if symbol[:3] == 'USD':
                return round(volume * LOT / self.leverage, volume_digit)  # margin
            else:
                return round((volume * LOT) * price / self.leverage, volume_digit)  # margin

    def cal_profit(self, type, symbol, price_open, price_close, volume):
        LOT = symbols_pip_value[symbol]
        if type == 'Buy':
            if symbols_with_usd[symbol]:
                return round((price_close - price_open) * volume * LOT, volume_digit)  # profit or loss
            else:
                return round(((price_close - price_open) * volume * LOT) / price_close,
                             volume_digit)  # profit or loss
        elif type == 'Sell':
            if symbols_with_usd[symbol]:
                return round((price_open - price_close) * volume * LOT, volume_digit)  # profit or loss
            else:
                return round(((price_open - price_close) * volume * LOT) / price_close,
                             volume_digit)  # profit or loss

    def buy(self, start_time, start_price, symbol, take_profit, stop_loss, volume, ticket):  # row is a series

        check, time, index, volume, row = self.check_order('Buy', start_time, start_price, symbol, take_profit,
                                                           stop_loss, volume)

        if not check:
            return None

        if self.order_possible(start_price, volume, symbol):
            self.open_buy_positions.append({'OpenTime': start_time, 'Type': 'Buy',
                                            'OpenPrice': start_price + (spreads[symbol]),
                                            'Symbol': symbol, 'TP': take_profit, 'SL': stop_loss,
                                            'Volume': volume, 'ClosedVolume': 0, 'Ticket': ticket})
            return self.open_buy_positions[-1]
        return None

    def sell(self, start_time, start_price, symbol, take_profit, stop_loss, volume, ticket):  # row is a series

        check, time, index, volume, row = self.check_order('Sell', start_time, start_price, symbol, take_profit,
                                                           stop_loss, volume)
        if not check:
            return None

        if self.order_possible(start_price, volume, symbol):
            self.open_sell_positions.append(
                {'OpenTime': start_time, 'Type': 'Sell', 'OpenPrice': start_price, 'Symbol': symbol,
                 'TP': take_profit, 'SL': stop_loss, 'Volume': volume,
                 'ClosedVolume': 0, 'Ticket': ticket})
            return self.open_sell_positions[-1]
        return None

    def check_order(self, type, start_time, start_price, symbol, take_profit, stop_loss, volume):
        time = self.adjust_time(start_time, time_frame_input)
        index = Outputs.index_date_v3(data[Config.symbols_dict[symbol]], time)
        volume = min(max(round(volume, Config.volume_digit), 10 ** -Config.volume_digit), Config.max_volume)
        row = Functions.item_data_list_to_dic(data[symbols_dict[symbol]], index)
        if type == 'Buy':
            if (take_profit < start_price and take_profit != 0) or (stop_loss > start_price and stop_loss != 0):
                print(f"order is invalid(tp&sl)({symbol})(buy)(price:{start_price})(tp:{take_profit})"
                      f"(sl:{stop_loss})[{start_time}]")
                return 0, time, index, volume, row
        if type == 'Sell':
            if (take_profit > start_price and take_profit != 0) or (stop_loss < start_price and stop_loss != 0):
                print(f"order is invalid(tp&sl)({symbol})(sell)(price:{start_price})(tp:{take_profit})(sl:{stop_loss})[{start_time}]")
                return 0, time, index, volume, row
        if start_price < row['Low'] - 0.00001 or start_price > row['High'] + 0.00001:
            print(f"order is invalid(price)({symbol})(buy)(price:{start_price})(low:{row['Low']})(high:{row['High']})[{start_time}]")
            return 0, time, index, volume, row
        if row['Volume'] == 0:
            print(f"order is invalid(Weekend)")
            return 0, time, index, volume
        return 1, time, index, volume, row

    def take_order(self, date, price, symbol, tp, sl, volume, ticket):
        if symbol in symbols_list:
            self.buy(date, price, symbol, tp, sl, volume, ticket)
        else:
            price = 1 / price
            tp = 1 / tp
            sl = 1 / sl
            symbol = symbol[-3:] + symbol[:3]
            self.sell(date, price, symbol, tp, sl, volume, ticket)
        pass

    def modify(self, ticket, take_profit, stop_loss):

        for position in self.open_buy_positions:
            if position['Ticket'] == ticket:
                i = self.last_index[position['Symbol']]
                row = Functions.item_data_list_to_dic(data[symbols_dict[position['Symbol']]], i)
                if (take_profit < row['Low'] and take_profit != 0) or (stop_loss > row['High'] and stop_loss != 0):
                    print(f"order is invalid(tp&sl)({position['Symbol']})(buy)(price:{row['Low']})(tp:{take_profit})(sl:{stop_loss})")
                    continue
                position['TP'] = take_profit
                position['SL'] = stop_loss
                return
        for position in self.open_sell_positions:
            if position['Ticket'] == ticket:
                i = self.last_index[position['Symbol']]
                row = Functions.item_data_list_to_dic(data[symbols_dict[position['Symbol']]], i)
                if (take_profit > row['High'] and take_profit != 0) or (stop_loss < row['Low'] and stop_loss != 0):
                    print(f"order is invalid(tp&sl)({position['Symbol']})(sell)(price:{row['High']})(tp:{take_profit})(sl:{stop_loss})")
                    continue
                position['TP'] = take_profit
                position['SL'] = stop_loss

    def buy_limit(self, time, price, symbol, take_profit, stop_loss, volume, ticket):
        self.open_buy_limits.append({'OpenTime': time, 'Price': price, 'Symbol': symbol, 'TP': take_profit,
                                     'SL': stop_loss, 'Volume': volume, 'Ticket': ticket})

    def sell_limit(self, time, price, symbol, take_profit, stop_loss, volume, ticket):
        self.open_sell_limits.append({'OpenTime': time, 'Price': price, 'Symbol': symbol, 'TP': take_profit,
                                      'SL': stop_loss, 'Volume': volume, 'Ticket': ticket})

    def close(self, time, price, volume, ticket, p='Manual Close'):  # t is 'Buy' or 'Sell'

        t, position = self.get_position(ticket)
        if volume > position['Volume']:
            if DEBUG:
                print("close volume greater than remainder volume")
            return False
        if t == 'Buy':
            if position['ClosedVolume'] == 0:
                self.closed_buy_positions.append(
                    {'OpenTime': position['OpenTime'], 'OpenPrice': position['OpenPrice'], 'CloseTime': time,
                     'ClosePrice': price, 'CloseType': p, 'Symbol': position['Symbol'],
                     'SL': position['SL'], 'TP': position['TP'], 'Volume': volume, 'Ticket': ticket})
                self.balance += self.cal_profit(t, position['Symbol'], position['OpenPrice'], price,
                                                volume)  # profit or loss
                position['Volume'] -= volume
                position['ClosedVolume'] = volume
            else:
                for c_position in self.closed_buy_positions:
                    if c_position['Ticket'] == ticket:
                        c_position['Volume'] += volume
                        self.balance += self.cal_profit(t, position['Symbol'], position['OpenPrice'], price,
                                                        volume)  # profit or loss
                        position['Volume'] -= volume
                        position['ClosedVolume'] += volume
                        break
            if position['Volume'] == 0:
                self.open_buy_positions.remove(position)

        elif t == 'Sell':
            price = price + (spreads[position['Symbol']])
            if position['ClosedVolume'] == 0:
                self.closed_sell_positions.append(
                    {'OpenTime': position['OpenTime'], 'OpenPrice': position['OpenPrice'], 'CloseTime': time,
                     'ClosePrice': price, 'CloseType': p, 'Symbol': position['Symbol'],
                     'SL': position['SL'],
                     'TP': position['TP'], 'Volume': volume, 'Ticket': ticket})
                self.balance += self.cal_profit(t, position['Symbol'], position['OpenPrice'], price,
                                                volume)  # profit or loss
                position['Volume'] -= volume
                position['ClosedVolume'] = volume
            else:
                for c_position in self.closed_sell_positions:
                    if c_position['Ticket'] == ticket:
                        c_position['Volume'] += volume
                        self.balance += self.cal_profit(t, position['Symbol'], position['OpenPrice'], price,
                                                        volume)  # profit or loss
                        position['Volume'] -= volume
                        position['ClosedVolume'] += volume
                        break
            if position['Volume'] == 0:
                self.open_sell_positions.remove(position)

    def close_all_symbol(self, t, symbol, gmt, price, p='Manual Close'):  # t is 'Buy' or 'Sell'   , close all positions of a specific symbol
        """
            close all buy or sell positions
        """
        if t == 'Buy':
            for position in self.open_buy_positions:
                if position['Symbol'] == symbol:
                    self.open_buy_positions.remove(position)
                    if position['Volume'] == 0:
                        self.closed_buy_positions.append(
                            {'OpenTime': position['OpenTime'], 'OpenPrice': position['OpenPrice'], 'CloseTime': gmt,
                             'ClosePrice': price,
                             'CloseType': p, 'Symbol': position['Symbol'], 'SL': position['SL']
                                , 'TP': position['TP'], 'Volume': position['Volume'],
                             'Ticket': position['Ticket']})
                        self.balance += self.cal_profit(t, position['Symbol'], position['OpenPrice'], price,
                                                        position['Volume'])  # profit or loss
                    else:
                        for c_position in self.closed_buy_positions:
                            if c_position['Ticket'] == position['Ticket']:
                                c_position['Volume'] += position['Volume']
                                self.balance += self.cal_profit(t, position['Symbol'], position['OpenPrice'], price,
                                                                position['Volume'])  # profit or loss
                                break
        elif t == 'Sell':
            for position in self.open_sell_positions:
                price = price + (spreads[position['Symbol']])
                if position['Symbol'] == symbol:
                    self.open_sell_positions.remove(position)
                    if position['Volume'] == 0:
                        self.closed_sell_positions.append(
                            {'OpenTime': position['OpenTime'], 'OpenPrice': position['OpenPrice'], 'CloseTime': gmt,
                             'ClosePrice': price,
                             'CloseType': p, 'Symbol': position['Symbol'], 'SL': position['SL']
                                , 'TP': position['TP'], 'Volume': position['Volume'],
                             'Ticket': position['Ticket']})
                        self.balance += self.cal_profit(t, position['Symbol'], position['OpenTime'], price,
                                                        position['Volume'])  # profit or loss
                    else:
                        for c_position in self.closed_buy_positions:
                            if c_position['Ticket'] == position['Ticket']:
                                c_position['Volume'] += position['Volume']
                                self.balance += self.cal_profit(t, position['Symbol'], position['OpenTime'], price,
                                                                position['Volume'])  # profit or loss
                                break

    def close_all(self, order):  # close all positions
        for position in self.open_buy_positions:
            i = self.last_index[position['Symbol']]
            price = data[symbols_dict[position['Symbol']]]['Close'][i]
            if position['ClosedVolume'] == 0:
                self.closed_buy_positions.append(
                    {'OpenTime': position['OpenTime'], 'OpenPrice': position['OpenPrice'],
                     'CloseTime': data[symbols_dict[position['Symbol']]]['Time'][i],
                     'ClosePrice': price, 'CloseType': order, 'Symbol': position['Symbol'],
                     'SL': position['SL'], 'TP': position['TP'],
                     'Volume': position['Volume'], 'Ticket': position['Ticket']})
                self.balance += self.cal_profit('Buy', position['Symbol'], position['OpenPrice'], price,
                                                position['Volume'])  # profit or loss
            else:
                for c_position in self.closed_buy_positions:
                    if c_position['Ticket'] == position['Ticket']:
                        c_position['Volume'] += position['Volume']
                        self.balance += self.cal_profit('Buy', position['Symbol'], position['OpenPrice'], price,
                                                        position['Volume'])  # profit or loss
                        break
        self.open_buy_positions.clear()
        for position in self.open_sell_positions:
            i = self.last_index[position['Symbol']]
            price = data[symbols_dict[position['Symbol']]]['Close'][i] \
                    + (spreads[position['Symbol']])
            if position['ClosedVolume'] == 0:
                self.closed_sell_positions.append(
                    {'OpenTime': position['OpenTime'], 'OpenPrice': position['OpenPrice'],
                     'CloseTime': data[symbols_dict[position['Symbol']]]['Time'][i],
                     'ClosePrice': price, 'CloseType': order, 'Symbol': position['Symbol'],
                     'SL': position['SL'], 'TP': position['TP'],
                     'Volume': position['Volume'], 'Ticket': position['Ticket']})
                self.balance += self.cal_profit('Sell', position['Symbol'], position['OpenPrice'], price,
                                                position['Volume'])  # profit or loss
            else:
                for c_position in self.closed_buy_positions:
                    if c_position['Ticket'] == position['Ticket']:
                        c_position['Volume'] += position['Volume']
                        self.balance += self.cal_profit('Sell', position['Symbol'], position['OpenPrice'], price,
                                                        position['Volume'])  # profit or loss
                        break

        self.open_sell_positions.clear()

    def order_possible(self, price, volume, symbol):
        """
            check possibility of your order
        """
        margin = self.margin + self.cal_margin('Buy', symbol, price, volume)
        equity = self.equity + self.cal_profit('Buy', symbol, price,
                                               price - (spreads[symbol]), volume)
        return ((equity / margin) * 100) > 120

    def get_margin(self):
        self.margin = 0
        for position in self.open_buy_positions:
            self.margin += self.cal_margin('Buy', position['Symbol'], position['OpenPrice'], position['Volume'])
        for position in self.open_sell_positions:
            self.margin += self.cal_margin('Sell', position['Symbol'], position['OpenPrice'], position['Volume'])
        return self.margin

    def get_equity(self):
        self.equity = self.balance
        for position in self.open_buy_positions:
            time = self.adjust_time(position['OpenTime'], time_frame_input)
            i = self.last_index[position['Symbol']]
            if time != data[symbols_dict[position['Symbol']]]['Time'][i]:
                self.equity += self.cal_profit('Buy', position['Symbol'], position['OpenPrice'],
                                               data[symbols_dict[position['Symbol']]]['Open'][i],
                                               position['Volume'])  # add profit
        for position in self.open_sell_positions:
            time = self.adjust_time(position['OpenTime'], time_frame_input)
            i = self.last_index[position['Symbol']]
            if time != data[symbols_dict[position['Symbol']]]['Time'][i]:
                self.equity += self.cal_profit('Sell', position['Symbol'], position['OpenPrice'],
                                               data[symbols_dict[position['Symbol']]]['Open'][i]
                                               + (spreads[position['Symbol']]),
                                               position['Volume'])  # add profit
        return self.equity

    def get_free_margin(self):
        return self.equity - self.margin

    def get_margin_level(self):
        return (self.equity / self.margin) * 100

    def check_zero_equity(self):
        if self.get_equity() <= initial_balance * 0.05:
            self.close_all("zero equity")
            if not self.call_margin:
                self.call_margin = True
                print('CALL MARGIN')

    def get_position(self, ticket):
        for position in self.open_buy_positions:
            if position['Ticket'] == ticket:
                return 'Buy', position
        for position in self.open_sell_positions:
            if position['Ticket'] == ticket:
                return 'Sell', position
        return False, False

    def get_open_positions_count(self):
        return len(self.open_buy_positions) + len(self.open_sell_positions)

    def get_closed_positions_count(self):
        return len(self.closed_buy_positions) + len(self.closed_sell_positions)

    def stop_loss_check(self):
        """
            check stop loss happened or not for open buy and sell positions
            and if it's happened close position
        """
        open_buy_positions_origin = copy.copy(self.open_buy_positions)
        for position in open_buy_positions_origin:
            i = self.last_index[position['Symbol']]
            row = Functions.item_data_list_to_dic(data[symbols_dict[position['Symbol']]], i)
            time = self.adjust_time(position['OpenTime'], time_frame_input)
            if time < row['Time'] and position['SL'] != 0:
                if row['Low'] <= position['SL']:
                    self.close(row['Time'], position['SL'], position['Volume'],
                               position['Ticket'], 'Stop Loss')

        open_sell_positions_origin = copy.copy(self.open_sell_positions)
        for position in open_sell_positions_origin:
            i = self.last_index[position['Symbol']]
            row = Functions.item_data_list_to_dic(data[symbols_dict[position['Symbol']]], i)
            time = self.adjust_time(position['OpenTime'], time_frame_input)
            if time < row['Time'] and position['SL'] != 0:
                if row['High'] + spreads[position['Symbol']] >= position['SL']:
                    self.close(row['Time'], position['SL'] - spreads[position['Symbol']] , position['Volume'],
                               position['Ticket'], 'Stop Loss')

    def take_profit_check(self):
        """
            heck take profit happened or not for open buy and sell positions
            and if it's happened close all positions
        """
        open_buy_positions_origin = copy.copy(self.open_buy_positions)
        for position in open_buy_positions_origin:
            i = self.last_index[position['Symbol']]
            row = Functions.item_data_list_to_dic(data[symbols_dict[position['Symbol']]], i)
            time = self.adjust_time(position['OpenTime'], time_frame_input)
            if time <= row['Time'] and position['TP'] != 0:
                if row['High'] > position['TP']:
                    self.close(row['Time'], position['TP'], position['Volume'],
                               position['Ticket'], 'Take Profit')
        open_sell_positions_origin = copy.copy(self.open_sell_positions)
        for position in open_sell_positions_origin:
            i = self.last_index[position['Symbol']]
            row = Functions.item_data_list_to_dic(data[symbols_dict[position['Symbol']]], i)
            time = self.adjust_time(position['OpenTime'], time_frame_input)
            if time <= row['Time'] and position['TP'] != 0:
                if row['Low'] + spreads[position['Symbol']] <= position['TP']:
                    self.close(row['Time'], position['TP'] - spreads[position['Symbol']], position['Volume'],
                               position['Ticket'], 'Take Profit')

    def pending_orders_check(self):
        for buy in self.open_buy_limits:
            i = self.last_index[buy['Symbol']]
            if data[symbols_dict[buy['Symbol']]]['Low'][i] <= buy['Price']:
                self.buy(data[symbols_dict[buy['Symbol']]]['Time'][i], buy['Price'], buy['Symbol'],
                         buy['TP'], buy['SL'], buy['Volume'],
                         buy['Ticket'])
                self.open_buy_limits.remove(buy)
        for sell in self.open_sell_limits:
            i = self.last_index[sell['Symbol']]
            if data[symbols_dict[sell['Symbol']]]['High'][i] + spreads[sell['Symbol']] >= sell['Price']:
                self.sell(data[symbols_dict[sell['Symbol']]]['Time'][i], sell['Price'], sell['Symbol'],
                          sell['TP'], sell['SL'],
                          sell['Volume'], sell['Ticket'])
                self.open_sell_limits.remove(sell)

    def get_closed_positions(self):
        positions = []
        for position in self.closed_buy_positions:
            positions.append(
                [position['OpenTime']] + ['Buy'] + [position['Ticket'], position['Volume'], position['Symbol']] + [
                    position['OpenPrice']]
                + [position['SL']] + [position['TP']]
                + [position['CloseTime']] + [position['ClosePrice']] + [position['CloseType']] +
                [self.cal_profit('Buy', position['Symbol'], position['OpenPrice'], position['ClosePrice'],
                                 position['Volume'])] +
                [(position['ClosePrice'] - position['OpenPrice']) * 10 ** symbols_pip[position['Symbol']] / 10] +
                [Outputs.index_date_v2(data_shows[symbols_dict[position['Symbol']]],
                                    self.adjust_time(position['OpenTime'], time_frame_input))]
                + [Outputs.index_date_v2(data_shows[symbols_dict[position['Symbol']]], position['CloseTime'])])
        for position in self.closed_sell_positions:
            positions.append(
                [position['OpenTime']] + ['Sell'] + [position['Ticket'], position['Volume'], position['Symbol']] + [
                    position['OpenPrice']]
                + [position['SL']] + [position['TP']]
                + [position['CloseTime']] + [position['ClosePrice']] + [position['CloseType']] +
                [self.cal_profit('Sell', position['Symbol'], position['OpenPrice'], position['ClosePrice'],
                                 position['Volume'])] +
                [(position['OpenPrice'] - position['ClosePrice']) * 10 ** symbols_pip[position['Symbol']] / 10] +
                [Outputs.index_date_v2(data_shows[symbols_dict[position['Symbol']]],
                                    self.adjust_time(position['OpenTime'], time_frame_input))]
                + [Outputs.index_date_v2(data_shows[symbols_dict[position['Symbol']]], position['CloseTime'])])
        return positions

    def get_total_profit(self):
        total_profit = 0
        wins = 0
        total = len(self.closed_buy_positions) + len(self.closed_sell_positions)
        for position in self.closed_buy_positions:
            profit = self.cal_profit('Buy', position['Symbol'], position['OpenPrice'], position['ClosePrice'],
                                     position['Volume'])  # add profit
            if profit > 0:
                wins += 1
            total_profit += profit
        for position in self.closed_sell_positions:
            profit = self.cal_profit('Sell', position['Symbol'], position['OpenPrice'], position['ClosePrice'],
                                     position['Volume'])  # add profit
            if profit > 0:
                wins += 1
            total_profit += profit
        for position in self.open_buy_positions:
            i = self.last_index[position['Symbol']]
            profit = self.cal_profit('Buy', position['Symbol'], position['OpenPrice']
                                     , data[symbols_dict[position['Symbol']]]['Open'][i],
                                     position['Volume'])
            if profit > 0:
                wins += 1
            total_profit += profit
        for position in self.open_sell_positions:
            i = self.last_index[position['Symbol']]
            profit = self.cal_profit('Sell', position['Symbol'], position['OpenPrice']
                                     , data[symbols_dict[position['Symbol']]]['Open'][i],
                                     position['Volume'])
            if profit > 0:
                wins += 1
            total_profit += profit
        return total_profit, wins, total

    def get_open_buy_positions_count(self, symbol):
        cnt = 0
        for position in self.open_buy_positions:
            if position['Symbol'] == symbol:
                cnt+=1
        return cnt

    def get_open_sell_positions_count(self, symbol):
        cnt = 0
        for position in self.open_sell_positions:
            if position['Symbol'] == symbol:
                cnt+=1
        return cnt

    def get_last_buy_closed(self, symbol):
        for i in range(len(self.closed_buy_positions)-1, -1, -1):
            if self.closed_buy_positions[i]['Symbol'] == symbol:
                return self.closed_buy_positions[i]
        return None

    def get_last_sell_closed(self, symbol):
        for i in range(len(self.closed_sell_positions)-1, -1, -1):
            if self.closed_sell_positions[i]['Symbol'] == symbol:
                return self.closed_sell_positions[i]
        return None


def initialize():
    """
        this method get all config properties from inputs file
    """
    global data, data_shows, start_date, end_date, date_format, risk, time_frame_input, time_frame_show, initial_balance
    data_paths = []
    data_shows_paths = []
    time_frame_input = Config.time_frame
    time_frame_show = Config.time_frame_show
    for symbol in symbols_list:
        data_paths += ["Data/" + Config.categories_list[symbol] + "/" + symbol + "/" + time_frame_input + ".csv"]

    for symbol in symbols_list:
        data_shows_paths += ["Data/" + Config.categories_list[symbol] + "/" + symbol + "/" + time_frame_show + ".csv"]

    balance = Config.balance

    leverage = Config.leverage
    date_format = Config.date_format
    start_date = datetime.strptime(Config.start_date, date_format)
    end_date = datetime.strptime(Config.end_date, date_format)

    data = ut.csv_to_df(data_paths, date_format=date_format)
    data_shows = ut.csv_to_df(data_shows_paths, date_format=date_format)

    for i in range(len(data)):
        data[i] = data[i].to_dict("list")
        data_shows[i] = data_shows[i][data_shows[i].Volume != 0]
        data_shows[i] = data_shows[i].to_dict("Records")

    initial_balance = balance
    simulation = Simulation(leverage, balance)
    return simulation, data, start_date, end_date, date_format, risk, time_frame_input


def simulate(simulation, predicts, data, start_date, end_date, risk):
    i_predict = 0
    predicts_size = len(predicts)
    start = Outputs.index_date_v3(data[SYMBOL], start_date)  # start index of backtesting
    end = Outputs.index_date_v3(data[SYMBOL], end_date)  # end index of backtesting
    profit = 0
    symbol = predicts[i_predict][3]
    if DEBUG:
        print(f"{start}, {end}")
    for i in tqdm(range(start, end-1)):
        if DEBUG:
            print(i, symbol)
        date = data[symbols_dict[symbol]]['Time'][i]
        # save history
        equity = simulation.get_equity(i)
        balance_history.append([i, date, simulation.balance])
        margin_history.append([i, date, simulation.get_margin()])
        equity_history.append([i, date, equity])
        free_margin_history.append([i, date, simulation.get_free_margin()])
        equity_percent_history.append([i, date, (equity / initial_balance) * 100])

        # calculate volume with specific risk  for each 100 pip
        volume = max(round((((simulation.balance) * (risk / 100)) / 1000), volume_digit), 10**-volume_digit)

        # perform order
        while i_predict < predicts_size and predicts[i_predict][0] == date:
            row = Functions.item_data_list_to_dic(data[symbols_dict[symbol]], i)
            if DEBUG:
                print(f"predict : {predicts[i_predict]}")
            price = predicts[i_predict][7]
            if price == 0:
                price = row['Open']
            if predicts[i_predict][2] == 'Buy':  # buy
                if not predicts[i_predict][5] > predicts[i_predict][6]:
                    if DEBUG:
                        print("take prfit and stop loss is incorrect")
                elif price < row['Low'] - 0.0000001 or price > row['High'] + 0.0000001:
                    if DEBUG:
                        print(f"price is invalid {price}, {row['Low']}, {row['High']}")
                else:
                    if DEBUG:
                        print(f"{row['Time']}, {row['Low']}, {row['High']}, {price}")
                    simulation.buy(row['Time'], price, symbol, predicts[i_predict][5], predicts[i_predict][6],
                                   volume, predicts[i_predict][
                                       1])  # date, price, symbol, take_profit, stop_loss, volume, ticket
                    # volume, ticket
            elif predicts[i_predict][2] == 'Sell':  # sell
                if not predicts[i_predict][5] < predicts[i_predict][6]:
                    if DEBUG:
                        print("take prfit and stop loss is incorrect")
                elif price < row['Low'] - 0.0000001 or price > row['High'] + 0.0000001:
                    if DEBUG:
                        print(f"price is invalid {price}, {row['Low']}, {row['High']}")
                else:
                    if DEBUG:
                        print(f"{row['Time']},{row['Low']}, {row['High']}, {price}")
                    simulation.sell(row['Time'], price, symbol, predicts[i_predict][5], predicts[i_predict][6],
                                    volume, predicts[i_predict][
                                        1])  # date, price, symbol, take_profit, stop_loss, volume, ticket
                    # volume, ticket
            elif predicts[i_predict][2] == 'close':  # close
                t, position = simulation.get_position(predicts[i_predict][1])
                if t:
                    simulation.close(t, position, date, row['Open'], position['Volume']
                                     , predicts[i_predict][1])
            elif predicts[i_predict][2] == 'modify':
                simulation.modify(predicts[i_predict][2], predicts[i_predict][5], predicts[i_predict][6])
            elif predicts[i_predict][2] == 'buy_limit':
                if not predicts[i_predict][5] > predicts[i_predict][6]:
                    if DEBUG:
                        print("take prfit and stop loss is incorrect")
                else:
                    simulation.buy_limit(row['Time'], predicts[i_predict][7], predicts[i_predict][3],
                                         predicts[i_predict][5],
                                         predicts[i_predict][6], volume, predicts[i_predict][1])
            elif predicts[i_predict][2] == 'sell_limit':
                if not predicts[i_predict][5] < predicts[i_predict][6]:
                    if DEBUG:
                        print("take prfit and stop loss is incorrect")
                else:
                    simulation.sell_limit(row['Time'], predicts[i_predict][7], predicts[i_predict][3],
                                          predicts[i_predict][5],
                                          predicts[i_predict][6], volume, predicts[i_predict][1])

            i_predict += 1
            if i_predict < predicts_size:
                symbol = predicts[i_predict][3]
                date = data[symbols_dict[symbol]]['Time'][i]

        # check positions
        simulation.take_profit_check(i)
        simulation.stop_loss_check(i)
        simulation.pending_orders_check(i)
        simulation.check_zero_equity(i)
        if (i - start - 1) % 24 == 0:
            n_profit, wins, total = simulation.get_total_profit(i)
            profit_history.append([i, date, n_profit - profit])
            profit = n_profit
    simulation.close_all(end, "exit Simulation")


def adjust_time(time_frame_input):
    global predicts
    if time_frame_input == "M5":
        for predict in predicts:
            predict[0] = predict[0].replace(minute=(predict[0].minute // 5) * 5)
    elif time_frame_input == "M15":
        for predict in predicts:
            predict[0] = predict[0].replace(minute=(predict[0].minute // 15) * 15)
    elif time_frame_input == "M30":
        for predict in predicts:
            predict[0] = predict[0].replace(minute=(predict[0].minute // 30) * 30)
    elif time_frame_input == "H1":
        for predict in predicts:
            predict[0] = predict[0].replace(minute=0)
    elif time_frame_input == "H4":
        for predict in predicts:
            predict[0] = predict[0].replace(minute=0, hour=(predict[0].hour // 4) * 4)
    elif time_frame_input == "D":
        for predict in predicts:
            predict[0] = predict[0].replace(minute=0, hour=0)


def print_solution(positions, df_profit_history, df_free_margin_history, df_margin_history,
                   df_equity_history, df_balance_history, total_profit,
                   test_years, simulation, start_date, end_date):

    outputs_list = []
    Outputs.init_outputs(profit_history, positions, simulation, balance_history, equity_history, margin_history,
                         test_years, start_date, end_date, total_profit, df_balance_history, df_equity_history,
                         df_margin_history, df_free_margin_history, df_profit_history)
    print()
    print()
    print(f"time range : {start_date} - {end_date}")
    outputs_list.append(['Start time', f"{start_date}"])
    outputs_list.append(['End time', f"{end_date}"])
    print(f"total profit (pip): {int(total_profit)}$ ({Outputs.total_profit_in_pip})")
    outputs_list.append(['Total profit (pip)', f"{round(total_profit, 2)}$ ({round(Outputs.total_profit_in_pip, 2)})"])
    print(f"average AUM : {Outputs.average_aum}")
    outputs_list.append(['Average AUM', Outputs.average_aum])
    print(f"capacity : {Outputs.capacity}")
    outputs_list.append(['Capacity', Outputs.capacity])
    print(f"Leverage : {simulation.leverage}")
    outputs_list.append(['Leverage', simulation.leverage])
    print(f"Maximum dollar position size : {Outputs.max_pos_size}")
    outputs_list.append(['Maximum dollar position size', Outputs.max_pos_size])
    print(f"frequency of bets : {Outputs.frequency_of_bets}")
    outputs_list.append(['Frequency of bets', Outputs.frequency_of_bets])
    print(f"sharpe ratio : {Outputs.sharpe_ratio}")
    outputs_list.append(['Sharpe ratio', Outputs.sharpe_ratio])
    print(f"average holding period : {Outputs.average_holding_period}")
    outputs_list.append(['Average holding period', Outputs.average_holding_period])
    print(f"annualized turnover : {Outputs.annualized_turnover}")
    outputs_list.append(['Annualized turnover', Outputs.annualized_turnover])
    print(f"total trades: {len(positions)}")
    outputs_list.append(['Total trades', len(positions)])
    if Outputs.long_trades == 0:
        won = 0
    else:
        won = int(round(Outputs.won_long_trade / Outputs.long_trades, 2) * 100)
    print(
        f"Long Trades(won %): {Outputs.long_trades}({won}%)"
        f"\tRatio of longs: {int(Outputs.ratio_of_longs * 100)}%")
    outputs_list.append(['Long Trades(won %)',
                         f"{Outputs.long_trades}({won}%)"])

    if Outputs.short_trades == 0:
        won = 0
    else:
        won = int(round(Outputs.won_short_trade / Outputs.short_trades, 2) * 100)
    print(
        f"Short Trades(won %): {Outputs.short_trades}({won}%)"
        f"\tRatio of shorts: {int((1 - Outputs.ratio_of_longs) * 100)}%")
    outputs_list.append(['Ratio of longs', f"{int(Outputs.ratio_of_longs * 100)}%"])
    outputs_list.append(['Short Trades(won %)',
                         f"{Outputs.short_trades}({won}%)"])
    outputs_list.append(['Ratio of shorts', f"{int((1 - Outputs.ratio_of_longs) * 100)}%"])
    if len(positions) == 0:
        won = 0
    else:
        won = round((Outputs.won_short_trade + Outputs.won_long_trade) / len(positions), 2)
    print(f"profit trades(% of total): {Outputs.won_short_trade + Outputs.won_long_trade}"
          f"({won})")
    outputs_list.append(['Profit trades', f"{Outputs.won_short_trade + Outputs.won_long_trade}"])
    if len(positions) == 0:
        won = 0
    else:
        won = round(1 - (Outputs.won_short_trade + Outputs.won_long_trade) / len(positions), 2)
    print(f"loss trades(% of total): {len(positions) - (Outputs.won_long_trade + Outputs.won_short_trade)}"
          f"({won})")
    outputs_list.append(['Loss trades', f"{len(positions) - (Outputs.won_long_trade + Outputs.won_short_trade)}"])
    if len(positions) == 0:
        accuracy = 0
    else:
        accuracy = round((Outputs.won_short_trade + Outputs.won_long_trade) * 100 / len(positions), 2)
    outputs_list.append(['Accuracy', f"{accuracy}%"])

    print(
        f"Maximum Absolute Drawdown (%): {Outputs.maximum_absolute_drawdown}({Outputs.maximum_absolute_drawdown_percent}%)")
    outputs_list.append(['Maximum Absolute Drawdown (%)',
                         f"{Outputs.maximum_absolute_drawdown}({Outputs.maximum_absolute_drawdown_percent}%)"])
    print(
        f"Maximum Relative Drawdown (%): {Outputs.maximum_relative_drawdown}({Outputs.maximum_relative_drawdown_percent}%) {Outputs.maximum_relative_details}")
    outputs_list.append(['Maximum Relative Drawdown (%)',
                         f"{Outputs.maximum_relative_drawdown}({Outputs.maximum_relative_drawdown_percent}%)"])
    outputs_list.append(['Maximum Relative Drawdown Detail', f"{Outputs.maximum_relative_details}"])
    print(
        f"Maximal Absolute Drawdown (%): {Outputs.maximal_absolute_drawdown}({Outputs.maximal_absolute_drawdown_percent}%)")
    outputs_list.append(['Maximal Absolute Drawdown (%)',
                         f"{Outputs.maximal_absolute_drawdown}({Outputs.maximal_absolute_drawdown_percent}%)"])
    print(
        f"Maximal Relative Drawdown (%): {Outputs.maximal_relative_drawdown}({Outputs.maximal_relative_drawdown_percent}%) {Outputs.maximal_relative_details}")
    outputs_list.append(['Maximal Relative Drawdown (%)',
                         f"{Outputs.maximal_relative_drawdown}({Outputs.maximal_relative_drawdown_percent}%)"])
    outputs_list.append(['Maximal Relative Drawdown Detail', f"{Outputs.maximal_relative_details}"])

    print(f"Largest\tProfit Trade:{Outputs.largest_profit_trade},\tLargest Loss Trade:{Outputs.largest_loss_trade}")
    print(f"Largest\tProfit Pip Trade:{Outputs.largest_profit_trade_pip},\tLargest Loss Pip Trade:{Outputs.largest_loss_trade_pip}")
    outputs_list.append(['Largest Profit Trade', Outputs.largest_profit_trade])
    outputs_list.append(['Largest Profit Pip Trade', Outputs.largest_profit_trade_pip])
    outputs_list.append(['Largest Loss Trade', Outputs.largest_loss_trade])
    outputs_list.append(['Largest Loss Pip Trade', Outputs.largest_loss_trade_pip])
    print(f"Average\tProfit Trade:{Outputs.average_profit_trade},\tAverage Loss Trade:{Outputs.average_loss_trade}")
    print(f"Average\tProfit Pip Trade:{Outputs.average_profit_trade_pip},\tAverage Loss Pip Trade:{Outputs.average_loss_trade_pip}")
    outputs_list.append(['Average Profit Trade', Outputs.average_profit_trade])
    outputs_list.append(['Average Profit Pip Trade', Outputs.average_profit_trade_pip])
    outputs_list.append(['Average Loss Trade', Outputs.average_loss_trade])
    outputs_list.append(['Average Loss Pip Trade', Outputs.average_loss_trade_pip])
    print(f"Maximum\tconsecutive wins($):{Outputs.maximum_consecutive_wins}({Outputs.maximum_consecutive_wins_amount})"
          f"\tconsecutive loss($):{Outputs.maximum_consecutive_losses}({Outputs.maximum_consecutive_losses_amount})")
    print(
        f"Maximal\tconsecutive profit(count):{Outputs.maximal_consecutive_wins}({Outputs.maximal_consecutive_wins_count})"
        f"\tconsecutive loss(count):{Outputs.maximal_consecutive_losses}({Outputs.maximal_consecutive_losses_count})")
    print(
        f"Average\tconsecutive wins:{Outputs.average_consecutive_wins}"
        f"\tconsecutive loss:{Outputs.average_consecutive_losses}")
    print()
    print()
    global output_dir
    outputs_df = pd.DataFrame(outputs_list, columns=['title', 'value'])
    outputs_df.to_excel(output_dir + 'statistic.xlsx', index=False)


def show_candlestick(name, df, positions_df, df_balance, df_equity, start, trends, extends):
    global output_dir
    output_file(output_dir + name + ".html")
    Candlestick.candlestick_plot(df, positions_df, name, df_balance, df_equity, start,
                                 trends, extends)


def get_output(simulation, trends=None, extends=None, backtest_with_market=False):
    global output_dir
    output_dir = "Outputs/" + InstanceConfig.algorithm_name + "/" + InstanceConfig.algorithm_time_frame +\
                 "_" + InstanceConfig.trailing_time_frame + "_" + Config.time_frame + "/" + InstanceConfig.tag + "/"
    if backtest_with_market:
        output_dir = "Outputs/" + MarketConfig.strategy_name + "/" + MarketConfig.time_frame + "/" + MarketConfig.tag + "/"
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    positions = simulation.get_closed_positions()
    total_profit, wins, total = simulation.get_total_profit()

    positions_df = pd.DataFrame(positions,
                                columns=['TimeOpen', 'Type', 'Ticket', 'Volume', 'Symbol', 'OpenPrice', 'S/L', 'T/P'
                                        ,'TimeClose', 'PriceClose', 'Result', 'Profit', 'Profit in pip', 'Index',
                                         'IndexEnd'])
    positions_df = positions_df.sort_values(['TimeOpen'])
    positions_df.to_excel(output_dir + "history.xlsx", index=False)
    positions = positions_df.values.tolist()
    df_balance_history = pd.DataFrame(balance_history, columns=['index', 'x', 'balance'])
    df_equity_history = pd.DataFrame(equity_history, columns=['index', 'x', 'equity'])
    df_margin_history = pd.DataFrame(margin_history, columns=['index', 'x', 'margin'])
    df_free_margin_history = pd.DataFrame(free_margin_history, columns=['index', 'x', 'free margin'])
    df_equity_percent_history = pd.DataFrame(equity_percent_history, columns=['index', 'x', 'equity percent'])
    df_profit_history = pd.DataFrame(profit_history, columns=['index', 'x', 'profit'])

    difference = end_date - start_date
    test_years = (difference.days + difference.seconds / 86400) / 365.2425
    # print all Outputs of the simulations
    if len(positions) == 0:
        print("zero order")
        return
    print_solution(positions, df_profit_history, df_free_margin_history, df_margin_history,
                   df_equity_history, df_balance_history, total_profit,
                   test_years, simulation, start_date, end_date)

    for symbol in symbols_list:
        if symbols_show[symbol]:
            start = Outputs.index_date_v2(data_shows[symbols_dict[symbol]], start_date)
            end = Outputs.index_date_v2(data_shows[symbols_dict[symbol]], end_date)
            data_shows[symbols_dict[symbol]] = pd.DataFrame(data_shows[symbols_dict[symbol]])
            show_candlestick(symbol + " " + time_frame_show, data_shows[symbols_dict[symbol]].iloc[start:end + 5],
                             positions_df.loc[positions_df['Symbol'] == symbol],
                             df_balance_history, df_equity_history, start, trends, extends)

def run():
    global predicts, positions
    global df_profit_history, df_equity_percent_history, df_free_margin_history
    global df_margin_history, df_equity_history
    global df_balance_history, positions_df, total_profit, wins
    global total, len_data, test_years, difference
    global simulation, data, start_date, end_date, date_format, risk, time_frame_input

    simulation, data, start_date, end_date, date_format, risk, time_frame_input = initialize()
    pd_orders = pd.read_hdf('Simulation/orders.h5', 'df')
    pd_orders['date'] = pd.to_datetime(pd_orders['date'], format=date_format)
    pd_orders = pd_orders.sort_values(['date'])
    predicts = pd_orders.values.tolist()

    adjust_time(time_frame_input)
    if DEBUG:
        print(predicts)
    difference = end_date - start_date
    test_years = (difference.days + difference.seconds / 86400) / 365.2425

    simulate(simulation, predicts, data, start_date, end_date, risk)

    positions = simulation.get_closed_positions()
    len_data = len(data[SYMBOL])
    total_profit, wins, total = simulation.get_total_profit(len_data - 1)

    positions_df = pd.DataFrame(positions,
                                columns=['TimeOpen', 'Type', 'Ticket', 'Volume', 'Symbol', 'OpenPrice', 'S/L', 'T/P'
                                    , 'TimeClose', 'PriceClose', 'Result', 'Profit', 'Profit in pip', 'Index',
                                         'IndexEnd'])
    positions_df = positions_df.sort_values(['TimeOpen'])
    positions_df.to_excel("Simulation/Outputs/history.xlsx", index=False)
    df_balance_history = pd.DataFrame(balance_history, columns=['index', 'x', 'balance'])
    df_equity_history = pd.DataFrame(equity_history, columns=['index', 'x', 'equity'])
    df_margin_history = pd.DataFrame(margin_history, columns=['index', 'x', 'margin'])
    df_free_margin_history = pd.DataFrame(free_margin_history, columns=['index', 'x', 'free margin'])
    df_equity_percent_history = pd.DataFrame(equity_percent_history, columns=['index', 'x', 'equity percent'])
    df_profit_history = pd.DataFrame(profit_history, columns=['index', 'x', 'profit'])

    # print all Outputs of the simulations
    if len(positions) == 0:
        print("zero order")
        return
    print_solution(positions, df_profit_history, df_free_margin_history, df_margin_history,
                   df_equity_history, df_balance_history, total_profit,
                   test_years, simulation, start_date, end_date)

    for symbol in symbols_list:
        if symbols_show[symbol]:
            start = Outputs.index_date_v3(data[symbols_dict[symbol]], start_date)
            end = Outputs.index_date_v3(data[symbols_dict[symbol]], end_date)
            show_candlestick(symbol, data[symbols_dict[symbol]][start:end],
                             positions_df.loc[positions_df['Symbol'] == symbol],
                             df_balance_history, df_equity_history, start)
