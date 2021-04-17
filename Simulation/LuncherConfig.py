from Algorithms.SimpleIdeaAlgorithm import SIAlgorithm
from Algorithms.RefinementSiAlgorithm import RSIAlgorithm
from Algorithms.SimpleIdeaModified import SIMAlgorithm
from Algorithms.DiveregenceAlgorithms import DivergenceAlgorithm
from Algorithms.SequenceAlgorithm import SequenceAlgorithm
from Algorithms.DojiAlgorithm import DojiAlgorithm
from Algorithms.HighLowBreakAlgorithm import HighLowBreakAlgorithm
from Algorithms.SimpleIdeaAndDoji import SIAndDojiAlgorithm
from Algorithms.SemiHammerAlgorithm import SemiHammerAlgorithm
from Algorithms.SimpleTrendLineBreakAlgorithm import SimpleTrendLineBreakAlgorithm
from Algorithms.MACrossAlgorithm import MAAlgorithm
from Algorithms.SSSRAlgorithm import SSSRAlgorithm
from Algorithms.MonotoneExtremumAlgorithm import MEAlgorithm
from Algorithms.ExtremumTrendsBreakAlgorithm import ETBAlgorithm
from Algorithms.RLAlgorithm import RLAlgorithm
from AlgorithmsRepairment.ReEntranceAlgorithm import ReEntrance
from AlgorithmsExit.AdvancedTrailing import AdvTraling
from AlgorithmsExit.TrailingWithHugeCandle import TrailingWithHugeCandle
from AlgorithmsExit.CandleTrailing import CandleTrailing
from AlgorithmsExit.WaveTPSL import WaveTPSL
from AlgorithmsExit.StatisticSL import StatisticSL
from AlgorithmsExit.BodyTP import BodyTP
from AccountManagment import AccountManagment


class LauncherConfig:
    # Hyper Parameters
    categories = ["Major"]
    symbols = ["EURUSD"]
    symbols_ratio = [3]
    history_size = 200
    algorithm_time_frame = "M30"
    trailing_time_frame = "M30"
    algorithm_name = "Divergence"
    tag = "EURUSD"

    def __init__(self, symbol, data, start_i, balance_ratio):
        # # Algorithms
        # Simple Idea
        self.si_win_inc = 2
        self.si_win_dec = 2
        self.si_shadow_threshold = 10
        self.si_body_threshold = 0

        # High Low Break
        self.high_low_break_window = 10

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
        self.hidden_divergence_check_window = 15
        self.upper_line_tr = 0.90
        self.divergence_alpha = 20
        self.divergence_extremum_mode = 1

        # Doji
        self.doji_win = 3
        self.doji_detect_mode = 3       # 1: HighLow, 2: TopBottom, 3: LastCandle
        self.doji_candle_mode = 1       # 1: Body, 2: Total

        # Semi Hammer
        self.semi_hammer_window = 20
        self.semi_hammer_detect_mode = 1
        self.semi_hammer_alpha = 2
        self.semi_hammer_trigger_threshold = 2

        # Simple Trend Line Break
        self.stlb_window = 100

        # Moving Average Cross
        self.ma_total_data_size = 100
        self.ma_window_size = 12
        self.ma_price_type = 'Close'
        self.ma_type = "EMA"
        self.ma_extremum_window = 2
        self.ma_extremum_mode = 2       # 1 : High Low , 2 : Top Bottom
        self.ma_extremum_pivot = 1

        # Super Strong Support Resistance
        self.sssr_window_size = 150
        self.sssr_extremum_window = 2
        self.sssr_extremum_mode = 2   # 1 : High Low , 2 : Top Bottom

        # Extremum Trends Break
        self.etb_window_size = 150
        self.etb_extremum_window = 1
        self.etb_extremum_mode = 2      # 1 : High Low , 2 : Top Bottom
        self.is_last_candle_check = False

        # Monotone Extremum
        self.me_window_size = 150
        self.me_extremum_window = 2
        self.me_extremum_mode = 2  # 1 : High Low , 2 : Top Bottom
        self.me_extremum_level = 3
        self.me_extremum_pivot = 1

        # Renforcement Learning
        self.rl_window_size = 100

        # # Exit Algorithms
        # Advance Trailing Stop
        self.adv_mode = 3
        self.adv_window = 10
        self.adv_alpha = 0.1

        # Trailing With Huge Candle
        self.trailing_huge_alpha = 0
        self.trailing_huge_beta = 0.8
        self.trailing_huge_mode = 1
        self.trailing_huge_extremum_window = 2
        self.trailing_huge_extremum_mode = 2    # 1 : High Low , 2 : Top Bottom
        self.trailing_huge_extremum_pivot = 4

        # Fix TP SL
        self.fix_tp = 0  # it can be disable if value equal to 0 (in point)
        self.fix_sl = 0  # it can be disable if value equal to 0 (int point)

        # Statistic SL
        self.statistic_sl_window = 10  # it can be disable if value equal to 0 (in point)
        self.statistic_sl_alpha = 0.8  # it can be disable if value equal to 0 (int point)

        # Body TP
        self.body_tp_window = 10
        self.body_tp_alpha = 1
        self.body_tp_mode = 1   # 1: body, 2: total

        # Wave TP SL
        self.wave_win_tp_sl = 3
        self.wave_alpha = 0.3
        self.wave_beta = 0.3


        # # Re Entrance
        self.re_entrance_enable = False  # if true the re entrance algorithm will execute
        self.enable_max_trade_per_candle = True  # if true only max_trade_per_candle can be placed on one candle
        self.max_trade_per_candle = 2  # if 1 only 1 trade can be placed for each candle
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
        #self.algorithm = SIAlgorithm(symbol, data[start_i - self.history_size:start_i], self.si_win_inc, self.si_win_dec, self.si_shadow_threshold, self.si_body_threshold)
        #self.algorithm = SemiHammerAlgorithm(symbol, data[start_i - self.history_size:start_i], self.semi_hammer_window, self.semi_hammer_alpha, self.semi_hammer_detect_mode, self.semi_hammer_trigger_threshold)
        #self.algorithm = SimpleTrendLineBreakAlgorithm(data[start_i - self.history_size:start_i], self.stlb_window)
        #self.algorithm = RSIAlgorithm(symbol, data[start_i - self.history_size:start_i], self.rsi_win_inc, self.rsi_win_dec, self.rsi_pivot)
        #self.algorithm = SIMAlgorithm(symbol, data[start_i - self.history_size:start_i], self.si_win_inc, self.si_win_dec, self.si_shadow_threshold, self.si_body_threshold)
        #self.algorithm = HighLowBreakAlgorithm(symbol, data[start_i - self.history_size:start_i], self.high_low_break_window)
        #self.algorithm = MinMaxAlgorithm(symbol, data[start_i - self.history_size:start_i], self.min_max_window_exteremum, self.min_max_window_trend, self.min_max_mode_trend)
        #self.algorithm = RegressionAlgorithm(symbol, data[start_i - self.history_size:start_i], self.reg_alpha, self.reg_beta, self.reg_window_exteremum)
        self.algorithm = DivergenceAlgorithm(symbol, data[start_i - self.history_size:start_i], self.big_window, self.small_window, self.hidden_divergence_check_window, self.upper_line_tr, self.divergence_alpha, self.divergence_extremum_mode)
        #self.algorithm = SequenceAlgorithm(symbol, data[start_i - self.history_size:start_i], self.si_win_inc, self.si_win_dec, self.si_shadow_threshold, self.si_body_threshold)
        #self.algorithm = DojiAlgorithm(data[start_i - self.history_size:start_i], self.doji_win, self.doji_detect_mode, self.doji_candle_mode)
        #self.algorithm = SIAndDojiAlgorithm(symbol, data[start_i - self.history_size:start_i], self.si_win_inc, self.si_win_dec, self.si_shadow_threshold, self.si_body_threshold, self.doji_win, self.doji_detect_mode, self.doji_candle_mode)
        #self.algorithm = MAAlgorithm(symbol, data[start_i - self.history_size:start_i], self.ma_total_data_size, self.ma_window_size, self.ma_price_type, self.ma_type ,self.ma_extremum_window, self.ma_extremum_mode, self.ma_extremum_pivot)
        #self.algorithm = SSSRAlgorithm(symbol, data[start_i - self.history_size:start_i], self.sssr_window_size, self.sssr_extremum_window, self.sssr_extremum_mode)
        #self.algorithm = ETBAlgorithm(symbol, data[start_i - self.history_size:start_i], self.etb_window_size, self.etb_extremum_window, self.etb_extremum_mode, self.is_last_candle_check)
        #self.algorithm = MEAlgorithm(symbol, data[start_i - self.history_size:start_i], self.me_window_size, self.me_extremum_window, self.me_extremum_mode, self.me_extremum_level, self.me_extremum_pivot)
        self.algorithm = RLAlgorithm(symbol, data[start_i - self.history_size:start_i], self.rl_window_size)

        # ReEntrance Section
        self.repairment_algorithm = ReEntrance(self.re_entrance_distance_limit, self.re_entrance_loss_enable, self.re_entrance_loss_limit, self.re_entrance_loss_threshold)

        # Algorithm Tools Section
        self.close_mode = "trailing"  # 'tp_sl', 'trailing', 'both'
        #self.tp_sl_tool = BodyTP(self.body_tp_window, self.body_tp_alpha, self.body_tp_mode)
        #self.tp_sl_tool = StatisticSL(symbol, self.statistic_sl_window, self.statistic_sl_alpha)
        #self.tp_sl_tool = FixTPSL(symbol, self.fix_tp, self.fix_sl)
        self.tp_sl_tool = WaveTPSL(self.wave_win_tp_sl, self.wave_alpha, self.wave_beta)
        #self.trailing_tool = AdvTraling(symbol, self.adv_window, self.adv_alpha, self.adv_mode)
        self.trailing_tool = TrailingWithHugeCandle(data[start_i - self.history_size:start_i], self.trailing_huge_alpha, self.trailing_huge_beta, self.trailing_huge_mode, self.trailing_huge_extremum_window, self.trailing_huge_extremum_mode, self.trailing_huge_extremum_pivot)
        #self.trailing_tool = CandleTrailing()

        # Account Management Section
        self.account_management = AccountManagment.BalanceManagement(self.balance_ratio)






