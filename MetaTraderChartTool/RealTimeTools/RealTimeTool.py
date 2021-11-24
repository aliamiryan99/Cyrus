from abc import abstractmethod
from MetaTrader.MetaTraderBase import MetaTraderBase


class RealTimeTool:

    @abstractmethod
    def __init__(self, chart_tool: MetaTraderBase, data):
        self.chart_tool = chart_tool
        self.data = data

    @abstractmethod
    def on_tick(self, time, bid, ask):
        pass

    @abstractmethod
    def on_data(self, candle):
        pass
