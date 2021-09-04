
from Strategies.Strategy import Strategy


class NeuralNetwork(Strategy):

    def __init__(self, market):
        super().__init__(market)

    def on_tick(self):
        pass

    def on_data(self):
        pass
