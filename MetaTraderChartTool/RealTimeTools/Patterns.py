from MetaTrader.MetaTraderBase import MetaTraderBase
from MetaTraderChartTool.RealTimeTools.RealTimeTool import RealTimeTool

from AlgorithmFactory.AlgorithmPackages.Patterns import DoubleTopAndBottom
from AlgorithmFactory.AlgorithmPackages.Patterns import HeadAndShoulder


class Pattern(RealTimeTool):

    def __init__(self, chart_tool: MetaTraderBase, data, pattern_type, coefficient, scales):
        super().__init__(chart_tool, data)

        self.patter_type = pattern_type

        self.bottom_color = "220,40,20"
        self.top_color = "20,60,200"
        self.width = 3

        bottom_detected, top_detected = {}, {}
        if pattern_type == "DoubleTopAndBottom":
            bottom_detected, top_detected = DoubleTopAndBottom.get_all_double_top_bottom_scales(self.data, scales, coefficient)
        elif pattern_type == "HeadAndShoulder":
            bottom_detected, top_detected = HeadAndShoulder.get_all_head_and_shoulders(self.data, scales)

        self.draw("Bottom", bottom_detected, self.bottom_color)
        self.draw("Top", top_detected, self.top_color)

    def on_tick(self, time, bid, ask):
        pass

    def on_data(self, candle):
        self.data.pop(0)

        self.data.append(candle)

    def draw(self, type_name, detected_lists, color):
        for scale in list(detected_lists.keys()):
            detected_list = detected_lists[scale]
            names, times1, prices1, times2, prices2 = [], [], [], [], []
            for i in range(len(detected_list)):
                for j in range(1, len(detected_list[i])):
                    names.append(f"{self.patter_type} {i} {type_name} _ Scale {scale} _ Line {j}")
                    times1.append(detected_list[i][j-1]['Time'])
                    prices1.append(detected_list[i][j-1]['Price'])
                    times2.append(detected_list[i][j]['Time'])
                    prices2.append(detected_list[i][j]['Price'])
            self.chart_tool.trend_line(names, times1, prices1, times2, prices2, width=self.width, color=color)
