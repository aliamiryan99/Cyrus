
from Strategies.Strategy import Strategy

from Shared.Variables import Variables
from AlgorithmFactory.AlgorithmTools.Aggregate import aggregate_data
from AlgorithmFactory.AlgorithmTools.Range import *

from Converters.Tools import *
import copy


class RangeRegion(Strategy):
    def __init__(self, market, bid_data, ask_data, symbol, range_candle_threshold, up_timeframe, stop_target_margin, type1_enable,
                 type2_enable, one_stop_in_region, candle_breakout_threshold, max_candles, account_management,
                 management_ratio, risk_free_enable, risk_free_price_percent, risk_free_volume_percent):
        super().__init__(market, bid_data, ask_data)
        self.symbol = symbol
        self.next_time_frame = up_timeframe
        self.range_candle_threshold = range_candle_threshold
        self.type1_enable = type1_enable
        self.type2_enable = type2_enable
        self.one_stop_in_region = one_stop_in_region
        self.candle_breakout_threshold = candle_breakout_threshold
        self.max_candles = max_candles
        self.risk_free_enable = risk_free_enable
        self.risk_free_price_percent = risk_free_price_percent
        self.risk_free_volume_percent = risk_free_volume_percent

        self.buy_position_triggered = False
        self.sell_position_triggered = False
        self.open_buys = []
        self.open_sells = []

        if account_management == 'Balance':
            from AlgorithmFactory.AccountManagment.BalanceManagement import BalanceManagement
            self.account_management = BalanceManagement(management_ratio)
        elif account_management == 'Risk':
            from AlgorithmFactory.AccountManagment.RiskManagement import RiskManagement
            self.account_management = RiskManagement(management_ratio)
        elif account_management == "Fix":
            from AlgorithmFactory.AccountManagment.FixVolume import FixVolume
            self.account_management = FixVolume(management_ratio)

        self.next_data = aggregate_data(bid_data, self.next_time_frame)[:-1]

        self.last_next_candle = self.next_data[-1]
        self.next_data = self.next_data[:-1]
        self.old_id = get_time_id(bid_data[-1]['Time'], up_timeframe)

        self.results, self.results_type = detect_range_region(self.next_data, range_candle_threshold,
                                                              candle_breakout_threshold, max_candles)

        self.extend_results = get_new_result_index(self.results, self.next_data, self.bid_data, self.next_time_frame)

        get_proximal_region(self.bid_data, self.extend_results)

        self.stop_target_margin = stop_target_margin * 10 ** -Variables.config.symbols_pip[symbol]
        self.breakouts_result = get_breakouts2(self.bid_data, self.extend_results, self.stop_target_margin,
                                               self.type1_enable, self.type2_enable, self.one_stop_in_region)

    def on_tick(self):
        if self.buy_position_triggered:
            self.open_buys = self.market.get_open_buy_positions(self.symbol)
            if len(self.open_buys) > 0:
                self.buy_position_triggered = False
        if self.sell_position_triggered:
            self.open_sells = self.market.get_open_sell_positions(self.symbol)
            if len(self.open_sells) > 0:
                self.sell_position_triggered = False
        if len(self.open_buys) == 2:
            min_tp = min(self.open_buys[0]['TP'], self.open_buys[1]['TP'])
            if self.bid_data[-1]['High'] > min_tp:
                self.open_buys = self.market.get_open_buy_positions(self.symbol)
                if len(self.open_buys) == 1:
                    tp = abs(self.open_buys[0]['TP'] - self.open_buys[0]['OpenPrice'])
                    tp = int(tp * 10 ** Variables.config.symbols_pip[self.symbol])
                    self.market.modify(self.open_buys[0]['Ticket'], tp, -20)
        if len(self.open_sells) == 2:
            max_tp = max(self.open_sells[0]['TP'], self.open_sells[1]['TP'])
            if self.bid_data[-1]['Low'] < max_tp:
                self.open_sells = self.market.get_open_sell_positions(self.symbol)
                if len(self.open_sells) == 1:
                    tp = abs(self.open_sells[0]['TP'] - self.open_sells[0]['OpenPrice'])
                    tp = int(tp * 10 ** Variables.config.symbols_pip[self.symbol])
                    self.market.modify(self.open_sells[0]['Ticket'], tp, -20)

    def on_data(self, bid_candle, ask_candle):
        self.bid_data.pop(0)

        # Update last next candle
        self.last_next_candle['High'] = max(self.bid_data[-1]['High'], self.last_next_candle['High'])
        self.last_next_candle['Low'] = min(self.bid_data[-1]['Low'], self.last_next_candle['Low'])
        self.last_next_candle['Close'] = self.bid_data[-1]['Close']
        self.last_next_candle['Volume'] += self.bid_data[-1]['Volume']

        self.extend_results = get_new_result_index(self.results, self.next_data, self.bid_data, self.next_time_frame)
        get_proximal_region(self.bid_data, self.extend_results)

        if len(self.extend_results) != 0 and self.extend_results[-1]['End'] == len(self.bid_data)-1:
            self.breakouts_result = get_breakouts2(self.bid_data, self.extend_results, self.stop_target_margin,
                                                   self.type1_enable, self.type2_enable, self.one_stop_in_region)
            if len(self.breakouts_result) != 0 and self.breakouts_result[-1] is not None and\
                    self.breakouts_result[-1]['X'] == len(self.bid_data)-1:
                price = bid_candle['Open']
                tp = abs(self.breakouts_result[-1]['TargetPrice'] - price)
                tp = int(tp * 10 ** Variables.config.symbols_pip[self.symbol])
                sl = abs(self.breakouts_result[-1]['StopPrice'] - price)
                sl = int(sl * 10 ** Variables.config.symbols_pip[self.symbol])
                volume = self.account_management.calculate(self.market.get_balance(), self.symbol, price,
                                                           self.breakouts_result[-1]['StopPrice'])
                if self.breakouts_result[-1]['TargetPrice'] > self.breakouts_result[-1]['StartPrice']:
                    if self.risk_free_enable:
                        tp1 = sl * (self.risk_free_price_percent/100)
                        volume1 = volume * (self.risk_free_volume_percent/100)
                        volume2 = volume - volume1
                        self.market.buy(price, self.symbol, tp1, sl, volume1)
                        self.market.buy(price, self.symbol, tp, sl, volume2)
                        self.buy_position_triggered = True
                    else:
                        self.market.buy(price, self.symbol, tp, sl, volume)
                else:
                    if self.risk_free_enable:
                        tp1 = sl * (self.risk_free_price_percent / 100)
                        volume1 = volume * (self.risk_free_volume_percent / 100)
                        volume2 = volume - volume1
                        self.market.sell(price, self.symbol, tp1, sl, volume1)
                        self.market.sell(price, self.symbol, tp, sl, volume2)
                        self.sell_position_triggered = True
                    else:
                        self.market.sell(price, self.symbol, tp, sl, volume)

        # Update next data and detect range_regions
        new_id = get_time_id(bid_candle['Time'], self.next_time_frame)
        if new_id != self.old_id:
            self.old_id = new_id
            self.next_data.pop(0)
            self.next_data.append(self.last_next_candle)
            self.last_next_candle = copy.deepcopy(bid_candle)
            self.results, self.results_type = detect_range_region(self.next_data, self.range_candle_threshold,
                                                                  self.candle_breakout_threshold, self.max_candles)

        self.bid_data.append(bid_candle)
