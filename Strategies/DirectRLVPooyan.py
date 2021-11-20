from abc import abstractmethod
from Market.Market import Market
from Strategies.Strategy import Strategy
from collections import deque
import numpy as np
import math


class DirectRLVPooyan(Strategy):

    def __init__(self, market: Market, bid_data, ask_data, symbol, input_shape, weights, bias, feedback_link, data_std):
        self.market = market
        self.bid_data = bid_data
        self.ask_data = ask_data
        self.symbol = symbol
        self.data_std = data_std

        # i/o params
        self.input_shape = input_shape
        self.last_action = 0
        self.short_term_memory = deque(maxlen=self.input_shape)
        self.last_price = 0.0
        self.switch_storage = 0

        # model params
        # To Do
        self.action_regularizer = feedback_link
        self.bias = bias
        self.weights = weights

    @abstractmethod
    def on_tick(self):
        pass

    @abstractmethod
    def on_data(self, bid_candle, ask_candle):
        state, flag = self.observe(bid_candle['Open'])
        if flag:
            signal = self.predict_signal(state)

            if signal == 1:
                if self.last_action == -1:
                    for position in self.market.get_open_sell_positions(self.symbol):
                        self.market.close(position['Ticket'], bid_candle['Open'])
                    # self.market.close_all(self.symbol, bid_candle['Close'])
                if self.last_action != 1:
                    self.market.buy(bid_candle['Open'], self.symbol, 0, 0, 1)
            elif signal == -1:
                if self.last_action == 1:
                    for position in self.market.get_open_buy_positions(self.symbol):
                        self.market.close(position['Ticket'], bid_candle['Open'])
                    # self.market.close_all(self.symbol, bid_candle['Close'])
                if self.last_action != -1:
                    self.market.sell(bid_candle['Open'], self.symbol, 0, 0, 1)
            else:
                for position in self.market.get_open_buy_positions(self.symbol):
                    self.market.close(position['Ticket'], bid_candle['Open'])
                for position in self.market.get_open_sell_positions(self.symbol):
                    self.market.close(position['Ticket'], bid_candle['Open'])

            self.last_action = signal

    def predict_signal(self, state):

        self.dot_product = np.dot(state, self.weights)
        self.feedback_link = self.last_action * self.action_regularizer
        self.current_action = math.tanh(self.dot_product + self.bias + self.feedback_link)

        if self.current_action >= 0.3:
            self.current_action = 1
        elif self.current_action < -0.3:
            self.current_action = -1
        else:
            self.current_action = 0

        return self.current_action

    def store_histoy(self, current_price):

        self.current_price_change = current_price - self.last_price

        if self.switch_storage:

            self.short_term_memory.append(self.current_price_change)

        else:

            self.switch_storage = 1

        self.last_price = current_price

    def observe(self, current_price):

        if len(self.short_term_memory) < self.input_shape - 1:

            self.store_histoy(current_price)
            return None, False

        else:
            self.store_histoy(current_price)
        state = np.asarray(self.short_term_memory, dtype=np.float64)
        state = state / self.data_std
        return state, True

