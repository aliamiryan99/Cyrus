
from AlgorithmsOfRecovery import Tools
from Shared.Variables import Variables


class Recovery:

    def __init__(self, symbol, data, window_size, price_alpha, tp_mode, tp_alpha, fix_tp, volume_mode, volume_alpha,
                 fib_enable):
        self.symbol = symbol
        self.price_alpha = price_alpha
        self.tp_mode = tp_mode
        self.tp_alpha = tp_alpha
        self.fix_tp = fix_tp * 10 ** -Variables.config.symbols_pip[symbol]
        self.volume_mode = volume_mode
        self.volume_alpha = volume_alpha
        self.fib_enable = fib_enable
        self.history = data[-window_size:]

        self.body_mean = {}
        self.position_type = {}
        self.fib1 = {}
        self.fib2 = {}
        self.limit_price = {}

    def on_data(self, candle):
        self.history.pop(0)
        self.history.append(candle)

    def on_tick(self, open_positions):
        candle = self.history[-1]
        ticket = open_positions[0]['Ticket']
        if ticket not in self.position_type.keys():
            self.new_position(open_positions, ticket)

        signal = self.detect_pattern(ticket, candle)
        if signal == 1:
            price, tp, volume, modify_list = self.get_tp_volume(open_positions, ticket)
            return {'Signal': 1, 'Price': price, 'TP': tp, 'Volume': volume}, modify_list
        elif signal == -1:
            price, tp, volume, modify_list = self.get_tp_volume(open_positions, ticket)
            return {'Signal': -1, 'Price': price, 'TP': tp, 'Volume': volume}, modify_list
        return {'Signal': 0, 'TP': 0, 'Volume': 0}, []

    def on_tick_end(self):
        pass

    def tp_touched(self, ticket):
        self.body_mean.pop(ticket)
        self.position_type.pop(ticket)
        self.fib1.pop(ticket)
        self.fib2.pop(ticket)
        self.limit_price.pop(ticket)

    def new_position(self, open_positions, ticket):
        self.position_type[ticket] = open_positions[0]['Type']
        self.body_mean[ticket] = 0
        for row in self.history:
            self.body_mean[ticket] += abs(row['High'] - row['Low']) * self.price_alpha / len(self.history)
        self.fib1[ticket] = 0
        self.fib2[ticket] = 1
        if self.position_type[ticket] == 'Buy':
            self.limit_price[ticket] = open_positions[0]['OpenPrice'] - (self.fib1[ticket] + self.fib2[ticket]) * \
                                       self.body_mean[ticket]
        if self.position_type[ticket] == 'Sell':
            self.limit_price[ticket] = open_positions[0]['OpenPrice'] + (self.fib1[ticket] + self.fib2[ticket]) * \
                                       self.body_mean[ticket]

    def detect_pattern(self, ticket, candle):
        if self.position_type[ticket] == 'Buy':
            if candle['Close'] <= self.limit_price[ticket]:
                return 1
        elif self.position_type[ticket] == 'Sell':
            if candle['Close'] >= self.limit_price[ticket]:
                return -1
        return 0

    def get_tp_volume(self, open_positions, ticket):
        price = self.history[-1]['Close']

        volume = Tools.calc_volume(open_positions, self.volume_mode, self.volume_alpha, self.fix_tp, self.history)

        tp = Tools.calc_tp(open_positions, price, volume, self.tp_mode, self.tp_alpha, self.fix_tp)
        if self.position_type[ticket] == 'Sell':
            tp *= -1

        if self.fib_enable:
            tmp = self.fib1[ticket]
            self.fib1[ticket] = self.fib2[ticket]
            self.fib2[ticket] += tmp
        if self.position_type[ticket] == 'Buy':
            self.limit_price[ticket] = price - (self.fib1[ticket] + self.fib2[ticket]) * self.body_mean[ticket]
        elif self.position_type[ticket] == 'Sell':
            self.limit_price[ticket] = price + (self.fib1[ticket] + self.fib2[ticket]) * self.body_mean[ticket]

        modify_list = []
        for position in open_positions:
            modify_list.append({'Ticket': position['Ticket'], 'TP': tp})

        return price, tp, volume, modify_list
