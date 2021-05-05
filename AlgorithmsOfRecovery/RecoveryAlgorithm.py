

class Recovery:

    def __init__(self, symbol, data, window_size, alpha, alpha_volume):
        self.symbol = symbol
        self.alpha = alpha
        self.alpha_volume = alpha_volume
        self.history = data[-window_size:]
        self.body_mean = {}
        self.position_type = {}
        self.fibo1 = {}
        self.fibo2 = {}
        self.limit_price = {}

    def on_data(self, candle):
        self.history.pop(0)
        self.history.append(candle)

    def on_tick(self, open_positions):
        candle = self.history[-1]
        ticket = open_positions[0]['Ticket']
        if len(open_positions) == 1 and ticket not in self.position_type.keys():
            self.position_type[ticket] = open_positions[0]['Type']
            self.body_mean[ticket] = 0
            for row in self.history:
                self.body_mean[ticket] += abs(row['High'] - row['Low']) * self.alpha / len(self.history)
            self.fibo1[ticket] = 0
            self.fibo2[ticket] = 1
            if self.position_type[ticket] == 'Buy':
                self.limit_price[ticket] = open_positions[0]['OpenPrice'] - (self.fibo1[ticket] + self.fibo2[ticket]) * self.body_mean[ticket]
            if self.position_type[ticket] == 'Sell':
                self.limit_price[ticket] = open_positions[0]['OpenPrice'] + (self.fibo1[ticket] + self.fibo2[ticket]) * self.body_mean[ticket]

        if len(open_positions) > 0:
            if self.position_type[ticket] == 'Buy':
                if candle['Close'] <= self.limit_price[ticket]:
                    price = candle['Close']
                    tp = (open_positions[-1]['OpenPrice']*2 + price)/3 - candle['Close']
                    #volume = open_positions[-1]['Volume'] * 2
                    volume = 0
                    for position in open_positions:
                        volume += position['Volume']
                    volume *= self.alpha_volume
                    # tmp = self.fibo1[ticket]
                    # self.fibo1[ticket] = self.fibo2[ticket]
                    # self.fibo2[ticket] += tmp
                    self.limit_price[ticket] = price - (self.fibo1[ticket] + self.fibo2[ticket]) * self.body_mean[ticket]
                    modify_array = []
                    for position in open_positions:
                        modify_array.append({'Ticket': position['Ticket'], 'TP': tp})
                    return {'Signal': 1, 'Price': price, 'TP': tp, 'Volume': volume}, modify_array
            elif self.position_type[ticket] == 'Sell':
                if candle['Close'] >= self.limit_price[ticket]:
                    price = candle['Close']
                    tp = (open_positions[-1]['OpenPrice']*2 + price)/3 - candle['Close']
                    #volume = open_positions[-1]['Volume'] * 2
                    volume = 0
                    for position in open_positions:
                        volume += position['Volume']
                    volume *= self.alpha_volume
                    # tmp = self.fibo1[ticket]
                    # self.fibo1[ticket] = self.fibo2[ticket]
                    # self.fibo2[ticket] += tmp
                    self.limit_price[ticket] = price + (self.fibo1[ticket] + self.fibo2[ticket]) * self.body_mean[ticket]
                    modify_array = []
                    for position in open_positions:
                        modify_array.append({'Ticket': position['Ticket'], 'TP': tp})
                    return {'Signal': -1, 'Price': price, 'TP': tp, 'Volume': volume}, modify_array
        return {'Signal': 0, 'TP': 0, 'Volume': 0}, []

    def on_tick_reset(self):
        pass

    def tp_touched(self, ticket):
        self.body_mean.pop(ticket)
        self.position_type.pop(ticket)
        self.fibo1.pop(ticket)
        self.fibo2.pop(ticket)
        self.limit_price.pop(ticket)

