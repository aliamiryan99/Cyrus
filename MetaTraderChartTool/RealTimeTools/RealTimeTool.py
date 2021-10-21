from abc import abstractmethod
from MetaTraderChartTool.BasicChartTools import BasicChartTools


class RealTimeTool:

    @abstractmethod
    def __init__(self, chart_tool: BasicChartTools, data):
        self.chart_tool = chart_tool
        self.data = data

    @abstractmethod
    def on_tick(self, time, bid, ask):
        pass

    @abstractmethod
    def on_data(self, candle):
        pass
