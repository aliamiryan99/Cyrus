
from Strategies.Strategy import Strategy
from Shared.Variables import Variables

from AlgorithmFactory.AlgorithmTools.Elliott import elliott

import pandas as pd


class Elliott(Strategy):

    def __init__(self, market, bid_data, ask_data, symbol, wave4_enable, wave5_enable, inside_flat_zigzag_wc, post_prediction_enable, price_type, candle_time_frame, neo_time_frame):
        super().__init__(market, bid_data, ask_data)
        self.symbol = symbol

        self.wave4_enable = wave4_enable
        self.wave5_enable = wave5_enable
        self.inside_flat_zigzag_wc = inside_flat_zigzag_wc
        self.post_prediction_enable = post_prediction_enable

        self.price_type = price_type

        self.candle_time_frame = candle_time_frame
        self.neo_time_frame = neo_time_frame

        monowave_list, polywave_list, post_prediction_list, In_impulse_prediction_list_w4, In_impulse_prediction_list_w5, In_zigzag_flat_prediction_list = \
            elliott.calculate(pd.DataFrame(bid_data), self.wave4_enable, self.wave5_enable, self.inside_flat_zigzag_wc,
                              self.post_prediction_enable, price_type=self.price_type,
                              candle_timeframe=candle_time_frame, neo_timeframe=neo_time_frame)

        if self.wave4_enable:
            self.last_prediction_w4_time = self.bid_data[In_impulse_prediction_list_w4[0]['X1'][-1]]['Time']
            self.last_prediction_w4_index = In_impulse_prediction_list_w4[0]['X1'][-1]

    def on_tick(self):
        pass

    def on_data(self, bid_candle, ask_candle):
        self.bid_data.pop(0)

        monowave_list, polywave_list, post_prediction_list, In_impulse_prediction_list_w4, \
        In_impulse_prediction_list_w5, In_zigzag_flat_prediction_list = elliott.calculate(
            pd.DataFrame(self.bid_data),
            self.wave4_enable,
            self.wave5_enable,
            self.inside_flat_zigzag_wc,
            self.post_prediction_enable,
            price_type=self.price_type,
            candle_timeframe=self.candle_time_frame,
            neo_timeframe=self.neo_time_frame)

        if self.wave4_enable:
            if len(In_impulse_prediction_list_w4) != 0:
                if self.bid_data[In_impulse_prediction_list_w4[0]['X1'][-1]]['Time'] > self.last_prediction_w4_time:
                    self.last_prediction_w4_index += 1
                    self.last_prediction_w4_time = self.bid_data[In_impulse_prediction_list_w4[0]['X1'][-1]]['Time']

                    if In_impulse_prediction_list_w4[0]['Y1'][0][0][0] != 'none':
                        if self.bid_data[-1]['Close'] < In_impulse_prediction_list_w4[0]['Y1'][0][0][0]:
                            tp = abs(In_impulse_prediction_list_w4[0]['Y1'][0][0][0] - self.bid_data[-1]['Close']) * 10 ** Variables.config.symbols_pip[self.symbol]
                            sl = 400
                            self.market.buy(self.bid_data[-1]['Close'], self.symbol, tp, sl, 0.1)
                        elif self.bid_data[-1]['Close'] > In_impulse_prediction_list_w4[0]['Y1'][0][0][0]:
                            tp = abs(In_impulse_prediction_list_w4[0]['Y1'][0][0][0] - self.bid_data[-1]['Close']) * 10 ** \
                            Variables.config.symbols_pip[self.symbol]
                            sl = 400
                            self.market.sell(self.bid_data[-1]['Close'], self.symbol, tp, sl, 0.1)




        self.bid_data.append(bid_candle)
