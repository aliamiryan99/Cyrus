
from MetaTraderChartTool.BasicChartTools import BasicChartTools
from MetaTraderChartTool.Tools.Tool import Tool
from AlgorithmFactory.AlgorithmTools.Range import detect_range_region
from Configuration.Trade.OnlineConfig import Config
from AlgorithmFactory.AlgorithmTools.Aggregate import aggregate_data


class RangeRegion(Tool):

    def __init__(self, symbol, data, range_candle_threshold):
        super().__init__(data)

        period = (data[1]['Time'] - data[0]['Time']).seconds//60
        time_frame = Config.timeframes_dic_rev[period]
        next_time_frame = time_frame
        keys = list(Config.timeframes_dic.keys())
        for i in range(len(keys)-1):
            if time_frame == keys[i]:
                next_time_frame = keys[i+1]

        self.next_data = aggregate_data(data, next_time_frame)

        self.results = detect_range_region(self.next_data, range_candle_threshold)

        self.area_length = 50 * 10 ** -Config.symbols_pip[symbol]
        self.blue_markers = []
        self.red_markers = []
        marker_activation = False
        result_i = 0
        for i in range(len(data)):
            if result_i != len(self.results) and data[i]['Time'] > self.next_data[self.results[result_i]['End']]['Time']:
                result_i += 1
                marker_activation = True
            if marker_activation:
                if data[i]['Close'] > self.results[result_i-1]['TopRegion']:
                    self.blue_markers.append(i)
                    marker_activation = False
                elif data[i]['Close'] < self.results[result_i-1]['BottomRegion']:
                    self.red_markers.append(i)
                    marker_activation = False

    def draw(self, chart_tool: BasicChartTools):

        names, times1, prices1, times2, prices2 = [], [], [], [], []
        for i in range(len(self.results)):
            result = self.results[i]
            names.append(f"RangeRegion{i}")
            times1.append(self.next_data[result['Start']]['Time'])
            prices1.append(result['BottomRegion'])
            times2.append(self.next_data[result['End']]['Time'])
            prices2.append(result['TopRegion'])

        chart_tool.rectangle(names, times1, prices1, times2, prices2, back=1)

        names, times1, prices1,  = [], [], []
        for i in range(len(self.blue_markers)):
            buy_index = self.blue_markers[i]
            names.append(f"BuyMarker{i}")
            times1.append(self.data[buy_index]['Time'])
            prices1.append(self.data[buy_index]['Close'])

        chart_tool.arrow(names, times1, prices1, 5, BasicChartTools.EnumAnchor.Right, color="0,0,255")

        names, times1, prices1 = [], [], []
        for i in range(len(self.red_markers)):
            sell_index = self.red_markers[i]
            names.append(f"SellMarker{i}")
            times1.append(self.data[sell_index]['Time'])
            prices1.append(self.data[sell_index]['Close'])

        chart_tool.arrow(names, times1, prices1, 5, BasicChartTools.EnumAnchor.Right, color="255,0,0")
