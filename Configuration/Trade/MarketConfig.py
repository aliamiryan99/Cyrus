from Market.Market import Market


class MarketConfig:

    market = "Simulator"    # 'Simulator' , 'MetaTrader'

    symbols = ["EURUSD"]
    tag = "RangeRegion EURUSD"

    time_frame = "H1"
    history_size = 1000

    strategies = ['NeuralNetwork', 'SimpleIdea', 'RangeRegion']
    strategy_name = 'RangeRegion'

    def __init__(self, market: Market, symbol, data, strategy_name):

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
        if strategy_name == "RangeRegion":
            from Strategies.RangeRegion import RangeRegion

            range_candle_threshold = 3
            up_timeframe = "D1"
            stop_target_margin = 50

            account_management = 'Risk'
            management_ratio = 1

            self.strategy = RangeRegion(market, data, symbol, range_candle_threshold, up_timeframe, stop_target_margin, account_management, management_ratio)
