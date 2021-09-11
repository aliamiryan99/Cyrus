from Market.Market import Market


class MarketConfig:

    market = "Simulator"    # 'Simulator' , 'MetaTrader'

    symbols = ["EURUSD"]

    time_frame = "M30"
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
            doji_win = 3
            doji_detect_mode = 3  # 1: HighLow, 2: TopBottom, 3: LastCandle
            doji_candle_mode = 1  # 1: Body, 2: Total

            self.strategy = SimpleIdea(market, data, symbol, si_win_inc, si_win_dec, si_shadow_threshold,
                                               si_body_threshold, doji_win, doji_detect_mode,
                                               doji_candle_mode)