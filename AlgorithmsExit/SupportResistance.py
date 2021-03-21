
class SuportResistance:

    def __init__(self, window_size, alpha, beta, threshold_tp, threshold_sl, static_tp, static_sl):
        self.window_size = window_size
        self.alpha = alpha
        self.beta = beta
        self.threshold_tp = threshold_tp
        self.threshold_sl = threshold_sl
        self.static_tp = static_tp
        self.static_sl = static_sl

    def on_data(self, data, position_type):
        tp, sl = 0, 0
        price = data[-1]['Close']
        if position_type == "buy":
            if self.static_tp == 0:
                tp = data[-1]['High'] - price
                for i in range(-1, -self.window_size, -1):
                    tp = max(tp, data[i]['High'] - price)
                tp *= self.alpha
                if abs(tp) < self.threshold_tp:
                    tp = self.threshold_tp
            else:
                tp = self.static_tp
            if self.static_sl == 0:
                sl = data[-1]['Low'] - price
                for i in range(-1, -self.window_size, -1):
                    sl = min(sl, data[i]['Low'] - price)
                sl *= self.beta
                if abs(sl) < self.threshold_sl:
                    sl = -self.threshold_sl
            else:
                sl = -self.static_sl
        elif position_type == "sell":
            if self.static_tp == 0:
                tp = data[-1]['Low'] - price
                for i in range(-1, -self.window_size, -1):
                    tp = min(tp, data[i]['Low'] - price)
                tp *= self.alpha
                if abs(tp) < self.threshold_tp:
                    tp = -self.threshold_tp
            else:
                tp = -self.static_tp
            if self.static_sl == 0:
                sl = data[-1]['High'] - price
                for i in range(-1, -self.window_size, -1):
                    sl = max(sl, data[i]['High'] - price)
                sl *= self.beta
                if abs(sl) < self.threshold_sl:
                    sl = self.threshold_sl
            else:
                sl = self.static_sl
        return tp, sl