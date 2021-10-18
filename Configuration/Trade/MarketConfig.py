from Market.Market import Market

import copy

class MarketConfig:

    market = "MetaTrader"    # 'Simulator' , 'MetaTrader'

    symbols = ["EURUSD.I"]
    tag = "RangeRegion"

    time_frame = "M1"
    history_size = 1000

    strategies = ['NeuralNetwork', 'SimpleIdea', 'RangeRegion']
    strategy_name = 'SimpleIdea'

    def __init__(self, market: Market, symbol, bid_data, ask_data, strategy_name, params=None):

        bid_data = copy.deepcopy(bid_data)
        ask_data = copy.deepcopy(ask_data)

        if strategy_name == "NeuralNetwork":
            from Strategies.NeuralNetwork import NeuralNetwork

            self.strategy = NeuralNetwork(market, bid_data, ask_data)
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

            self.strategy = SimpleIdea(market, bid_data, ask_data, symbol, si_win_inc, si_win_dec, si_shadow_threshold,
                                        si_body_threshold, si_mode, si_mean_window,
                                        si_extremum_window, si_extremum_mode, si_alpha,
                                        si_impulse_threshold)
        if strategy_name == "RangeRegion":
            from Strategies.RangeRegion import RangeRegion

            range_candle_threshold = 3
            up_timeframe = "D1"
            stop_target_margin = 50
            candle_breakout_threshold = 1
            max_candles = 1000

            type1_enable = True
            type2_enable = False

            one_stop_in_region = True

            account_management = 'Fix'
            management_ratio = 1

            risk_free_enable = True
            risk_free_price_percent = 100
            risk_free_volume_percent = 50

            if params is not None:
                range_candle_threshold = params['RangeCandleThreshold']
                up_timeframe = params['UpTimeFrame']
                stop_target_margin = params['StopTargetMargin']
                type1_enable = params['Type1Enable']
                type2_enable = params['Type2Enable']
                one_stop_in_region = params['OneStopInRegion']

                account_management = params['AccountManagement']
                management_ratio = params['ManagementRatio']
                risk_free_enable = params['RiskFreeEnable']
                risk_free_price_percent = params['RiskFreePricePercent']
                risk_free_volume_percent = params['RiskFreeVolumePercent']

            self.strategy = RangeRegion(market, bid_data, ask_data, symbol, range_candle_threshold, up_timeframe, stop_target_margin,
                                        type1_enable, type2_enable, one_stop_in_region, candle_breakout_threshold,
                                        max_candles, account_management, management_ratio, risk_free_enable,
                                        risk_free_price_percent, risk_free_volume_percent)
