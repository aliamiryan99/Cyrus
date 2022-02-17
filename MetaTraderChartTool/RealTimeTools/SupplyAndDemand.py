
from Configuration.Trade.OnlineConfig import Config

from MetaTrader.MetaTraderBase import MetaTraderBase
from MetaTraderChartTool.RealTimeTools.RealTimeTool import RealTimeTool

from AlgorithmFactory.AlgorithmPackages.SharpDetection.SharpDetection import SharpDetection
from AlgorithmFactory.AlgorithmTools.LocalExtermums import *


class SupplyAndDemand(RealTimeTool):

    def __init__(self, chart_tool: MetaTraderBase, data, symbol, tr, minimum_candles, tr2, minimum_candles2, swing_filter, fresh_window):
        super().__init__(chart_tool, data)

        self.chart_tool.set_speed(200)
        self.chart_tool.set_candle_start_delay(5)

        self.symbol = symbol
        self.fresh_window = fresh_window
        self.swing_filter = swing_filter

        self.demand_color = "20,100,200"
        self.supply_color = "240,100,50"

        # Find Movements
        self.sharp_detection = SharpDetection(tr, minimum_candles)
        self.sharp_detection2 = SharpDetection(tr2, minimum_candles2)

        self.find_movements(data)
        self.find_sources(data)

        # Set Id
        self.set_sources_id(self.demand_sources)
        self.set_sources_id(self.supply_sources)

        # Save Last Source
        self.last_demand_source = self.get_last_source(self.demand_sources)
        self.last_supply_source = self.get_last_source(self.supply_sources)

        # Save Fresh Movements
        self.fresh_demand_sources = self.get_fresh_sources(self.demand_sources)
        self.fresh_supply_sources = self.get_fresh_sources(self.supply_sources)

        # Draw Movements
        self.area_id = 1
        self.source_area_id = 1
        self.last_min_id = 1
        self.last_max_id = 1
        self.draw_local_extremum(self.min_extremums, self.max_extremums)
        self.draw_sharps(self.result_up)
        self.draw_sharps(self.result2_up)
        self.draw_sources(self.demand_sources, self.demand_color)
        self.draw_sharps(self.result_down)
        self.draw_sharps(self.result2_down)
        self.draw_sources(self.supply_sources, self.supply_color)

        self.data = self.data[-fresh_window:]

    def on_tick(self, time, bid, ask):
        self.check_touch_area(self.fresh_demand_sources, 1, ask)
        self.check_touch_area(self.fresh_supply_sources, 2, bid)

    def on_data(self, candle):
        self.data.pop(0)

        self.update_fresh_sources(self.fresh_demand_sources, "Demand", candle)
        self.update_fresh_sources(self.fresh_supply_sources, "Supply", candle)

        self.find_movements(self.data)
        self.find_new_source(self.data)

        self.redraw_movements(self.fresh_demand_sources, self.demand_color)
        self.redraw_movements(self.fresh_supply_sources, self.supply_color)

        self.data.append(candle)

    def check_touch_area(self, sources, type, price):
        for i in range(len(sources)):
            if type == 1:   # Demand
                if price < sources[i]['UpPrice']:
                    sl = (price - sources[i]['DownPrice']) * 10 ** Config.symbols_pip[self.symbol]
                    self.chart_tool.buy(self.symbol, 1, sl, sl)
                    self.chart_tool.buy(self.symbol, 1, sl*2, sl)
                    sources.pop(i)
            if type == 2:   # Supply
                if price > sources[i]['DownPrice']:
                    sl = (sources[i]['UpPrice'] - price) * 10 ** Config.symbols_pip[self.symbol]
                    self.chart_tool.sell(self.symbol, 1, sl, sl)
                    self.chart_tool.sell(self.symbol, 1, sl*2, sl)
                    sources.pop(i)

    def find_movements(self, data):
        self.min_extremums, self.max_extremums = get_local_extermums(data, 10, 2)
        open, high, low, close = get_ohlc(data)
        self.result_up, self.result_down = self.sharp_detection.get_sharps(data, close)
        self.result2_up, self.result2_down = self.sharp_detection2.get_sharps(data, close)

        # Filter Movements
        self.result2_up = self.sharp_detection2.filter_intersections("Demand", self.result_up)
        self.result2_down = self.sharp_detection2.filter_intersections("Supply", self.result_down)
        self.sharp_detection2.set_sharp_area_up(self.result2_up)
        self.sharp_detection2.set_sharp_area_down(self.result2_down)
        if self.swing_filter:
            self.result_up = self.sharp_detection.filter_swings("Demand", self.min_extremums, close, 10)
            self.sharp_detection.set_sharp_area_up(self.result_up)
            self.result_down = self.sharp_detection.filter_swings("Supply", self.max_extremums, close, 10)
            self.sharp_detection.set_sharp_area_down(self.result_down)
            self.result2_up = self.sharp_detection2.filter_swings("Demand", self.min_extremums, close, 10)
            self.sharp_detection2.set_sharp_area_up(self.result2_up)
            self.result2_down = self.sharp_detection2.filter_swings("Supply", self.max_extremums, close, 10)
            self.sharp_detection2.set_sharp_area_down(self.result2_down)

    def find_sources(self, data):
        # Find Source of Movements
        self.demand_sources = self.sharp_detection.get_source_of_movement("Demand", data)
        self.demand_sources += self.sharp_detection2.get_source_of_movement("Demand", data)

        self.supply_sources = self.sharp_detection.get_source_of_movement("Supply", data)
        self.supply_sources += self.sharp_detection2.get_source_of_movement("Supply", data)

    def update_fresh_sources(self, fresh_sources, type, last_candle):
        for fresh_source in fresh_sources:
            fresh_source['End'] = len(self.data)
            fresh_source['EndTime'] = last_candle['Time']
            if type == "Demand":
                if self.data[-1]['Low'] <= fresh_source['UpPrice']:
                    fresh_sources.remove(fresh_source)
            if type == "Supply":
                if self.data[-1]['High'] >= fresh_source['DownPrice']:
                    fresh_sources.remove(fresh_source)


    def get_last_source(self, sources):
        last_source = sources[0]
        for i in range(len(sources)):
            if sources[i]['Start'] > last_source['Start']:
                last_source = sources[i]
        return last_source

    def find_new_source(self, data):
        demand_sources = self.sharp_detection.get_source_of_movement("Demand", data)
        if len(demand_sources) != 0 and demand_sources[-1]['StartTime'] > self.last_demand_source['StartTime']:
            demand_sources[-1]['ID'] = self.last_demand_source['ID'] + 1
            self.last_demand_source = demand_sources[-1]
            self.fresh_demand_sources.append(self.last_demand_source)
            self.draw_sharps([self.result_up[-1]])
        demand_sources = self.sharp_detection2.get_source_of_movement("Demand", data)
        if len(demand_sources) != 0 and demand_sources[-1]['StartTime'] > self.last_demand_source['StartTime']:
            demand_sources[-1]['ID'] = self.last_demand_source['ID'] + 1
            self.last_demand_source = demand_sources[-1]
            self.fresh_demand_sources.append(self.last_demand_source)
            self.draw_sharps([self.result2_up[-1]])
        supply_sources = self.sharp_detection.get_source_of_movement("Supply", data)
        if len(supply_sources) != 0 and supply_sources[-1]['StartTime'] > self.last_supply_source['StartTime']:
            supply_sources[-1]['ID'] = self.last_supply_source['ID'] + 1
            self.last_supply_source = supply_sources[-1]
            self.fresh_supply_sources.append(self.last_supply_source)
            self.draw_sharps([self.result_down[-1]])
        supply_sources = self.sharp_detection2.get_source_of_movement("Supply", data)
        if len(supply_sources) != 0 and supply_sources[-1]['StartTime'] > self.last_supply_source['StartTime']:
            supply_sources[-1]['ID'] = self.last_supply_source['ID'] + 1
            self.last_supply_source = supply_sources[-1]
            self.fresh_supply_sources.append(self.last_supply_source)
            self.draw_sharps([self.result2_down[-1]])

    def get_fresh_sources(self, origin_sources):
        fresh_sources = []
        for i in range(len(origin_sources)):
            if origin_sources[i]['End'] == len(self.data) - 1:
                fresh_sources.append(origin_sources[i])
        return fresh_sources

    def set_sources_id(self, sources):
        for i in range(len(sources)):
            sources[i]['ID'] = i+1

    def redraw_movements(self, fresh_sources, color):
        if len(fresh_sources) > 0:
            self.delete_sources(fresh_sources)
            self.draw_sources(fresh_sources, color)

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
            self.chart_tool.rectangle(names1, times1, prices1, times2, prices2, back=1)

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