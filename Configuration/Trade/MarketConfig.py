from Market.Market import Market


class MarketConfig:

    market = "Simulator"    # 'Simulator' , 'MetaTrader'

    symbols = ["EURUSD"]

    time_frame = "M30"
    history_size = 200

    strategies = ['NeuralNetwork']
    strategy = 'NeuralNetwork'

    def __init__(self, market:Market, strategy_name):

        if strategy_name == "NeuralNetwork":
            from Strategies.NeuralNetwork import NeuralNetwork

            self.strategy = NeuralNetwork(market)
