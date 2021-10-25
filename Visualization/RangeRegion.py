
from Visualization.Visualizer import Visualizer

from AlgorithmFactory.AlgorithmTools.Aggregate import aggregate_data
from AlgorithmFactory.AlgorithmTools.Range import *

from Indicators.MA import MovingAverage

from Visualization.BaseChart import *


class RangeRegion(Visualizer):

    def __init__(self, symbol, data, range_candle_threshold, up_timeframe, stop_target_margin, type1_enable,
                 type2_enable, one_stop_in_region, candle_breakout_threshold, max_candles, ma_enable, ma_type,
                 ma_period):
        self.data = data
        self.ma_enable = ma_enable

        next_time_frame = up_timeframe

        self.ma_o = MovingAverage(self.data, ma_type, "Close", ma_period)

        self.next_data = aggregate_data(data, next_time_frame)

        self.last_next_candle = self.next_data[-1]
        self.next_data = self.next_data[:-1]

        self.results, self.results_type = detect_range_region(self.next_data, range_candle_threshold,
                                                              candle_breakout_threshold, max_candles)

        self.extend_results = get_new_result_index(self.results, self.next_data, self.data, next_time_frame)

        get_proximal_region(self.data, self.extend_results)

        stop_target_margin *= 10 ** -Config.symbols_pip[symbol]
        self.breakouts_result = get_breakouts2(self.data, self.extend_results, stop_target_margin, type1_enable,
                                               type2_enable, one_stop_in_region)

        avg_pip, avg_percent = get_statistics_of_breakouts(self.data, self.breakouts_result)

        print(f"{avg_pip * 10 ** Config.symbols_pip[symbol] / 10} pip , {avg_percent*100} %")

    def draw(self, fig, height):
        # Range Box
        for result in self.extend_results:
            fig.patch([result['Start'], result['Start'], result['End'], result['End']],
                      [result['TopRegion'], result['BottomRegion'], result['BottomRegion'],
                       result['TopRegion']], alpha=0.1, color="black")

        # Setup 2
        for result in self.breakouts_result:
            if result is not None:
                fig.patch([result['X'], result['X'], result['Y'], result['Y']],
                          [result['StartPrice'], result['StopPrice'], result['StopPrice'],
                           result['StartPrice']], alpha=0.5, color="red")
                fig.patch([result['X'], result['X'], result['Y'], result['Y']],
                          [result['StartPrice'], result['TargetPrice'], result['TargetPrice'],
                           result['StartPrice']], alpha=0.5, color="blue")

        # Moving Average
        if self.ma_enable:
            fig.line(x=list(np.arange(len(self.data))), y=self.ma_o.values, color="blue", width=1)

        show(fig)

