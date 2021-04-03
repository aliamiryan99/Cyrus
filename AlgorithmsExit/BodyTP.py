

class BodyTP:
    def __init__(self, window, alpha, mode):
        self.window = window
        self.alpha = alpha
        self.mode = mode    # 1: body, 2: total

    def on_tick(self, data, position_type):    # position_type : (buy or sell)
        sum = 0
        i, cnt = 1, 0
        for i in range(1, self.window+1):
            if self.mode == 1:
                sum += abs(data[-i]['Close'] - data[-i]['Open'])
            elif self.mode == 2:
                sum += data[-i]['High'] - data[-i]['Low']

        tp = (sum / self.window) * self.alpha
        if position_type == 'sell':
            tp *= -1
        max_high = max(data[-2]['High'], data[-3]['High'])
        min_low = min(data[-2]['Low'], data[-3]['Low'])
        sl = 0
        if position_type == 'buy':
            sl = -abs(data[-1]['Close'] - min_low)
        elif position_type == 'sell':
            sl = abs(max_high - data[-1]['Close'])
        return tp, sl

