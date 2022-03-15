import copy

from Configuration.Trade.OnlineConfig import Config

from MetaTrader.MetaTraderBase import MetaTraderBase
from MetaTrader.RealTimeTools.RealTimeTool import RealTimeTool

from AlgorithmFactory.AlgorithmPackages.SharpDetection.SharpDetection import SharpDetection
from AlgorithmFactory.AlgorithmTools.LocalExtermums import *
from AlgorithmFactory.AlgorithmPackages.CandleSticks import CandleSticks

from AlgorithmFactory.AccountManagment.RiskManagement import RiskManagement
from AlgorithmFactory.AlgorithmPackages.Trend.TrendDetection import detect_trend


class SupplyAndDemand(RealTimeTool):

    def __init__(self, chart_tool: MetaTraderBase, data, symbol, tr, minimum_candles, tr2, minimum_candles2,
                 swing_filter, fresh_window, atr_window, risk, fresh_limitation, free_risk_enable, touch_trade_enable,
                 candlestick_trade_enable, trend_filter_enable):
        super().__init__(chart_tool, data)

        self.free_risk_enable = free_risk_enable
        self.touch_trade_enable = touch_trade_enable
        self.candlestick_trade_enable = candlestick_trade_enable
        self.trend_filter_enable = trend_filter_enable

        self.fresh_limitation = fresh_limitation

        self.sharp_color = "200,200,200"

        self.speed = 100
        self.risk = risk
        self.sl_margin_atr = 0.5

        self.chart_tool.set_speed(self.speed)
        self.chart_tool.set_candle_start_delay(20)

        self.symbol = symbol
        self.fresh_window = fresh_window
        self.atr_window = atr_window
        self.swing_filter = swing_filter

        self.demand_color = "20,100,200"
        self.supply_color = "240,100,50"

        # Risk Object
        self.risk_manager = RiskManagement(self.risk)

        # Find Movements
        self.sharp_detection = SharpDetection(tr, minimum_candles)
        self.sharp_detection2 = SharpDetection(tr2, minimum_candles2)

        self.find_movements(data, len(data)-1)
        self.find_sources(data)

        # Find Candlestick Patterns
        self.detected_candlesticks = CandleSticks.get_candlesticks(self.data)

        # Set Id
        self.set_sources_id(self.demand_sources)
        self.set_sources_id(self.supply_sources)

        # Save Last Extremum
        self.last_min_extremum = self.data[self.min_extremums[-1]]['Time']
        self.last_max_extremum = self.data[self.max_extremums[-1]]['Time']

        # Save Last Movement
        if len(self.result_up) == 0:
            self.last_up_sharp = self.result2_up[-1]
        elif len(self.result2_up) == 0:
            self.last_up_sharp = self.result_up[-1]
        else:
            if self.result_up[-1]['Start'] > self.result2_up[-1]['Start']:
                self.last_up_sharp = self.result2_up[-1]
            else:
                self.last_up_sharp = self.result_up[-1]

        if len(self.result_down) == 0:
            self.last_down_sharp = self.result2_down[-1]
        elif len(self.result2_down) == 0:
            self.last_down_sharp = self.result_down[-1]
        else:
            if self.result_down[-1]['Start'] > self.result2_down[-1]['Start']:
                self.last_down_sharp = self.result2_down[-1]
            else:
                self.last_down_sharp = self.result_down[-1]

        # Save Last Source
        self.last_demand_source = self.get_last_source(self.demand_sources)
        self.last_supply_source = self.get_last_source(self.supply_sources)

        # Save Fresh Movements
        self.fresh_demand_sources = self.get_fresh_sources(self.demand_sources, self.result_up + self.result2_up)
        self.fresh_supply_sources = self.get_fresh_sources(self.supply_sources, self.result_down + self.result2_down)

        # Save Last Candlestick
        self.last_candlestick = self.detected_candlesticks[-1]

        # Draw
        self.area_id = 1
        self.source_area_id = 1
        self.last_min_id = 1
        self.last_max_id = 1
        self.last_candlestick_index = 1
        self.draw_local_extremum(self.min_extremums, self.max_extremums)
        self.draw_sharps(self.result_up + self.result2_up)
        self.draw_sources(self.demand_sources, self.demand_color)
        self.draw_sharps(self.result_down + self.result2_down)
        self.draw_sources(self.supply_sources, self.supply_color)
        self.draw_candlestick(self.detected_candlesticks)

        self.open_buy_trades_cnt, self.open_sell_trades_cnt = 0, 0

    def on_tick(self, time, bid, ask):
        if self.touch_trade_enable:
            self.check_touch_area(self.fresh_demand_sources, 1, ask)
            self.check_touch_area(self.fresh_supply_sources, 2, bid)

        if self.free_risk_enable:
            self.check_free_risk(bid, ask)

    def on_data(self, candle):
        self.data.pop(0)

        self.update_fresh_sources(self.fresh_demand_sources['Sources'], candle, 'Demand')
        self.update_fresh_sources(self.fresh_supply_sources['Sources'], candle, 'Supply')

        self.find_movements(self.data[-self.fresh_window:], self.atr_window)
        self.find_new_source(self.data[-self.fresh_window:])

        self.redraw_sources(self.fresh_demand_sources['Sources'], self.demand_color)
        self.redraw_sources(self.fresh_supply_sources['Sources'], self.supply_color)

        self.redraw_last_sharp()

        self.check_fresh_expiration()

        self.redraw_extremums()

        self.check_trend()

        if self.candlestick_trade_enable:
            self.check_new_candlestick(candle['Close'])

        self.data.append(candle)

    def check_new_candlestick(self, price):
        detected_candlesticks = CandleSticks.get_candlesticks(self.data[-4:])
        if len(detected_candlesticks) != 0 and detected_candlesticks[-1]['Time'] > self.last_candlestick['Time']:
            self.last_candlestick = detected_candlesticks[-1]
            self.draw_candlestick([self.last_candlestick])

            for i in range(len(self.fresh_demand_sources['Sources'])):
                fresh_demand = self.fresh_demand_sources['Sources'][i]
                if self.last_candlestick['Directions'][0] >= 0 and fresh_demand['Touched']:
                    fresh_movement = self.fresh_demand_sources['Movements'][i]
                    tp = (fresh_movement['ExtPrice'] - price) * 10 ** Config.symbols_pip[self.symbol]
                    atr = get_body_mean(self.data, len(self.data) - 1)
                    sl = (price - fresh_demand['MinMetPrice'] + self.sl_margin_atr * atr) * 10 ** Config.symbols_pip[self.symbol]
                    if tp > sl*2:
                        self.chart_tool.set_speed(0.01)
                        v = self.risk_manager.calculate(self.chart_tool.balance, self.symbol, price, fresh_demand['MinMetPrice'] - self.sl_margin_atr * atr)
                        self.chart_tool.buy(self.symbol, v/2, tp, sl)
                        self.chart_tool.buy(self.symbol, v/2, tp/2, sl)
                        self.fresh_demand_sources['Sources'].pop(i)
                        self.fresh_demand_sources['Movements'].pop(i)
                        self.chart_tool.set_speed(self.speed)
                        break

            for i in range(len(self.fresh_supply_sources['Sources'])):
                fresh_supply = self.fresh_supply_sources['Sources'][i]
                if self.last_candlestick['Directions'][0] <= 0 and fresh_supply['Touched']:
                    fresh_movement = self.fresh_supply_sources['Movements'][i]
                    tp = (price - fresh_movement['ExtPrice']) * 10 ** Config.symbols_pip[self.symbol]
                    atr = get_body_mean(self.data, len(self.data) - 1)
                    sl = (fresh_supply['MaxMetPrice'] - price + self.sl_margin_atr * atr) * 10 ** Config.symbols_pip[self.symbol]
                    if tp > sl*2:
                        self.chart_tool.set_speed(0.01)
                        v = self.risk_manager.calculate(self.chart_tool.balance, self.symbol, price, fresh_supply['MaxMetPrice'] + self.sl_margin_atr * atr)
                        self.chart_tool.sell(self.symbol, v/2, tp, sl)
                        self.chart_tool.sell(self.symbol, v/2, tp/2, sl)
                        self.fresh_supply_sources['Sources'].pop(i)
                        self.fresh_supply_sources['Movements'].pop(i)
                        self.chart_tool.set_speed(self.speed)
                        break

    def check_fresh_expiration(self):
        copy_fresh_demands_sources = copy.copy(self.fresh_demand_sources['Sources'])
        copy_fresh_demands_movements = copy.copy(self.fresh_demand_sources['Movements'])
        for i in range(len(copy_fresh_demands_sources)):
            fresh_source = copy_fresh_demands_sources[i]
            fresh_movement = copy_fresh_demands_movements[i]
            if (self.data[-2]['Close'] < fresh_source['DownPrice'] and self.data[-1]['Close'] < fresh_source['DownPrice'])\
                    or fresh_source['End'] - fresh_source['Start'] > self.fresh_limitation:
                self.fresh_demand_sources['Sources'].remove(fresh_source)
                self.fresh_demand_sources['Movements'].remove(fresh_movement)
        copy_fresh_supply_sources = copy.copy(self.fresh_supply_sources['Sources'])
        copy_fresh_supply_movements = copy.copy(self.fresh_supply_sources['Movements'])
        for i in range(len(copy_fresh_supply_sources)):
            fresh_source = copy_fresh_supply_sources[i]
            fresh_movement = copy_fresh_supply_movements[i]
            if (self.data[-2]['Close'] > fresh_source['UpPrice'] and self.data[-2]['Close'] > fresh_source['DownPrice']) \
                    or fresh_source['End'] - fresh_source['Start'] > self.fresh_limitation:
                self.fresh_supply_sources['Sources'].remove(fresh_source)
                self.fresh_supply_sources['Movements'].remove(fresh_movement)

        for i in range(len(self.fresh_demand_sources['Sources'])-1):
            last_source = self.fresh_demand_sources['Sources'][-1]
            fresh_source = self.fresh_demand_sources['Sources'][i]
            if max(fresh_source['DownPrice'], last_source['DownPrice']) < min(fresh_source['UpPrice'], last_source['UpPrice']):
                self.fresh_demand_sources['Sources'].pop(i)
                self.fresh_demand_sources['Movements'].pop(i)
                break
        for i in range(len(self.fresh_supply_sources['Sources'])-1):
            last_source = self.fresh_supply_sources['Sources'][-1]
            fresh_source = self.fresh_supply_sources['Sources'][i]
            if max(fresh_source['DownPrice'], last_source['DownPrice']) < min(fresh_source['UpPrice'], last_source['UpPrice']):
                self.fresh_supply_sources['Sources'].pop(i)
                self.fresh_supply_sources['Movements'].pop(i)
                break

    def check_touch_area(self, sources, type, price):
        copy_sources = copy.copy(sources['Sources'])
        copy_movements = copy.copy(sources['Movements'])
        for i in range(len(copy_sources)):
            if type == 1:   # Demand
                if price < copy_sources[i]['UpPrice']:
                    self.chart_tool.set_speed(0.01)
                    atr = get_body_mean(self.data, len(self.data)-1)
                    sl = (price - copy_sources[i]['DownPrice'] + 0.5 * atr) * 10 ** Config.symbols_pip[self.symbol]
                    v = self.risk_manager.calculate(self.chart_tool.balance, self.symbol, price, copy_sources[i]['DownPrice'])
                    self.chart_tool.buy(self.symbol, v, sl, sl)
                    sources['Sources'].remove(copy_sources[i])
                    sources['Movements'].remove(copy_movements[i])
                    self.chart_tool.set_speed(self.speed)
            if type == 2:   # Supply
                if price > copy_sources[i]['DownPrice']:
                    self.chart_tool.set_speed(0.01)
                    atr = get_body_mean(self.data, len(self.data) - 1)
                    sl = (copy_sources[i]['UpPrice'] - price + 0.5 * atr) * 10 ** Config.symbols_pip[self.symbol]
                    v = self.risk_manager.calculate(self.chart_tool.balance, self.symbol, price, copy_sources[i]['UpPrice'])
                    self.chart_tool.sell(self.symbol, v, sl, sl)
                    sources['Sources'].remove(copy_sources[i])
                    sources['Movements'].remove(copy_movements[i])
                    self.chart_tool.set_speed(self.speed)

    def check_free_risk(self, bid, ask):
        if len(self.chart_tool.open_buy_trades) == 1:
            if self.chart_tool.open_buy_trades[0]['SL'] < self.chart_tool.open_buy_trades[0]['OpenPrice']:
                if (self.chart_tool.open_buy_trades[0]['OpenPrice'] * 2 + self.chart_tool.open_buy_trades[0]['TP']) / 3 < bid:
                    self.chart_tool.set_speed(0.01)
                    tp = int((self.chart_tool.open_buy_trades[0]['TP'] - self.chart_tool.open_buy_trades[0][
                        'OpenPrice']) * 10 ** Config.symbols_pip[self.symbol])
                    self.chart_tool.modify(self.chart_tool.open_buy_trades[0]['Ticket'], tp, -20)
                    self.chart_tool.open_buy_trades[0]['SL'] = self.chart_tool.open_buy_trades[0]['OpenPrice']
                    self.chart_tool.set_speed(self.speed)
        if len(self.chart_tool.open_sell_trades) == 1:
            if self.chart_tool.open_sell_trades[0]['SL'] > self.chart_tool.open_sell_trades[0]['OpenPrice']:
                if (self.chart_tool.open_sell_trades[0]['OpenPrice'] * 2 + self.chart_tool.open_sell_trades[0]['TP']) / 3 > ask:
                    self.chart_tool.set_speed(0.01)
                    tp = int((self.chart_tool.open_sell_trades[0]['OpenPrice'] - self.chart_tool.open_sell_trades[0][
                        'TP']) * 10 ** Config.symbols_pip[self.symbol])
                    self.chart_tool.modify(self.chart_tool.open_sell_trades[0]['Ticket'], tp, -20)
                    self.chart_tool.open_sell_trades[0]['SL'] = self.chart_tool.open_sell_trades[0]['OpenPrice']
                    self.chart_tool.set_speed(self.speed)
        self.open_buy_trades_cnt = len(self.chart_tool.open_buy_trades)
        self.open_sell_trades_cnt = len(self.chart_tool.open_sell_trades)

    def check_trend(self):
        open, high, low, close = get_ohlc(self.data)
        self.local_min_asyc, self.local_max_asyc = get_local_extermums_asymetric(self.data, 50, 10, 1)
        bullish, bearish = detect_trend(self.local_max_asyc, self.local_min_asyc, high, low)
        if bullish[-1] > bearish[-1]:
            self.chart_tool.delete(["TrendLabel"])
            self.chart_tool.label(["TrendLabel"], [50], [20], ['Bullish'], color="50,50,250"
                                  , corner=self.chart_tool.EnumBaseCorner.RightUpper)
        else:
            self.chart_tool.delete(["TrendLabel"])
            self.chart_tool.label(["TrendLabel"], [50], [20], ['Bearish'], color="250,50,50"
                                  ,  corner=self.chart_tool.EnumBaseCorner.RightUpper)

    def find_movements(self, data, atr_window):
        self.min_extremums, self.max_extremums = get_local_extermums(data, 10, 1)
        open, high, low, close = get_ohlc(data)
        self.result_up, self.result_down = self.sharp_detection.get_sharps(data, close, atr_window)
        self.result2_up, self.result2_down = self.sharp_detection2.get_sharps(data, close, atr_window)

        # Filter Movements
        self.result2_up = self.sharp_detection2.filter_intersections("Demand", self.result_up)
        self.result2_down = self.sharp_detection2.filter_intersections("Supply", self.result_down)
        self.sharp_detection2.set_sharp_area_up(self.result2_up)
        self.sharp_detection2.set_sharp_area_down(self.result2_down)
        if self.swing_filter:
            self.result_up = self.sharp_detection.filter_swings("Demand", self.min_extremums, self.max_extremums, high, 10)
            self.sharp_detection.set_sharp_area_up(self.result_up)
            self.result_down = self.sharp_detection.filter_swings("Supply", self.min_extremums, self.max_extremums, low, 10)
            self.sharp_detection.set_sharp_area_down(self.result_down)
            self.result2_up = self.sharp_detection2.filter_swings("Demand", self.min_extremums, self.max_extremums, high, 10)
            self.sharp_detection2.set_sharp_area_up(self.result2_up)
            self.result2_down = self.sharp_detection2.filter_swings("Supply", self.min_extremums, self.max_extremums, low, 10)
            self.sharp_detection2.set_sharp_area_down(self.result2_down)

    def find_sources(self, data):
        # Find Source of Movements
        self.demand_sources = self.sharp_detection.get_source_of_movement("Demand", data, self.fresh_limitation)
        self.demand_sources += self.sharp_detection2.get_source_of_movement("Demand", data, self.fresh_limitation)

        self.supply_sources = self.sharp_detection.get_source_of_movement("Supply", data,  self.fresh_limitation)
        self.supply_sources += self.sharp_detection2.get_source_of_movement("Supply", data, self.fresh_limitation)

    def update_fresh_sources(self, fresh_sources, last_candle, type):
        copy_fresh_sources = copy.copy(fresh_sources)
        for fresh_source in copy_fresh_sources:
            fresh_source['End'] += 1
            fresh_source['EndTime'] = last_candle['Time']
            if type == "Demand":
                if self.data[-1]['Low'] <= fresh_source['UpPrice']:
                    fresh_source['Touched'] = True
                if self.data[-1]['Low'] < fresh_source['MinMetPrice']:
                    fresh_source['MinMetPrice'] = self.data[-1]['Low']
            if type == "Supply":
                if self.data[-1]['High'] >= fresh_source['DownPrice']:
                    fresh_source['Touched'] = True
                if self.data[-1]['High'] > fresh_source['MaxMetPrice']:
                    fresh_source['MaxMetPrice'] = self.data[-1]['High']

    def get_last_source(self, sources):
        last_source = sources[0]
        for i in range(len(sources)):
            if sources[i]['Start'] > last_source['Start']:
                last_source = sources[i]
        return last_source

    def find_new_source(self, data):
        demand_sources = self.sharp_detection.get_source_of_movement("Demand", data, self.fresh_limitation)
        if len(demand_sources) != 0 and demand_sources[-1]['StartTime'] > self.last_demand_source['StartTime'] and \
                demand_sources[-1]['EndTime'] >= data[-1]['Time']:
            if self.result_up[-1]['StartTime'] > self.last_up_sharp['EndTime']:
                demand_sources[-1]['ID'] = self.last_demand_source['ID'] + 1
                self.last_demand_source = demand_sources[-1]
                self.last_up_sharp = self.result_up[-1]
                self.fresh_demand_sources['Sources'].append(self.last_demand_source)
                self.fresh_demand_sources['Movements'].append(self.last_up_sharp)
                self.draw_sharps([self.result_up[-1]])
        demand_sources = self.sharp_detection2.get_source_of_movement("Demand", data, self.fresh_limitation)
        if len(demand_sources) != 0 and demand_sources[-1]['StartTime'] > self.last_demand_source['StartTime'] and \
                demand_sources[-1]['EndTime'] >= data[-1]['Time']:
            if self.result2_up[-1]['StartTime'] > self.last_up_sharp['EndTime']:
                demand_sources[-1]['ID'] = self.last_demand_source['ID'] + 1
                self.last_demand_source = demand_sources[-1]
                self.last_up_sharp = self.result2_up[-1]
                self.fresh_demand_sources['Sources'].append(self.last_demand_source)
                self.fresh_demand_sources['Movements'].append(self.last_up_sharp)
                self.draw_sharps([self.result2_up[-1]])
        supply_sources = self.sharp_detection.get_source_of_movement("Supply", data, self.fresh_limitation)
        if len(supply_sources) != 0 and supply_sources[-1]['StartTime'] > self.last_supply_source['StartTime'] and \
                supply_sources[-1]['EndTime'] >= data[-1]['Time']:
            if self.result_down[-1]['StartTime'] > self.last_down_sharp['EndTime']:
                supply_sources[-1]['ID'] = self.last_supply_source['ID'] + 1
                self.last_supply_source = supply_sources[-1]
                self.last_down_sharp = self.result_down[-1]
                self.fresh_supply_sources['Sources'].append(self.last_supply_source)
                self.fresh_supply_sources['Movements'].append(self.last_down_sharp)
                self.draw_sharps([self.result_down[-1]])
        supply_sources = self.sharp_detection2.get_source_of_movement("Supply", data, self.fresh_limitation)
        if len(supply_sources) != 0 and supply_sources[-1]['StartTime'] > self.last_supply_source['StartTime'] and \
                supply_sources[-1]['EndTime'] >= data[-1]['Time']:
            if self.result2_down[-1]['StartTime'] > self.last_down_sharp['EndTime']:
                supply_sources[-1]['ID'] = self.last_supply_source['ID'] + 1
                self.last_supply_source = supply_sources[-1]
                self.last_down_sharp = self.result2_down[-1]
                self.fresh_supply_sources['Sources'].append(self.last_supply_source)
                self.fresh_supply_sources['Movements'].append(self.last_down_sharp)
                self.draw_sharps([self.result2_down[-1]])

    def get_fresh_sources(self, origin_sources, movements):
        fresh_sources = {'Sources': [], 'Movements': []}
        for i in range(len(origin_sources)):
            if origin_sources[i]['End'] == len(self.data) - 1:
                fresh_sources['Sources'].append(origin_sources[i])
                fresh_sources['Movements'].append(movements[i])
        return fresh_sources

    def set_sources_id(self, sources):
        for i in range(len(sources)):
            sources[i]['ID'] = i+1

    def redraw_extremums(self):
        if len(self.max_extremums) > 0 and self.data[self.max_extremums[-1]]['Time'] > self.last_max_extremum:
            self.last_max_extremum = self.data[self.max_extremums[-1]]['Time']
            self.draw_local_extremum([], [self.max_extremums[-1]])
        if len(self.min_extremums) > 0 and self.data[self.min_extremums[-1]]['Time'] > self.last_min_extremum:
            self.last_min_extremum = self.data[self.min_extremums[-1]]['Time']
            self.draw_local_extremum([self.min_extremums[-1]], [])

    def draw_candlestick(self, detected_list):
        names, text, times, prices = [], [], [], []
        for i in range(len(detected_list)):
            names.append(f"{self.last_candlestick_index}")
            text.append(f"{detected_list[i]['Type']}")
            times.append(detected_list[i]['Time'])
            prices.append(detected_list[i]['Price'])
            self.last_candlestick_index += 1
        self.chart_tool.text(names, times, prices, text, self.chart_tool.EnumAnchor.Top)

    def redraw_sources(self, fresh_sources, color):
        if len(fresh_sources) > 0:
            self.delete_sources(fresh_sources)
            self.draw_sources(fresh_sources, color)

    def redraw_last_sharp(self):
        sharps_up = self.result_up + self.result2_up
        if len(sharps_up) > 0:
            last_sharp_up = self.result_up[-1] if len(self.result2_up) == 0 or (len(self.result_up) != 0 and self.result_up[-1]['Start'] > self.result2_up[-1]['Start']) else self.result2_up[-1]
            if len(sharps_up) != 0 and last_sharp_up['StartTime'] == self.last_up_sharp['StartTime'] and last_sharp_up['EndTime'] >= self.data[-2]['Time']:
                self.last_up_sharp = last_sharp_up
                self.fresh_demand_sources['Movements'][-1] = self.last_up_sharp
                self.area_id -= 1
                self.chart_tool.delete([f"SharpArea{self.area_id}"])
                self.draw_sharps([self.last_up_sharp])
        sharps_down = self.result_down + self.result2_down
        if len(sharps_down) > 0:
            last_down_sharp = self.result_down[-1] if len(self.result2_down) == 0 or (len(self.result_down) != 0 and self.result_down[-1]['Start'] > self.result2_down[-1]['Start']) else self.result2_down[-1]
            if len(sharps_down) != 0 and last_down_sharp['StartTime'] == self.last_down_sharp['StartTime'] and last_down_sharp['EndTime'] >= self.data[-1]['Time']:
                self.last_down_sharp = last_down_sharp
                self.fresh_supply_sources['Movements'][-1] = self.last_down_sharp
                self.area_id -= 1
                self.chart_tool.delete([f"SharpArea{self.area_id}"])
                self.draw_sharps([self.last_down_sharp])

    def draw_sharps(self, results):
        if len(results) != 0:
            names1, times1, prices1, times2, prices2 = [], [], [], [], []
            for i in range(len(results)):
                times1.append(self.data[results[i]['Start']]['Time'])
                prices1.append(self.data[results[i]['Start']]['Open'])
                times2.append(self.data[min(results[i]['Ext']+1, len(self.data)-1)]['Time'])
                prices2.append(self.data[min(results[i]['Ext']+1, len(self.data)-1)]['Open'])
                names1.append(f"SharpArea{self.area_id}")
                self.area_id += 1
            self.chart_tool.rectangle(names1, times1, prices1, times2, prices2, back=1, color=self.sharp_color)

    def draw_sources(self, sources, color):
        if len(sources) != 0:
            names1, times1, prices1, times2, prices2 = [], [], [], [], []
            for i in range(len(sources)):
                times1.append(sources[i]['StartTime'])
                prices1.append(sources[i]['UpPrice'])
                times2.append(sources[i]['EndTime'])
                prices2.append(sources[i]['DownPrice'])
                names1.append(f"SourceArea{sources[i]['Type']}{sources[i]['ID']}")
            self.chart_tool.rectangle(names1, times1, prices1, times2, prices2, back=1, color=color)

    def delete_sources(self, sources):
        names = []
        for source in sources:
            names.append(f"SourceArea{source['Type']}{source['ID']}")
        self.chart_tool.delete(names)

    def draw_local_extremum(self, local_min, local_max):

        if len(local_min) != 0:
            times1, prices1, texts1, names1 = [], [], [], []
            for i in range(len(local_min)):
                times1.append(self.data[local_min[i]]['Time'])
                prices1.append(self.data[local_min[i]]['Low'])
                texts1.append(self.data[local_min[i]]['Low'])
                names1.append(f"LocalMinPython{self.last_min_id}")
                self.last_min_id += 1
            self.chart_tool.arrow_up(names1, times1, prices1, anchor=self.chart_tool.EnumArrowAnchor.Top, color="12,83,211")
        if len(local_max) != 0:
            times2, prices2, texts2, names2 = [], [], [], []
            for i in range(len(local_max)):
                times2.append(self.data[local_max[i]]['Time'])
                prices2.append(self.data[local_max[i]]['High'])
                texts2.append(self.data[local_max[i]]['High'])
                names2.append(f"LocalMaxPython{self.last_max_id}")
                self.last_max_id += 1
            self.chart_tool.arrow_down(names2, times2, prices2, anchor=self.chart_tool.EnumArrowAnchor.Bottom, color="211,83,12")
