
from MetaTraderChartTool.BasicChartTools import BasicChartTools
from MetaTraderChartTool.Tools.Tool import Tool
from AlgorithmFactory.AlgorithmTools.Range import *
from Configuration.Trade.OnlineConfig import Config
from AlgorithmFactory.AlgorithmTools.Aggregate import aggregate_data


class RangeRegion(Tool):

    def __init__(self, symbol, data, range_candle_threshold, up_timeframe, stop_target_margin):
        super().__init__(data)

        # diff_time = data[1]['Time'] - data[0]['Time']
        # period = diff_time.seconds//60 + diff_time.days * 1440
        # time_frame = Config.timeframes_dic_rev[period]
        # next_time_frame = time_frame
        # keys = list(Config.timeframes_dic.keys())
        # for i in range(len(keys)-1):
        #     if time_frame == keys[i]:
        #         next_time_frame = keys[i+1]

        next_time_frame = up_timeframe

        self.next_data = aggregate_data(data, next_time_frame)

        self.results, self.results_type = detect_range_region(self.next_data, range_candle_threshold)

        self.extend_results = get_new_result_index(self.results, self.next_data, self.data, next_time_frame)

        get_proximal_region(self.data, self.extend_results)

        stop_target_margin *= 10 ** -Config.symbols_pip[symbol]
        self.breakouts_result = get_breakouts2(self.data, self.extend_results, stop_target_margin)

    def draw(self, chart_tool: BasicChartTools):

        # Range Box
        names, times1, prices1, times2, prices2 = [], [], [], [], []
        for i in range(len(self.results)):
            result = self.results[i]

            if result['End'] >= len(self.next_data):
                end_time = self.next_data[-1]['Time'] + (self.next_data[-1]['Time'] - self.next_data[-2]['Time'])
            else:
                end_time = self.next_data[result['End']]['Time']
            names.append(f"RangeRegion{i}")
            times1.append(self.next_data[result['Start']]['Time'])
            prices1.append(result['BottomRegion'])
            times2.append(end_time)
            prices2.append(result['TopRegion'])

        chart_tool.rectangle(names, times1, prices1, times2, prices2)

        # Fibo Ranges
        names, times1, prices1, times2, prices2 = [], [], [], [], []
        for i in range(len(self.extend_results)):
            if self.results_type[i] != "Unknown":
                extend_result = self.extend_results[i]
                names.append(f"RangeRegionFibo{i}")
                times1.append(self.data[extend_result['Start']]['Time'])
                times2.append(self.data[extend_result['End']]['Time'])
                if self.results_type[i] == "Up":
                    prices1.append(extend_result['ProximalTop'])
                    prices2.append(extend_result['ProximalBottom'])
                elif self.results_type[i] == "Down":
                    prices1.append(extend_result['ProximalBottom'])
                    prices2.append(extend_result['ProximalTop'])

        chart_tool.fibonacci_retracement(names, times1, prices1, times2, prices2, color="0,0,0")

        # Total Braekouts Marker
        # names, times1, prices1,  = [], [], []
        # for i in range(len(self.blue_markers)):
        #     buy_index = self.blue_markers[i]
        #     names.append(f"BuyMarker{i}")
        #     times1.append(self.next_data[buy_index]['Time'])
        #     prices1.append(self.next_data[buy_index]['Close'])
        #
        # chart_tool.arrow(names, times1, prices1, 5, BasicChartTools.EnumAnchor.Right, color="0,0,255")
        #
        # names, times1, prices1 = [], [], []
        # for i in range(len(self.red_markers)):
        #     sell_index = self.red_markers[i]
        #     names.append(f"SellMarker{i}")
        #     times1.append(self.next_data[sell_index]['Time'])
        #     prices1.append(self.next_data[sell_index]['Close'])
        #
        # chart_tool.arrow(names, times1, prices1, 5, BasicChartTools.EnumAnchor.Right, color="255,0,0")

        # Setup 2
        names, times1, prices1, times2, prices2 = [], [], [], [], []
        names2, times12, prices12, times22, prices22 = [], [], [], [], []
        for i in range(len(self.breakouts_result)):
            result = self.breakouts_result[i]
            if result is not None:
                names.append(f"StopRegion{i}")
                times1.append(self.data[result['X']]['Time'])
                prices1.append(result['StartPrice'])
                times2.append(self.data[result['Y']]['Time'])
                prices2.append(result['StopPrice'])

                names2.append(f"TargetRegion{i}")
                times12.append(self.data[result['X']]['Time'])
                prices12.append(result['StartPrice'])
                times22.append(self.data[result['Y']]['Time'])
                prices22.append(result['TargetPrice'])

        chart_tool.rectangle(names, times1, prices1, times2, prices2, back=1, color='178,34,34')
        chart_tool.rectangle(names2, times12, prices12, times22, prices22, back=1, color='0,100,0')
