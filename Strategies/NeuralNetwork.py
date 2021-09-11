
from Strategies.Strategy import Strategy


class NeuralNetwork(Strategy):

    def __init__(self, market, data):
        super().__init__(market, data)

    def on_tick(self):
        pass

    def on_data(self, candle):
        pass
