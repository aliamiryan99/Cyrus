

class ReEntrance:
    def __init__(self, candles_limit, loss_enable, loss_limit_cnt, loss_threshold):
        self.candles_limit = candles_limit
        self.loss_enable = loss_enable
        self.loss_limit = loss_limit_cnt
        self.loss_threshold = loss_threshold
        self.candles_from_last_position_buy_cnt = 0
        self.buy_loss_cnt = 0
        self.sell_loss_cnt = 0
        self.buy_position_trigger = 0
        self.candles_from_last_position_sell_cnt = 0
        self.sell_position_trigger = 0
        self.limit_price_buy = 0
        self.limit_price_sell = 0
        self.algorithm_history = []

    def on_tick(self, algorithm_history, is_buy_close, is_sell_close, profit_in_pip, start_index_buy, start_index_sell, end_index):
        self.algorithm_history = algorithm_history
        if is_buy_close:
            self.buy_position_trigger = 1
            self.candles_from_last_position_buy_cnt = 0
            a = algorithm_history[start_index_buy]['High']
            for i in range(start_index_buy+1, end_index+1):
                a = max(a, algorithm_history[i]['High'])
            self.limit_price_buy = a
            if self.loss_enable:
                if profit_in_pip < -self.loss_threshold:
                    self.buy_loss_cnt += 1
                else:
                    self.buy_loss_cnt = 0
                if self.buy_loss_cnt == self.loss_limit:
                    self.buy_position_trigger = 0
                    self.buy_loss_cnt = 0
        if is_sell_close:
            self.sell_position_trigger = 1
            self.candles_from_last_position_sell_cnt = 0
            b = algorithm_history[start_index_sell]['Low']
            for i in range(start_index_sell + 1, end_index + 1):
                b = min(b, algorithm_history[i]['Low'])
            self.limit_price_sell = b
            if self.loss_enable:
                if profit_in_pip < -self.loss_threshold:
                    self.sell_loss_cnt += 1
                else:
                    self.sell_loss_cnt = 0
                if self.sell_loss_cnt == self.loss_limit:
                    self.sell_position_trigger = 0
                    self.sell_loss_cnt = 0

        if self.candles_from_last_position_buy_cnt > self.candles_limit:
            self.buy_position_trigger = 0
            self.candles_from_last_position_buy_cnt = 0

        if self.candles_from_last_position_sell_cnt > self.candles_limit:
            self.sell_position_trigger = 0
            self.candles_from_last_position_sell_cnt = 0

        if self.buy_position_trigger == 1 and not is_buy_close:
            if algorithm_history[-1]['High'] > self.limit_price_buy:
                return 1, self.limit_price_buy

        if self.sell_position_trigger == 1 and not is_sell_close:
            if algorithm_history[-1]['Low'] < self.limit_price_sell:
                return -1, self.limit_price_sell

        return 0, 0

    def on_data(self):
        if self.buy_position_trigger == 1:
            if self.algorithm_history[-2]['High'] > self.limit_price_buy:
                self.limit_price_buy = self.algorithm_history[-2]['High']        # correct : -2 , instead: -1
            self.candles_from_last_position_buy_cnt += 1
        if self.sell_position_trigger == 1:
            if self.algorithm_history[-2]['Low'] < self.limit_price_sell:
                self.limit_price_sell = self.algorithm_history[-2]['Low']       # correct : -2 , instead: -1
            self.candles_from_last_position_sell_cnt += 1

    def reset_triggers(self, position_type):
        if position_type == 'buy':
            self.buy_position_trigger = 0
            self.candles_from_last_position_buy_cnt = 0
        if position_type == 'sell':
            self.sell_position_trigger = 0
            self.candles_from_last_position_sell_cnt = 0
