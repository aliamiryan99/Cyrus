
from Strategies.Strategy import Strategy

from Shared.Variables import Variables
from AlgorithmFactory.AlgorithmTools.Aggregate import aggregate_data
from AlgorithmFactory.AlgorithmTools.Range import *

from Converters.Tools import *
import copy


class RangeRegion(Strategy):
    def __init__(self, market, data, symbol, range_candle_threshold, up_timeframe, stop_target_margin, account_management, management_ratio):
        super().__init__(market, data)
        self.symbol = symbol
        self.next_time_frame = up_timeframe
        self.range_candle_threshold = range_candle_threshold

        if account_management == 'Balance':
            from AlgorithmFactory.AccountManagment.BalanceManagement import BalanceManagement
            self.account_management = BalanceManagement(management_ratio)
        elif account_management == 'Risk':
            from AlgorithmFactory.AccountManagment.RiskManagement import RiskManagement
            self.account_management = RiskManagement(management_ratio)
        elif account_management == "Fix":
            from AlgorithmFactory.AccountManagment.FixVolume import FixVolume
            self.account_management = FixVolume(management_ratio)

        self.next_data = aggregate_data(data, self.next_time_frame)[:-1]

        self.last_next_candle = self.next_data[-1]
        self.next_data = self.next_data[:-1]
        self.old_id = get_time_id(data[-1]['Time'], up_timeframe)

        self.results, self.results_type = detect_range_region(self.next_data, range_candle_threshold)

        self.extend_results = get_new_result_index(self.results, self.next_data, self.data, self.next_time_frame)

        get_proximal_region(self.data, self.extend_results)

        self.stop_target_margin = stop_target_margin * 10 ** -Variables.config.symbols_pip[symbol]
        self.breakouts_result = get_breakouts2(self.data, self.extend_results, self.stop_target_margin)

    def on_tick(self):
        pass

    def on_data(self, candle):
        self.data.pop(0)

        # Update last next candle
        self.last_next_candle['High'] = max(self.data[-1]['High'], self.last_next_candle['High'])
        self.last_next_candle['Low'] = min(self.data[-1]['Low'], self.last_next_candle['Low'])
        self.last_next_candle['Close'] = self.data[-1]['Close']
        self.last_next_candle['Volume'] += self.data[-1]['Volume']

        self.extend_results = get_new_result_index(self.results, self.next_data, self.data, self.next_time_frame)
        get_proximal_region(self.data, self.extend_results)

        if len(self.extend_results) != 0 and self.extend_results[-1]['End'] == len(self.data)-1:
            self.breakouts_result = get_breakouts2(self.data, self.extend_results, self.stop_target_margin)
            if len(self.breakouts_result) != 0 and self.breakouts_result[-1] is not None and\
                    self.breakouts_result[-1]['X'] == len(self.data)-1:
                price = candle['Open']
                tp = abs(self.breakouts_result[-1]['TargetPrice'] - price)
                tp = int(tp * 10 ** Variables.config.symbols_pip[self.symbol])
                sl = abs(self.breakouts_result[-1]['StopPrice'] - price)
                sl = int(sl * 10 ** Variables.config.symbols_pip[self.symbol])
                volume = self.account_management.calculate(self.market.get_balance(), self.symbol, price,
                                                           self.breakouts_result[-1]['StopPrice'])
                if self.breakouts_result[-1]['TargetPrice'] > self.breakouts_result[-1]['StartPrice']:
                    self.market.buy(price, self.symbol, tp, sl, volume)
                else:
                    self.market.sell(price, self.symbol, tp, sl, volume)

        # Update next data and detect range_regions
        new_id = get_time_id(candle['Time'], self.next_time_frame)
        if new_id != self.old_id:
            self.old_id = new_id
            self.next_data.pop(0)
            self.next_data.append(self.last_next_candle)
            self.last_next_candle = copy.deepcopy(candle)
            self.results, self.results_type = detect_range_region(self.next_data, self.range_candle_threshold)


        self.data.append(candle)