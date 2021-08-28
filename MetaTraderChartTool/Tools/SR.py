from abc import abstractmethod
from MetaTraderChartTool.BasicChartTools import BasicChartTools


class SR(Tool):


    def __init__(self, data):
        self.data = data

    def draw(self, chart_tools: BasicChartTools):
        pass
