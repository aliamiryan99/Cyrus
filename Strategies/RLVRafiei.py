
from Strategies.Strategy import Strategy

from AlgorithmFactory.AlgorithmTools.CandleTools import *


class RLVRafiei(Strategy):

    def __init__(self, market, bid_data, ask_data, symbol, num_of_parameters=10, learn_speed=0.01, L2_weight=0.000002, thres=0.5, lots=0.01, coms=5,
                 coef=0.01, pre_A=-0.02, pre_B=0.5, prep=0, dreturn=0):
        super().__init__(market, bid_data, ask_data)
        self.symbol = symbol
        self.num_of_parameters = num_of_parameters
        self.weight = 0.001 * np.sort(np.abs(np.random.normal(0.1, 1, (self.num_of_parameters))))
        self.weight[-1] = 1
        self.learn_speed = learn_speed
        self.L2_weight = L2_weight
        self.dfw = np.zeros(self.num_of_parameters)
        self.thres = thres
        self.lots = lots
        self.coms = coms
        self.coef = coef
        self.pre_A = pre_A
        self.pre_B = pre_B
        self.prep = prep
        self.prepos = self.prep
        self.pre_dfw = self.dfw
        self.dreturn = dreturn

    def on_tick(self):
        pass

    def on_data(self, bid_candle, ask_candle):
        self.bid_data.pop(0)

        open, high, low, close = get_ohlc(self.bid_data)
        self.get_data(close)

        self.position()

        pos = self.position()

        if pos == 1:
            if self.pre_pos == -1:
                for position in self.market.get_open_sell_positions(self.symbol):
                    self.market.close(position['Ticket'], bid_candle['Open'])
                # self.market.close_all(self.symbol, bid_candle['Close'])
            if self.pre_pos != 1:
                self.market.buy(bid_candle['Open'], self.symbol, 0, 0, 0.1)
        elif pos == -1:
            if self.pre_pos == 1:
                for position in self.market.get_open_buy_positions(self.symbol):
                    self.market.close(position['Ticket'], bid_candle['Open'])
                # self.market.close_all(self.symbol, bid_candle['Close'])
            if self.pre_pos != -1:
                self.market.sell(bid_candle['Open'], self.symbol, 0, 0, 0.1)
        else:
            for position in self.market.get_open_buy_positions(self.symbol):
                self.market.close(position['Ticket'], bid_candle['Open'])
            for position in self.market.get_open_sell_positions(self.symbol):
                self.market.close(position['Ticket'], bid_candle['Open'])

        self.update_weights()

        self.pre_pos = pos
        self.pre_A = self.A
        self.pre_B = self.B

        self.bid_data.append(bid_candle)

    def get_data(self, price):
        self.pips = 10000 * np.diff(price[-self.num_of_parameters + 1:])

    def position(self):
        self.posvec = self.pips
        self.posvec = np.append(1, self.posvec)
        self.posvec = np.append(self.posvec, self.prepos)
        self.raw_pos = np.tanh(self.posvec.dot(self.weight))
        if abs(self.raw_pos) <= self.thres:
            self.pos = 0
        else:
            self.pos = np.sign(self.raw_pos)

        return self.pos

    def daily_return(self):
        self.dreturn = self.lots * (10 * self.prepos * self.pips[-1] - self.coms * abs(self.pos - self.prepos))

    def ma_sharpe(self):
        self.A = self.pre_A + self.coef * (self.dreturn - self.pre_A)
        self.B = self.pre_B + self.coef * (self.dreturn ** 2 - self.pre_B)

    def diffs(self):
        self.dDt_dRt = 0 if (self.pre_B - self.pre_A ** 2) == 0 else (self.pre_B - self.pre_A * self.dreturn) / (
                self.pre_B - self.pre_A ** 2) ** (1.5)
        self.dRt_dFt = -self.coms * self.lots * np.sign(self.pos - self.prepos)
        self.dRt_dFtpre = self.coms * self.lots * np.sign(self.pos - self.prepos) + self.lots * self.pips[-1] * 10
        self.dfw = (1 - np.tanh(self.weight.dot(self.posvec)) ** 2) * (self.posvec + self.weight[-1] * self.pre_dfw)
        self.dUt_dWt = self.dDt_dRt * (self.dRt_dFt * self.dfw + self.dRt_dFtpre * self.pre_dfw) * self.coef

        self.pre_dfw = self.dfw

    def update_weights(self):
        self.daily_return()
        self.diffs()
        self.ma_sharpe()
        self.weight = self.weight + self.learn_speed * self.dUt_dWt - self.L2_weight * self.weight
