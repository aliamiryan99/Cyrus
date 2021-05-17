
from Simulation.Config import Config


class HighLowSimpleIdea:

    def __init__(self, symbol, data_history, window, mode):
        # Data window, moving average window
        self.window = window
        self.mode = mode
        self.tr = 50 * 10 ** -Config.symbols_pip[symbol]
        len_window = len(data_history)
        if len_window <= self.window:
            raise Exception("window len should be greater than window size")
        self.data_window = data_history
        self.buy_satisfy, self.sell_satisfy = False, False
        self.candle_buy_submitted, self.candle_sell_submitted = False, False

    def on_tick(self):
        if self.mode == 2:
            if self.buy_satisfy and not self.candle_buy_submitted:
                if min(self.data_window[-1]['Close'], self.data_window[-1]['Open']) - self.data_window[-1]['Low'] > max(self.data_window[-2]['High'] - max(self.data_window[-2]['Open'], self.data_window[-2]['Close']),  min(self.data_window[-2]['Open'], self.data_window[-2]['Close']) - self.data_window[-2]['Low']):
                    if self.data_window[-1]['High'] - self.data_window[-1]['Close'] < self.tr:
                        #if abs(self.data_window[-1]['Close'] - self.data_window[-1]['Open']) <= self.tr:
                        if self.data_window[-1]['Close'] > self.data_window[-1]['Open']:
                            self.candle_buy_submitted = True
                            return 1, self.data_window[-1]['Open']
            elif self.sell_satisfy and not self.candle_sell_submitted:
                if self.data_window[-1]['High'] - max(self.data_window[-1]['Close'], self.data_window[-1]['Open']) > max(self.data_window[-2]['High'] - max(self.data_window[-2]['Open'], self.data_window[-2]['Close']), min(self.data_window[-2]['Open'], self.data_window[-2]['Close']) - self.data_window[-2]['Low']):
                    if self.data_window[-1]['Close'] - self.data_window[-1]['Low'] < self.tr:
                        #if abs(self.data_window[-1]['Close'] - self.data_window[-1]['Open']) <= self.tr:
                        if self.data_window[-1]['Close'] < self.data_window[-1]['Open']:
                            self.candle_sell_submitted = True
                            return -1, self.data_window[-1]['Open']
        return 0, 0

    def on_data(self, candle, cash):
        self.candle_buy_submitted, self.candle_sell_submitted = False, False
        self.buy_satisfy, self.sell_satisfy = self.check_satisfaction()
        signal = 0
        if self.mode == 1:
            if self.buy_satisfy:
                signal = 1
            elif self.sell_satisfy:
                signal = -1
        self.data_window.pop(0)
        self.data_window.append(candle)
        return signal, self.data_window[-1]['Open']

    def check_satisfaction(self):
        buy_satisfy = True
        if self.data_window[-1]['High'] < self.data_window[-2]['High']:
            buy_satisfy = False
        for i in range(2, self.window+2):
            if self.data_window[-i]['High'] > self.data_window[-i-1]['High']:
                buy_satisfy = False
        sell_satisfy = True
        if self.data_window[-1]['Low'] > self.data_window[-2]['Low']:
            sell_satisfy = False
        for i in range(2, self.window + 2):
            if self.data_window[-i]['Low'] < self.data_window[-i-1]['Low']:
                sell_satisfy = False

        return buy_satisfy, sell_satisfy

