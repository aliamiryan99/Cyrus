

class StatisticSL:
    def __init__(self, symbol, window, alpha):
        self.symbol = symbol
        self.window = window
        self.alpha = alpha

    def on_tick(self, data, position_type):    # position_type : (buy or sell)
        sum = 0
        i, cnt = 1, 0
        while cnt < self.window:
            if data[-i]['Volume'] != 0:
                sum += data[-i]['High'] - data[-i]['Low']
                cnt += 1
            i += 1
        sl = (sum / self.window) * self.alpha
        if position_type == 'buy':
            sl *= -1
        return 0, sl