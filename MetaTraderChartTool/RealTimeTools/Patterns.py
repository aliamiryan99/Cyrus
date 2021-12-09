from MetaTrader.MetaTraderBase import MetaTraderBase
from MetaTraderChartTool.RealTimeTools.RealTimeTool import RealTimeTool

from AlgorithmFactory.AlgorithmPackages.Patterns import DoubleTopAndBottom
from AlgorithmFactory.AlgorithmTools.CandleTools import get_body_mean
from AlgorithmFactory.AlgorithmTools import LocalExtermums


class Pattern(RealTimeTool):

    def __init__(self, chart_tool: MetaTraderBase, data, pattern_type, extremum_window, extremum_mode):
        super().__init__(chart_tool, data)

        self.patter_type = pattern_type

        tr = get_body_mean(data, len(data)) * 0.3
        min_extemums, max_extremums = LocalExtermums.get_local_extermums(data, extremum_window, extremum_mode)

        detected_list = DoubleTopAndBottom.get_double_tops(self.data, max_extremums, tr)

        self.draw(detected_list)

    def on_tick(self, time, bid, ask):
        pass

    def on_data(self, candle):
        self.data.pop(0)

        self.data.append(candle)

    def draw(self, detected_list):
        names, times1, prices1, times2, prices2 = [], [], [], [], []
        for i in range(len(detected_list)):
            for j in range(1, len(detected_list[i])):
                names.append(f"{self.patter_type} {i} _ lien {j}")
                times1.append(detected_list[i][j-1]['Time'])
                prices1.append(detected_list[i][j-1]['Price'])
                times2.append(detected_list[i][j]['Time'])
                prices2.append(detected_list[i][j]['Price'])
        self.chart_tool.trend_line(names, times1, prices1, times2, prices2, width=2)
