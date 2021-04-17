

class Recovery:

    def __init__(self, symbol, data, window_size, alpha):
        self.symbol = symbol
        self.alpha = alpha
        self.history = data[-window_size:]
        self.body_mean = 0
        self.last_open_position = None
        self.last_open_position_type = None
        self.fibo1 = 1
        self.fibo2 = 1
        self.limit_price = 0

    def on_data(self, candle):
        self.history.pop(0)
        self.history.append(candle)

    def on_tick(self, candle, open_positions):
        if len(open_positions) == 1:
            self.new_position_type = open_positions[0]['Type']
            self.body_mean = 0
            for row in self.history:
                self.body_mean += abs(row['Close'] - row['Open']) / len(self.history)
            self.fibo1 = 1
            self.fibo2 = 1
            if self.new_position_type == 'buy':
                self.limit_price = open_positions[0]['OpenPrice'] - (self.fibo1 + self.fibo2) * self.body_mean
            if self.new_position_type == 'sell':
                self.limit_price = open_positions[0]['OpenPrice'] + (self.fibo1 + self.fibo2) * self.body_mean

        if len(open_positions) > 0:
            if self.last_open_position_type == 'buy':
                if candle['Close'] <= self.limit_price:
                    pass
            elif self.last_open_position_type == 'sell':
                pass



