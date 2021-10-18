
from Strategies.Strategy import Strategy


class NeuralNetwork(Strategy):

    def __init__(self, market, bid_data, ask_data):
        super().__init__(market, bid_data, ask_data)

    def on_tick(self):
        pass

    def on_data(self, bid_candle, ask_candle):
        pass
