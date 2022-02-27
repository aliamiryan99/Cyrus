from MetaTrader.MetaTraderBase import MetaTraderBase
from MetaTrader.RealTimeTools.RealTimeTool import RealTimeTool

from AlgorithmFactory.AlgorithmPackages.Patterns import DoubleTopAndBottom
from AlgorithmFactory.AlgorithmPackages.Patterns import HeadAndShoulder


class Pattern(RealTimeTool):

    def __init__(self, chart_tool: MetaTraderBase, data, pattern_type, coefficient, scales, window):
        super().__init__(chart_tool, data)

        self.pattern_type = pattern_type
        self.scales = scales
        self.coefficient = coefficient

        self.bottom_color = "220,40,20"
        self.top_color = "20,60,200"
        self.width = 3

        self.calculate()
        self.pre_bottom_detected, self.pre_top_detected = self.bottom_detected, self.top_detected
        self.pattern_id = 1
        for scale in list(self.bottom_detected.keys()):
            self.draw_pattern("Bottom", self.bottom_detected[scale], scale, self.bottom_color)
        for scale in list(self.top_detected.keys()):
            self.draw_pattern("Top", self.top_detected[scale], scale, self.top_color)

        self.data = self.data[-window:]

        self.chart_tool.set_speed(1000)
        self.chart_tool.set_candle_start_delay(10)

    def on_tick(self, time, bid, ask):
        pass

    def on_data(self, candle):
        self.data.pop(0)

        self.calculate()
        self.draw()

        self.data.append(candle)

    def calculate(self):
        self.bottom_detected, self.top_detected = {}, {}
        if self.pattern_type == "DoubleTopAndBottom":
            self.bottom_detected, self.top_detected = DoubleTopAndBottom.get_all_double_top_bottom_scales(self.data, self.scales, self.coefficient)
        elif self.pattern_type == "HeadAndShoulder":
            self.bottom_detected, self.top_detected = HeadAndShoulder.get_all_head_and_shoulders(self.data, self.scales)

    def draw(self):
        self.draw_new_patterns("Bottom", self.bottom_detected, self.pre_bottom_detected, self.bottom_color)
        self.draw_new_patterns("Top", self.top_detected, self.pre_top_detected, self.top_color)

    def draw_new_patterns(self, name, detected_list, pre_detected_list, color):
        for scale in list(detected_list.keys()):
            if len(detected_list[scale]) != 0:
                if detected_list[scale][-1][-4]['Time'] > pre_detected_list[scale][-1][-4]['Time']:
                    self.draw_pattern(name, [detected_list[scale][-1]], scale, color)
                    pre_detected_list[scale][-1] = detected_list[scale][-1]

    def draw_pattern(self, type_name, detected_list, scale, color):
            names, times1, prices1, times2, prices2 = [], [], [], [], []
            for i in range(len(detected_list)):
                for j in range(1, len(detected_list[i])):
                    names.append(f"{self.pattern_type} {i} {type_name} _ Scale {scale} _ Line {self.pattern_id}")
                    times1.append(detected_list[i][j-1]['Time'])
                    prices1.append(detected_list[i][j-1]['Price'])
                    times2.append(detected_list[i][j]['Time'])
                    prices2.append(detected_list[i][j]['Price'])
                    self.pattern_id += 1
            self.chart_tool.trend_line(names, times1, prices1, times2, prices2, width=self.width, color=color)
