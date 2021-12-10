from MetaTrader.MetaTraderBase import MetaTraderBase
from MetaTraderChartTool.RealTimeTools.RealTimeTool import RealTimeTool

from AlgorithmFactory.AlgorithmPackages.CandleSticks import CandleSticks


class CandleStick(RealTimeTool):

    def __init__(self, chart_tool: MetaTraderBase, data, candle_type, telegram):
        super().__init__(chart_tool, data)

        self.telegram_channel_name = "@polaris_candlestick_patterns"

        self.color = "40,180,60"
        self.width = 1
        self.candle_type = candle_type

        detected_list = CandleSticks.get_candlesticks(self.data, candle_type)
        self.last_index = 1
        self.draw(detected_list)

        self.data = self.data[-10:]

    def on_tick(self, time, bid, ask):
        pass

    def on_data(self, candle):
        self.data.pop(0)

        detected_list = CandleSticks.get_candlesticks(self.data, self.candle_type)
        if len(detected_list) > 0 and detected_list[-1]['Time'] == self.data[-1]['Time']:
            self.draw([detected_list[-1]])

        self.data.append(candle)

    def draw(self, detected_list):
        names, times, prices = [], [], []
        for i in range(len(detected_list)):
            names.append(f"{self.candle_type} {self.last_index}")
            times.append(detected_list[i]['Time'])
            prices.append(detected_list[i]['Price'])
            self.last_index += 1
        self.chart_tool.arrow(names, times, prices, 252, self.chart_tool.EnumArrowAnchor.Top, width=self.width, color=self.color)
