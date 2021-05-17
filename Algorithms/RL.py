import numpy as np

from AlgorithmPackages.RLPkg.tradingrrl16 import TradingRRL


class RefinementLearning:

    def __init__(self, symbol, data_history, window_size):
        # Data window, moving average window
        self.window_size = window_size
        len_window = len(data_history)
        if len_window <= self.window_size:
            raise Exception("window len should be greater than window size")
        self.data_window = data_history[-self.window_size-5:]
        self.close = np.array([row['Close'] for row in self.data_window[:-1]])
        self.trading_rrl = TradingRRL()
        self.cash_history = []

    def on_tick(self):
        # call in every tick
        # return signal, price
        return 0, 0

    def on_data(self, candle, cash):
        # this function in open of candles
        # execute algorithm and set signal
        # signal = random.randint(-1,1)
        self.cash_history.append(cash)
        if len(self.cash_history) > self.window_size:
            self.cash_history.pop(0)
        reward = 0
        if len(self.cash_history) > 1:
            reward = self.cash_history[-2] - self.cash_history[-1]

        self.close = self.close[1:]
        self.close = np.append(self.close, [self.data_window[-1]['Close']])
        
        
        self.trading_rrl.set_t_p_r(self.close)
        signal = self.trading_rrl.set_x_F()
        self.R = reward
        self.trading_rrl.fit()


        if signal > 0.7 :
            siganl = 1
        elif signal < -0.7:
            signal = -1
        else:
            signal = 0

        self.data_window.pop(0)
        self.data_window.append(candle)
        return signal, self.data_window[-1]['Open']



