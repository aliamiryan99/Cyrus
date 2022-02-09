
from MetaTrader.MetaTraderBase import MetaTraderBase
from MetaTraderChartTool.RealTimeTools.RealTimeTool import RealTimeTool

from AlgorithmFactory.AlgorithmTools.CandleTools import *
from AlgorithmFactory.AlgorithmPackages.SharpDetection.SharpDetection import SharpDetection
from AlgorithmFactory.AlgorithmTools.LocalExtermums import *


class SupplyAndDemand(RealTimeTool):

    def __init__(self, chart_tool: MetaTraderBase, data, tr, minimum_candles, tr2, minimum_candles2, swing_filter):
        super().__init__(chart_tool, data)

        self.min_extremums, self.max_extremums = get_local_extermums(data, 10, 2)

        self.sharp_detection = SharpDetection(tr, minimum_candles)
        self.sharp_detection2 = SharpDetection(tr2, minimum_candles2)

        open, high, low, close = get_ohlc(data)
        self.result = self.sharp_detection.get_sharps(data, close)
        self.result2 = self.sharp_detection2.get_sharps(data, close)

        self.result2 = self.sharp_detection2.filter_intersections(self.result)
        self.sharp_detection2.set_sharp_area(self.result2)
        if swing_filter:
            self.result = self.sharp_detection.filter_swings(self.min_extremums, close, 10)
            self.sharp_detection.set_sharp_area(self.result)
            self.result2 = self.sharp_detection2.filter_swings(self.min_extremums, close, 10)
            self.sharp_detection2.set_sharp_area(self.result2)

        self.sources = self.sharp_detection.get_source_of_movement(data)
        self.sources += self.sharp_detection2.get_source_of_movement(data)

        self.area_id = 1
        self.source_area_id = 1
        self.last_min_id = 1
        self.last_max_id = 1
        self.draw_local_extremum(self.min_extremums, self.max_extremums)
        self.draw(self.result)
        self.draw(self.result2)
        self.draw_sources(self.sources)


    def on_tick(self, time, bid, ask):
        pass

    def on_data(self, candle):
        self.data.pop(0)

        self.data.append(candle)

    def draw(self, results):

        if len(results) != 0:
            names1, times1, prices1, times2, prices2 = [], [], [], [], []
            for i in range(len(results)):
                times1.append(self.data[results[i]['Start']]['Time'])
                prices1.append(self.data[results[i]['Start']]['Open'])
                times2.append(self.data[results[i]['Max']+1]['Time'])
                prices2.append(self.data[results[i]['Max']+1]['Open'])
                names1.append(f"SharpArea{self.area_id}")
                self.area_id += 1
            self.chart_tool.rectangle(names1, times1, prices1, times2, prices2, back=1)

    def draw_sources(self, results):
        if len(results) != 0:
            names1, times1, prices1, times2, prices2 = [], [], [], [], []
            for i in range(len(results)):
                times1.append(self.data[results[i]['Start']]['Time'])
                prices1.append(results[i]['UpPrice'])
                times2.append(self.data[results[i]['End']]['Time'])
                prices2.append(results[i]['DownPrice'])
                names1.append(f"SourceArea{self.source_area_id}")
                self.source_area_id += 1
            self.chart_tool.rectangle(names1, times1, prices1, times2, prices2, back=1, color="20,100,200")

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
