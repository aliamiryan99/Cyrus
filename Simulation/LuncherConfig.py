from Algorithms.SimpleIdeaAlgorithm import SIAlgorithm
from Algorithms.RefinementSiAlgorithm import RSIAlgorithm
from Algorithms.DiveregenceAlgorithms import DivergenceAlgorithm
from AlgorithmsRepairment.ReEntranceAlgorithm import ReEntrance
from AlgorithmsExit.AdvancedTrailing import AdvTraling
from AlgorithmsExit.WaveTPSL import WaveTPSL
from AlgorithmsExit.StatisticSL import StatisticSL
from AccountManagment import AccountManagment

class LauncherConfig:
    # Hyper Parameters
    categories = ["CFD", "Metal", "CFD"]
    symbols = ["US30USD"]
    symbols_ratio = [3, 3, 3]
    history_size = 200
    algorithm_time_frame = "D"
    trailing_time_frame = "H12"
    algorithm_name = "SI&ReEntrance"
    tag = "US30USD"

    def __init__(self, symbol, data, start_i, balance_ratio):
        # # Algorithms
        # Simple Idea
        self.si_win_inc = 2
        self.si_win_dec = 2
        self.si_shadow_threshold = 10
        self.si_body_threshold = 0
        # Refinement Simple Idea
        self.rsi_win_inc = 2
        self.rsi_win_dec = 2
        self.rsi_pivot = 2
        # Min Max Trend
        self.min_max_window_exteremum = 1
        self.min_max_window_trend = 1
        self.min_max_mode_trend = 'Last'
        # Regression Line
        self.reg_alpha = 1
        self.reg_beta = 1
        self.reg_window_exteremum = 3
        # Divergence
        self.big_window = 5
        self.small_window = 3
        self.hidden_divergence_check_window = 25
        self.upper_line_tr = 0.90
        self.divergence_alpha = 4
        # # Exit Algorithms
        # Advance Trailing Stop
        self.adv_mode = 3
        self.adv_window = 10
        self.adv_alpha = 0.1
        # Fix TP SL
        self.fix_tp = 0  # it can be disable if value equal to 0 (in point)
        self.fix_sl = 0  # it can be disable if value equal to 0 (int point)
        # Statistic SL
        self.statistic_sl_window = 10  # it can be disable if value equal to 0 (in point)
        self.statistic_sl_alpha = 0.8  # it can be disable if value equal to 0 (int point)
        # Wave TP SL
        self.wave_win_tp_sl = 3
        self.wave_alpha = 0.3
        self.wave_beta = 0.6
        # # Re Entrance
        self.re_entrance_enable = True  # if true the re entrance algorithm will execute
        self.enable_max_trade_per_candle = True  # if true only max_trade_per_candle can be placed on one candle
        self.max_trade_per_candle = 1  # if 1 only 1 trade can be placed for each candle
        self.re_entrance_distance_limit = 3
        self.force_re_entrance_price = False
        self.re_entrance_loss_enable = False
        self.re_entrance_loss_limit = 2
        self.re_entrance_loss_threshold = 0     # loss pip threshold
        # # Account Management
        self.risk_ratio = 3  # 1% loss per trade if 1
        self.balance_ratio = balance_ratio  # 0.01 LOT for each 1000 dollar if 1

        # Options
        self.multi_position = False     # if false only one position with same direction can be placed
        self.algorithm_force_price = False   # if true positions open in algorithm price only (for gaps)
        self.force_close_on_algorithm_price = False  # if true positions only close in algorithm price ( for gaps )
        self.algorithm_virtual_signal = False    # if true algorithm positions don't executed (only re_entrance)

        # Algorithm Section
        self.algorithm = SIAlgorithm(symbol, data[start_i - self.history_size:start_i],
                                    self.si_win_inc, self.si_win_dec, self.si_shadow_threshold, self.si_body_threshold)
        # self.algorithm = RSIAlgorithm(symbol, data[start_i - self.history_size:start_i], self.rsi_win_inc,
        #                               self.rsi_win_dec, self.rsi_pivot)
        #self.algorithm = MinMaxAlgorithm(symbol, data[start_i - self.history_size:start_i], self.min_max_window_exteremum, self.min_max_window_trend, self.min_max_mode_trend)
        #self.algorithm = RegressionAlgorithm(symbol, data[start_i - self.history_size:start_i], self.reg_alpha, self.reg_beta, self.reg_window_exteremum)
        # self.algorithm = DivergenceAlgorithm(symbol, data[start_i - self.history_size:start_i], self.big_window,
        #                                      self.small_window, self.hidden_divergence_check_window, self.upper_line_tr,
        #                                      self.divergence_alpha)

        # ReEntrance Section
        self.repairment_algorithm = ReEntrance(self.re_entrance_distance_limit, self.re_entrance_loss_enable,
                                               self.re_entrance_loss_limit, self.re_entrance_loss_threshold)

        # Algorithm Tools Section
        self.close_mode = "both"  # 'tp_sl', 'trailing', 'both'
        self.tp_sl_tool = StatisticSL(symbol, self.statistic_sl_window, self.statistic_sl_alpha)
        #self.tp_sl_tool = FixTPSL(symbol, self.fix_tp, self.fix_sl)
        #self.tp_sl_tool = WaveTPSL(self.wave_win_tp_sl, self.wave_alpha, self.wave_beta)
        self.trailing_tool = AdvTraling(symbol, self.adv_window, self.adv_alpha, self.adv_mode)

        # Account Management Section
        self.account_management = AccountManagment.BalanceManagement(self.balance_ratio)






