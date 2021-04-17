
from Algorithms.ShadowConfirmation import ShadowConfirmation


class ShadowConfirmationAlgorithm:

    def __init__(self, data_history, window_size, shadow_confirmation_mode):        # shadow_confirmation_mode ; 1 : fast_limit , 2 : normal_limit , 3 : late_limit
        # Data window, moving average window
        self.window_size = window_size
        len_window = len(data_history)
        self.shadow_confirmation_mode = shadow_confirmation_mode
        if len_window <= self.window_size:
            raise Exception("window len should be greater than window size")
        self.data_window = data_history[-self.window_size-5:]
        self.signal_trigger = 0

    def on_tick(self):
        if self.signal_trigger == 1:
            if self.data_window[-1]['Low'] < self.data_window[-2]['Low']:
                limit_price = 0
                if self.shadow_confirmation_mode == 1:
                    limit_price = min(self.data_window[-2]['Open'], self.data_window[-2]['Close'])
                elif self.shadow_confirmation_mode == 2:
                    limit_price = max(self.data_window[-2]['Open'], self.data_window[-2]['Close'])
                elif self.shadow_confirmation_mode == 3:
                    limit_price = self.data_window[-2]['High']
                if self.data_window[-1]['Close'] >= limit_price:
                    return 1, limit_price
        elif self.signal_trigger == -1:
            limit_price = 0
            if self.shadow_confirmation_mode == 1:
                limit_price = max(self.data_window[-2]['Open'], self.data_window[-2]['Close'])
            elif self.shadow_confirmation_mode == 2:
                limit_price = min(self.data_window[-2]['Open'], self.data_window[-2]['Close'])
            elif self.shadow_confirmation_mode == 3:
                limit_price = self.data_window[-2]['Low']
            if self.data_window[-1]['High'] > self.data_window[-2]['High']:
                if self.data_window[-1]['Close'] <= limit_price:
                    return -1, limit_price
        return 0, 0

    def on_data(self, candle, cash):
        self.signal_trigger = ShadowConfirmation.pattern_detect(self.data_window, self.window_size)
        self.data_window.pop(0)
        self.data_window.append(candle)
        return 0, 0



