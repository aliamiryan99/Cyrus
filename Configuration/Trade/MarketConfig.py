from Market.Market import Market


class MarketConfig:

    market = "Simulator"    # 'Simulator' , 'MetaTrader'

    symbols = ["EURUSD"]

    time_frame = "D"
    history_size = 200

    strategies = ['NeuralNetwork', 'SimpleIdea']
    strategy_name = 'SimpleIdea'

    def __init__(self, market:Market, symbol, data, strategy_name):

        if strategy_name == "NeuralNetwork":
            from Strategies.NeuralNetwork import NeuralNetwork

            self.strategy = NeuralNetwork(market, data)
        if strategy_name == "SimpleIdea":
            from Strategies.SimpleIdea import SimpleIdea

            si_win_inc = 2
            si_win_dec = 2
            si_shadow_threshold = 10
            si_body_threshold = 0
            si_mode = 1  # mode 1 : simple , mode 2 : average condition , mode 3 : impulse condition
            si_mean_window = 20
            si_extremum_window = 1
            si_extremum_mode = 2
            si_alpha = 3
            si_impulse_threshold = 1000

            self.strategy = SimpleIdea(market, data, symbol, si_win_inc, si_win_dec, si_shadow_threshold,
                                        si_body_threshold, si_mode, si_mean_window,
                                        si_extremum_window, si_extremum_mode, si_alpha,
                                        si_impulse_threshold)