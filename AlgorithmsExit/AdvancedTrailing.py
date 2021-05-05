from AlgorithmTools.BodyStop import get_body_mean
from AlgorithmTools import LocalExtermums


class AdvTraling:
    def __init__(self, symbol, window, alpha, mode):    # mode is (1,2,3);
        self.mode = mode
        self.symbol = symbol
        self.window = window
        self.alpha = alpha
        self.body_mean_local_min, self.bodymean_local_max = 0, 0
        self.threshold = 0

    def on_data(self, history):
        last_min, last_max = LocalExtermums.get_last_local_extermum(history, 1)
        self.body_mean_local_min, self.bodymean_local_max = get_body_mean(history, last_min, last_max)
        sum = 0
        i, cnt = 1, 0
        while cnt < self.window:
            if history[-i]['Volume'] != 0:
                sum += abs(history[-i]['High'] - history[-i]['Low'])
                cnt += 1
            i += 1
        self.threshold = (sum / self.window) * self.alpha

    def on_tick(self, history, entry_point, position_type, time):
        old_candle = history[-2]
        if old_candle['Volume'] == 0:
            j = 3
            while history[-j]['Volume'] == 0:
                j += 1
            old_candle = history[-j]
        new_candle = history[-1]
        max_price = max(old_candle["Open"], old_candle["Close"])  # it can be replaced by  new_candle['Close']
        min_price = min(old_candle["Open"], old_candle["Close"])  # it can be replaced by  new_candle['Close']
        old_high = max(old_candle['High'], max_price + self.threshold)
        old_low = min(old_candle['Low'], min_price - self.threshold)

        if position_type == "buy":
            if self.mode == 1:
                if new_candle['High'] < old_high:
                    return True, new_candle['Close']
                elif new_candle['Close'] < max_price:
                    return True, new_candle['Close']
            elif self.mode == 2:
                if new_candle["High"] < old_high and new_candle['Low'] < old_low:
                    return True, new_candle['Close']
                elif new_candle['High'] > old_high and new_candle['Close'] < max_price:
                    return True, new_candle['Close']
            elif self.mode == 3:
                if new_candle['High'] > old_high and new_candle['Close'] < max_price:
                    return True, max_price
                elif new_candle['Low'] < old_low:
                    return True, old_low
            elif self.mode == 4:
                if new_candle['High'] > old_high and new_candle['Close'] < max_price:
                    return True, max_price
                elif new_candle['Low'] < min_price:
                    return True, min_price
            elif self.mode == 5:
                if new_candle['High'] > old_high and new_candle['Close'] < max_price:
                    return True, max_price
                elif new_candle['Low'] < old_low:
                    return True, old_low
                elif new_candle['Close'] - new_candle['Open'] >= self.bodymean_local_max:
                    return True, new_candle['Open'] + self.bodymean_local_max
            elif self.mode == 6:
                if new_candle['High'] > old_high and new_candle['Close'] < max_price:
                    return True, max_price
                elif new_candle['Low'] < min_price:
                    return True, min_price
                elif new_candle['Close'] - new_candle['Open'] >= self.bodymean_local_max:
                    return True, new_candle['Open'] + self.bodymean_local_max

        elif position_type == "sell":
            if self.mode == 1:
                if new_candle['Low'] > old_low:
                    return True, new_candle['Close']
                elif new_candle['Close'] > min_price:  # paradox!!!
                    return True, new_candle['Close']
            elif self.mode == 2:
                if new_candle['High'] > old_high and new_candle['Low'] > old_low:
                    return True, new_candle['Close']
                elif new_candle['Low'] > old_low and new_candle['Close'] > min_price:  # paradox!!!
                    return True, new_candle['Close']
            elif self.mode == 3:
                if new_candle['Low'] < old_low and new_candle['Close'] > min_price:
                    return True, min_price
                elif new_candle['High'] > old_high:
                    return True, old_high
            elif self.mode == 4:
                if new_candle['Low'] < old_low and new_candle['Close'] > min_price:
                    return True, min_price
                elif new_candle['High'] > max_price:
                    return True, max_price
            elif self.mode == 5:
                if new_candle['Low'] < old_low and new_candle['Close'] > min_price:
                    return True, min_price
                elif new_candle['High'] > max_price:
                    return True, max_price
                elif new_candle['Close'] - new_candle['Open'] <= - self.body_mean_local_min:
                    return True,  new_candle['Open'] - self.body_mean_local_min
            elif self.mode == 6:
                if new_candle['Low'] < old_low and new_candle['Close'] > min_price:
                    return True, min_price
                elif new_candle['High'] > max_price:
                    return True, max_price
                elif new_candle['Close'] - new_candle['Open'] <= - self.body_mean_local_min:
                    return True,  new_candle['Open'] - self.body_mean_local_min
        return False, 0

    def on_tick_reset(self):
        pass

    def get_first_stop_loss(self, history, position_type):
        old_candle = history[-2]
        if position_type == "buy":
            return abs(old_candle['Low'])
        elif position_type == "sell":
            return abs(old_candle['High'])

