
import copy

algorithm_list = ['SimpleIdea', 'SimpleIdeaRefinement', 'SimpleIdeaModified', 'Divergence',
                  'NSoldier', 'Doji', 'HighLowBreak', 'SimpleIdeaAndDoji', 'SmiHammer', 'SimpleTrendLineBreak',
                  'MovingAverageCross', 'SuperStrongSupportResistance', 'MonotoneExtremum', 'ExtremumTrendBreak',
                  'RefinementLearning', 'ShadowConfirmation', 'ConditionalDivergence', 'Stochastic',
                  'StrongSimpleIdea', 'HighLowSimpleIdea', 'MinMax', 'Regression', 'SharpPointDetection']
repairment_list = ['ReEntrance']
recovery_list = ['Basic', 'Signal', 'Candle']
close_mode_list = ['tp_sl', 'trailing', 'both']
tp_sl_list = ['Fix', 'Body', 'Extremum', 'Wave']
trailing_list = ['Simple', 'Candle', 'HugeCandle', 'LocalExtremum', 'Stochastic']
account_management_list = ['Balance', 'Risk']


class InstanceConfig:
    # Hyper Parameters
    symbols = ["EURUSD"]
    symbols_ratio = [3, 3, 3]
    history_size = 400
    algorithm_time_frame = "D"
    trailing_time_frame = "D"
    tag = "EURUSD"

    algorithm_name = 'Regression'
    repairment_name = 'ReEntrance'
    recovery_name = 'Signal'
    close_mode = 'tp_sl'
    tp_sl_name = 'Wave'
    trailing_name = 'Simple'
    account_management_name = 'Risk'

    def __init__(self, symbol, data, algorithm_name, repairment_name, recovery_name, close_mode,
                 tp_sl_name, trailing_name, account_management_name, management_ratio):

        # Options
        self.re_entrance_enable = False  # re entrance strategy
        self.recovery_enable = False  # recovery strategy
        self.multi_position = False  # if false only one position with same direction can be placed
        self.algorithm_force_price = False  # if true positions open in algorithm price only (for gaps)
        self.force_close_on_algorithm_price = False  # if true positions only close in algorithm price ( for gaps )
        self.algorithm_virtual_signal = False  # if true algorithm positions don't executed (only re_entrance)
        self.enable_max_trade_per_candle = True  # if true only max_trade_per_candle can be placed on one candle
        self.max_trade_per_candle = 2  # if 1 only 1 trade can be placed for each candle

        # Select Algorithm
        data = copy.deepcopy(data)
        if algorithm_name == 'SimpleIdea':
            from Algorithms.SI import SimpleIdea
            si_win_inc = 2
            si_win_dec = 2
            si_shadow_threshold = 10
            si_body_threshold = 0
            si_mode = 3  # mode 1 : Simlpe , mode 2 : average condition , mode 3 : impulse condition
            si_mean_window = 20
            si_extremum_window = 1
            si_extremum_mode = 2
            si_alpha = 3
            si_impulse_threshold = 1000

            self.algorithm = SimpleIdea(symbol, data, si_win_inc, si_win_dec, si_shadow_threshold,
                                        si_body_threshold, si_mode, si_mean_window,
                                        si_extremum_window, si_extremum_mode, si_alpha,
                                        si_impulse_threshold)
        elif algorithm_name == 'SimpleIdeaRefinement':
            from Algorithms.SIR import SimpleIdeaRefinement
            rsi_win_inc = 1
            rsi_win_dec = 1
            rsi_pivot = 1  # if price mode is 2 then pivot >= 2
            rsi_price_mode = 1  # 1 : High Low , 2 : Top Bottom
            rsi_alpha = 2

            self.algorithm = SimpleIdeaRefinement(symbol, data, rsi_win_inc, rsi_win_dec, rsi_pivot, rsi_price_mode,
                                                  rsi_alpha)
        elif algorithm_name == 'SimpleIdeaModified':
            from Algorithms.SIM import SimpleIdeaModified
            win_inc = 2
            win_dec = 2
            shadow_threshold = 10
            body_threshold = 0
            mode = 3  # mode 1 : Simple , mode 2 : average condition , mode 3 : impulse condition
            mean_window = 20

            self.algorithm = SimpleIdeaModified(symbol, data, win_inc, win_dec, shadow_threshold,
                                                body_threshold, mode, mean_window)
        elif algorithm_name == 'Divergence':
            from Algorithms.Div import Divergence
            big_window = 5
            small_window = 3
            hidden_divergence_check_window = 15
            upper_line_tr = 0.90
            alpha = 20
            extremum_mode = 1

            self.algorithm = Divergence(symbol, data, big_window, small_window, hidden_divergence_check_window,
                                        upper_line_tr, alpha, extremum_mode)
        elif algorithm_name == 'NSoldier':
            from Algorithms.NSld import NSoldier
            window = 3

            self.algorithm = NSoldier(symbol, data, window)
        elif algorithm_name == 'Doji':
            from Algorithms.Doj import Doji
            win = 3
            detect_mode = 3  # 1: HighLow, 2: TopBottom, 3: LastCandle
            candle_mode = 1  # 1: Body, 2: Total

            self.algorithm = Doji(data, win, detect_mode, candle_mode)
        elif algorithm_name == 'HighLowBreak':
            from Algorithms.HLB import HighLowBreak
            window = 1
            pivot = 2

            self.algorithm = HighLowBreak(symbol, data, window, pivot)
        elif algorithm_name == 'SimpleIdeaAndDoji':
            from Algorithms.SIandDoj import SimpleIdeaAndDoji
            si_win_inc = 2
            si_win_dec = 2
            si_shadow_threshold = 10
            si_body_threshold = 0
            doji_win = 3
            doji_detect_mode = 3  # 1: HighLow, 2: TopBottom, 3: LastCandle
            doji_candle_mode = 1  # 1: Body, 2: Total

            self.algorithm = SimpleIdeaAndDoji(symbol, data, si_win_inc, si_win_dec, si_shadow_threshold,
                                               si_body_threshold, doji_win, doji_detect_mode,
                                               doji_candle_mode)
        elif algorithm_name == 'SmiHammer':
            from Algorithms.SH import SemiHammer
            window = 20
            detect_mode = 1
            alpha = 2
            trigger_threshold = 1

            self.algorithm = SemiHammer(data, window, alpha, detect_mode, trigger_threshold)
        elif algorithm_name == 'SimpleTrendLineBreak':
            from Algorithms.STLB import SimpleTrendLineBreak
            window = 100

            self.algorithm = SimpleTrendLineBreak(data, window)
        elif algorithm_name == 'MovingAverageCross':
            from Algorithms.MACros import MovingAverageCross
            total_data_size = 100
            window_size = 14
            price_type = 'Close'
            ma_type = "EMA"
            extremum_window = 2
            extremum_mode = 2  # 1 : High Low , 2 : Top Bottom
            extremum_pivot = 1

            self.algorithm = MovingAverageCross(symbol, data, total_data_size, window_size, price_type, ma_type,
                                                extremum_window, extremum_mode, extremum_pivot)
        elif algorithm_name == 'SuperStrongSupportResistance':
            from Algorithms.SSSR import SuperStrongSupportResistance
            window_size = 150
            extremum_window = 6
            extremum_mode = 1  # 1 : High Low , 2 : Top Bottom

            self.algorithm = SuperStrongSupportResistance(symbol, data, window_size, extremum_window, extremum_mode)
        elif algorithm_name == 'MonotoneExtremum':
            from Algorithms.MonExt import MonotoneExtremum
            window_size = 150
            extremum_window = 4
            extremum_mode = 1  # 1 : High Low , 2 : Top Bottom
            extremum_level = 4
            extremum_pivot = 1
            # monotone_mode 1 : limit price is taken from last extremum price
            # monotone_mode 2 : limit price is taken from last candle
            mode = 1

            self.algorithm = MonotoneExtremum(symbol, data, window_size, extremum_window, extremum_mode,
                                              extremum_level, extremum_pivot, mode)
        elif algorithm_name == 'ExtremumTrendBreak':
            from Algorithms.ExTrBr import ExtremumTrendBreak
            window_size = 150
            extremum_window = 8
            extremum_mode = 1  # 1 : High Low , 2 : Top Bottom
            is_last_candle_check = True

            self.algorithm = ExtremumTrendBreak(symbol, data, window_size, extremum_window, extremum_mode,
                                                is_last_candle_check)
        elif algorithm_name == 'RefinementLearning':
            from Algorithms.RL import RefinementLearning
            self.rl_window_size = 100
            self.algorithm = RefinementLearning(symbol, data, self.rl_window_size)
        elif algorithm_name == 'ShadowConfirmation':
            from Algorithms.ShCon import ShadowConfirmation
            self.sc_window_size = 3
            self.sc_mode = 1  # shadow_confirmation_mode ; 1 : fast_limit , 2 : normal_limit , 3 : late_limit

            self.algorithm = ShadowConfirmation(data, self.sc_window_size, self.sc_mode)
        elif algorithm_name == 'ConditionalDivergence':
            from Algorithms.ConDiv import ConditionalDivergence
            extremum_mode = 1  # High Low
            extremum_window = 1
            resistance_pivot = 1
            price_mode = 1  # High Low , Top Bottom
            trend_window = 2

            self.algorithm = ConditionalDivergence(symbol, data, extremum_mode, extremum_window, resistance_pivot,
                                                   price_mode, trend_window)
        elif algorithm_name == 'Stochastic':
            from Algorithms.Stoch import Stochastic
            upper_band = 0.8
            lower_band = 0.2
            price_mode = 1  # 1 : High, Low, 2 : Top, Bottom
            window = 14

            self.algorithm = Stochastic(symbol, data, upper_band, lower_band, price_mode, window)
        elif algorithm_name == 'StrongSimpleIdea':
            from Algorithms.SSI import StrongSimpleIdea
            win_inc = 3
            win_dec = 3
            shadow_threshold = 10
            body_threshold = 0
            mode = 1  # 1 : standard , 2 : with average condition
            mean_window = 20
            extremum_window = 1
            extremum_mode = 2
            huge_detection_window = 5
            alpha = 0.5
            gap_threshold = 100

            self.algorithm = StrongSimpleIdea(symbol, data, win_inc, win_dec, shadow_threshold, body_threshold, mode,
                                              mean_window, extremum_window, extremum_mode, huge_detection_window,
                                              alpha, gap_threshold)
        elif algorithm_name == 'HighLowSimpleIdea':
            from Algorithms.HLSI import HighLowSimpleIdea
            window = 3
            mode = 2  # mode 1 : On Open , mode 2 : On Open With Shadow Condition

            self.algorithm = HighLowSimpleIdea(symbol, data, window, mode)
        elif algorithm_name == 'MinMax':
            from Algorithms.MinMax import MinMax
            extremum_window = 1
            extremum_mode = 1

            self.algorithm = MinMax(symbol, data, extremum_window, extremum_mode)
        elif algorithm_name == 'Regression':
            from Algorithms.Reg import Regression
            extremum_window = 3
            extremum_mode = 1

            self.algorithm = Regression(data, extremum_window, extremum_mode)
        elif algorithm_name == 'SharpPointDetection':
            from Algorithms.SPD import SharpPointDetection
            mean_alpha = 0.05
            candle_bound = 4

            self.algorithm = SharpPointDetection(data, mean_alpha, candle_bound)

        # ReEntrance Section
        if repairment_name == 'ReEntrance':
            from AlgorithmsOfRepairment.ReEntranceAlgorithm import ReEntrance
            self.force_re_entrance_price = False
            distance_limit = 6
            loss_enable = False
            loss_limit = 2
            loss_threshold = 0  # loss pip threshold

            self.repairment_algorithm = ReEntrance(distance_limit, loss_enable, loss_limit, loss_threshold)

        # Recovery Section
        data = copy.deepcopy(data)
        if recovery_name == 'Basic':
            from AlgorithmsOfRecovery.RecoveryAlgorithm import Recovery
            window_size = 20
            price_alpha = 2
            tp_mode = 1     # 1 : alpha mode, 2 : fix tp mode
            tp_alpha = 0.66  # 0 < x < 1
            fix_tp = 200    # in point
            volume_mode = 3     # 1 : const alpha , 2 : base on pre candle, 3 : base on summation
            volume_alpha = 1.7
            fib_enable = False

            self.recovery_algorithm = Recovery(symbol, data, window_size, price_alpha, tp_mode, tp_alpha, fix_tp,
                                               volume_mode, volume_alpha, fib_enable)
        elif recovery_name == 'Candle':
            from AlgorithmsOfRecovery.CandleRecoveryAlgorithm import CandleRecovery
            window_size = 20
            tp_mode = 2     # 1 : alpha mode, 2 : fix tp mode
            tp_alpha = 0.7  # 0 < x < 1
            fix_tp = 0  # in point
            volume_mode = 3  # 1 : const alpha , 2 : base on pre candle, 3 : base on summation
            volume_alpha = 2

            self.recovery_algorithm = CandleRecovery(symbol, data, window_size, tp_mode, fix_tp, tp_alpha, volume_mode,
                                                     volume_alpha)
        elif recovery_name == 'Signal':
            from AlgorithmsOfRecovery.SignalRecoveryAlgorithm import SignalRecovery
            from Algorithms.HLB import HighLowBreak
            window = 1
            pivot = 2
            s_r_algorithm = HighLowBreak(symbol, data, window, pivot)
            # tp mode : 1 : const TP, 2 : dynamic tp(candle) , 3 : dynamic tp(extremum), 4 : profit tp
            window_size = 50
            volume_alpha = 4
            tp_mode = 1
            const_tp = 450
            price_th = 200

            self.recovery_algorithm = SignalRecovery(symbol, data, window_size, volume_alpha, const_tp,
                                                     price_th, s_r_algorithm, tp_mode)

        # Algorithm Of Exit Section
        data = copy.deepcopy(data)
        self.close_mode = close_mode  # 'tp_sl', 'trailing', 'both'
        if tp_sl_name == 'Fix':
            from AlgorithmsOfExit.TpSl.Fix import Fix
            fix_tp = 450  # it can be disable if value equal to 0 (in point)
            fix_sl = 0  # it can be disable if value equal to 0 (int point)

            self.tp_sl_tool = Fix(symbol, fix_tp, fix_sl)
        elif tp_sl_name == 'Body':
            from AlgorithmsOfExit.TpSl.Body import Body
            window = 30
            alpha = 1
            mode = 1  # 1: body candle, 2: total candle
            tp_disable = False
            sl_disable = True

            self.tp_sl_tool = Body(window, alpha, mode, tp_disable, sl_disable)
        elif tp_sl_name == 'Extremum':
            from AlgorithmsOfExit.TpSl.Extremum import Extremum
            extremum_window = 2
            extremum_mode = 1
            extremum_pivot = 1
            alpha = 1

            self.tp_sl_tool = Extremum(data, symbol, extremum_window, extremum_mode, extremum_pivot, alpha)
        elif tp_sl_name == 'Wave':
            from AlgorithmsOfExit.TpSl.Wave import Wave
            extremum_window = 3
            extremum_mode = 1  # 1 : High Low , 2 : Top Bottom
            alpha = 0.4
            beta = 0.4

            self.tp_sl_tool = Wave(data, extremum_window, extremum_mode, alpha, beta)

        data = copy.deepcopy(data)
        if trailing_name == 'Simple':
            from AlgorithmsOfExit.Trailings.SimpTr import SimpleTrailing
            mode = 3
            window = 10
            alpha = 0.1

            self.trailing_tool = SimpleTrailing(symbol, window, alpha, mode)
        elif trailing_name == 'Candle':
            from AlgorithmsOfExit.Trailings.CndTr import CandleTrailing

            self.trailing_tool = CandleTrailing()
        elif trailing_name == 'HugeCandle':
            from AlgorithmsOfExit.Trailings.HugCanTr import HugeCandleTrailing
            alpha = 0
            beta = 0.8
            mode = 1
            extremum_window = 2
            extremum_mode = 2  # 1 : High Low , 2 : Top Bottom
            extremum_pivot = 4

            self.trailing_tool = HugeCandleTrailing(data, alpha, beta, mode, extremum_window, extremum_mode,
                                                    extremum_pivot)
        elif trailing_name == 'LocalExtremum':
            from AlgorithmsOfExit.Trailings.LExTr import LocalExtremumTrailing
            window = 2
            mode = 1
            pivot = 1

            self.trailing_tool = LocalExtremumTrailing(data, window, mode, pivot)
        elif trailing_name == 'Stochastic':
            from AlgorithmsOfExit.Trailings.StochTr import StochasticTrailing
            upper_band = 0.8
            lower_band = 0.2
            window = 14

            self.trailing_tool = StochasticTrailing(data, upper_band, lower_band, window)

        # # Account Management Section
        # IF Risk : 1% loss per trade if 1 , IF Balance : 0.01 LOT for each 1000 dollar if 1
        self.management_ratio = management_ratio
        if account_management_name == 'Balance':
            from AccountManagment.AccountManagment import BalanceManagement
            self.account_management = BalanceManagement(self.management_ratio)
        elif account_management_name == 'Risk':
            from AccountManagment.AccountManagment import RiskManagement
            self.account_management = RiskManagement(self.management_ratio)
