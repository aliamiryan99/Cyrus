

class Body:
    def __init__(self, window, alpha, candle_mode, tp_disable, sl_disable):
        self.window = window
        self.alpha = alpha
        self.tp_disable, self.sl_disable = tp_disable, sl_disable
        self.candle_mode = candle_mode    # 1: body, 2: total

    def on_data(self, candle):
        pass

    def on_tick(self, data, position_type):    # position_type : (buy or sell)
        sum = 0
        for i in range(2, self.window+2):
            if self.candle_mode == 1:
                sum += abs(data[-i]['Close'] - data[-i]['Open'])
            elif self.candle_mode == 2:
                sum += data[-i]['High'] - data[-i]['Low']

        tp = (sum / self.window) * self.alpha
        if position_type == 'Sell':
            tp *= -1
        sl = -tp
        if self.tp_disable:
            tp = 0
        if self.sl_disable:
            sl = 0
        return tp, sl

