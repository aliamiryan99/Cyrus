from Market.Market import Market

import copy


class MarketConfig:

    market = "Simulator"    # 'Simulator' , 'MetaTrader'

    symbols = ["EURUSD"]
    tag = "EURUSD"

    time_frame = "M30"
    history_size = 200

    strategies = ['NeuralNetwork', 'SimpleIdea', 'RangeRegion', 'DirectRLVPooyan']
    strategy_name = 'DirectRLVPooyan'

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
            type2_enable = True
            one_stop_in_region = False
            ma_filter_enable = True
            ma_type = "SMA"
            ma_period = 200

            account_management = 'Risk'
            management_ratio = 1

            risk_free_enable = False
            risk_free_price_percent = 100
            risk_free_volume_percent = 50

            if params is not None:
                range_candle_threshold = params['RangeCandleThreshold']
                up_timeframe = params['UpTimeFrame']
                stop_target_margin = params['StopTargetMargin']
                candle_breakout_threshold = params['CandlesBreakoutThreshold']
                max_candles = params['MaxCandles']
                type1_enable = params['Type1Enable']
                type2_enable = params['Type2Enable']
                one_stop_in_region = params['OneStopInRegion']
                ma_filter_enable = params['MaFilterEnable']
                ma_type = params['MaType']
                ma_period = params['MaPeriod']

                account_management = params['AccountManagement']
                management_ratio = params['ManagementRatio']
                risk_free_enable = params['RiskFreeEnable']
                risk_free_price_percent = params['RiskFreePricePercent']
                risk_free_volume_percent = params['RiskFreeVolumePercent']

            self.strategy = RangeRegion(market, bid_data, ask_data, symbol, range_candle_threshold, up_timeframe, stop_target_margin,
                                        type1_enable, type2_enable, one_stop_in_region, candle_breakout_threshold,
                                        max_candles, ma_filter_enable, ma_period, ma_type, account_management,
                                        management_ratio, risk_free_enable, risk_free_price_percent,
                                        risk_free_volume_percent)
        if strategy_name == "DirectRLVPooyan":
            from Strategies.DirectRLVPooyan import DirectRLVPooyan

            input_shape = 8
            weights = [0.009222261, -0.014876936, -0.011727244, 0.016797503, -0.026659025, -0.015411552, -0.001764283, 0.037169577]
            # [-0.022754631, -0.012325789, -0.044426516, 0.022545825, 0.055269639, -0.027307641, -0.061036172, 0.120108635]
            bias = -0.004313122
            feedback_link = -0.000135494
            data_std = 0.000591

            self.strategy = DirectRLVPooyan(market, bid_data, ask_data, symbol, input_shape, weights, bias, feedback_link, data_std)
