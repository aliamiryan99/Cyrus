from MetaTrader.MetaTraderBase import MetaTraderBase
from MetaTraderChartTool.RealTimeTools.RealTimeTool import RealTimeTool

from AlgorithmFactory.AlgorithmPackages.CandleSticks import CandleSticks


class CandleStick(RealTimeTool):

    def __init__(self, chart_tool: MetaTraderBase, data, candle_type):
        super().__init__(chart_tool, data)

        self.candle_type = candle_type

        detected_list = CandleSticks.get_candlesticks(self.data, candle_type)

        self.draw(detected_list)

    def on_tick(self, time, bid, ask):
        pass

    def on_data(self, candle):
        self.data.pop(0)

        self.data.append(candle)

    def draw(self, detected_list):
        names, times, prices = [], [], []
        for i in range(len(detected_list)):
            names.append(f"{self.candle_type} {i}")
            times.append(self.data[detected_list[i][0]]['Time'])
            prices.append(self.data[detected_list[i][0]]['Low'])
        self.chart_tool.arrow(names, times, prices, 252, self.chart_tool.EnumArrowAnchor.Top)
