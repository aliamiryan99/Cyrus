from abc import abstractmethod
from MetaTraderChartTool.BasicChartTools import BasicChartTools


class Tool:

    @abstractmethod
    def __init__(self, data):
        self.data = data

    @abstractmethod
    def draw(self, chart_tools: BasicChartTools):
        pass
