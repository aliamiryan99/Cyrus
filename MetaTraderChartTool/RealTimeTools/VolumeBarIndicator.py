
from MetaTraderChartTool.BasicChartTools import BasicChartTools
from MetaTraderChartTool.RealTimeTools.RealTimeTool import RealTimeTool

from Indicators.VolumeBarIndicator import VolumeBar
from Indicators.VolumeBarGenerator import VolumeGenerator

from Indicators.GpIndicator import GpIndicator

from datetime import timedelta
import pandas as pd


class VolumeBarIndicator(RealTimeTool):

    def __init__(self, chart_tool: BasicChartTools, data, prediction_multiplayer, window_size, vb_target_enable, vb_slow_enable, gp_enable, save_data):
        super().__init__(chart_tool, data)

        self.window_size = window_size

        self.vb_target_enable = vb_target_enable
        self.vb_slow_enable = vb_slow_enable
        self.gp_enable = gp_enable
        self.save_data = save_data

        self.data_window = 15

        vb_time_frame_cnt_fast = 5 * 12 * 24
        vb_time_frame_generator_target = 12
        vb_time_frame_generator_slow = 48

        self.slow_up_color = "60,179,113"
        self.slow_down_color = "255,0,0"
        self.target_up_color = "30,144,255"
        self.target_down_color = "255,255,0"
        self.width = 2

        self.volume_bar_fast = VolumeBar(vb_time_frame_cnt_fast)
        self.volume_bar_target = VolumeGenerator(vb_time_frame_generator_target)
        self.volume_bar_slow = VolumeGenerator(vb_time_frame_generator_slow)
        # self.volume_bar_target = VolumeBar(vb_time_frame_cnt_target)
        # self.volume_bar_slow = VolumeBar(vb_time_frame_cnt_slow)

        self.prediction_multiplayer = prediction_multiplayer
        deal_rate_enable = False

        self.gp_indicator = GpIndicator(prediction_multiplayer, deal_rate_enable)

        start_index, end_index = self.get_last_week_index(data)

        self.last_week_volume = 0
        for i in range(start_index, end_index):
            self.last_week_volume += data[i]['Volume']

        self.new_week = self.is_new_week(self.data[-1])
        self.new_day = False

        self.new_week_volume = 0
        for i in range(len(self.data)-1, start_index+1, -1):
            self.new_week_volume += data[i]['Volume']

        self.volume_bars_size_fast = len(self.volume_bar_fast.total_data)
        self.volume_bars_size_target = len(self.volume_bar_target.total_data)
        self.volume_bars_size_slow = len(self.volume_bar_slow.total_data)
        self.fast_line_cnt, self.target_line_cnt, self.slow_line_cnt = 0, 0, 0

        self.pre_target_len, self.pre_slow_len = 0, 0

        self.fast_correct, self.fast_wrong, self.target_correct, self.target_wrong, self.slow_correct, self.slow_wrong = 0, 0, 0, 0, 0, 0
        self.fast_pre_predict, self.target_pre_predict, self.slow_pre_predict = 0, 0, 0
        self.fast_gap_list , self.target_gap_list, self.slow_gap_list = [], [], []
        self.fast_gap_avg, self.target_gap_avg, self.slow_gap_avg = 0, 0, 0

        self.fast_saved_len, self.target_saved_len, self.slow_saved_len = 0, 0, 0

    def on_tick(self, time, bid, ask):
        tick = {'Time': time, 'Bid': bid, 'Ask': ask}
        self.new_week_volume += 1
        self.volume_bar_fast.update(tick, self.last_week_volume, self.new_week)
        # self.volume_bar_target.update(tick, self.last_week_volume, self.new_week)
        # self.volume_bar_slow.update(tick, self.last_week_volume, self.new_week)
        if self.volume_bar_fast.cum_value == 0:
            vb = self.volume_bar_fast.total_data[-1]
            self.volume_bar_target.update(vb)
            self.volume_bar_slow.update(vb)
            if self.save_data:
                if len(self.volume_bar_fast.total_data) - self.fast_saved_len > 100:
                    pd.DataFrame(self.volume_bar_fast.total_data).to_csv("Data/VolumeBar/Fast.csv")
                    self.fast_saved_len = len(self.volume_bar_fast.total_data)
                if len(self.volume_bar_target.total_data) - self.target_saved_len > 10:
                    pd.DataFrame(self.volume_bar_target.total_data).to_csv("Data/VolumeBar/Target.csv")
                    self.target_saved_len = len(self.volume_bar_target.total_data)
                if len(self.volume_bar_slow.total_data) - self.slow_saved_len > 5:
                    pd.DataFrame(self.volume_bar_slow.total_data).to_csv("Data/VolumeBar/Slow.csv")
                    self.slow_saved_len = len(self.volume_bar_slow.total_data)

        if self.volume_bar_fast.cum_value == 0 and len(self.volume_bar_fast.total_data) > 1:
            print("TrendLineFast")
            pre_vb = self.volume_bar_fast.total_data[-2]
            vb = self.volume_bar_fast.total_data[-1]
            self.volume_bars_size_fast = len(self.volume_bar_fast.total_data)
            self.fast_line_cnt += 1
            # self.chart_tool.trend_line([f"vb_{self.fast_line_cnt}_fast"], [pre_vb['Time']], [pre_vb['WAP']], [vb['Time']], [vb['WAP']])

            if self.volume_bar_target.cum_value == 0:
                print("TrendLineTarget")
                # pre_vb = self.volume_bar_target.total_data[-2]
                vb = self.volume_bar_target.total_data[-1]
                self.target_line_cnt += 1
                # self.chart_tool.trend_line([f"vb_{self.target_line_cnt}_target"], [pre_vb['Time']], [pre_vb['WAP']],
                #                            [vb['Time']], [vb['WAP']], color="255,255,0")
                if self.vb_target_enable:
                    color = self.target_up_color
                    if vb['Close'] < vb['Open']:
                        color = self.target_down_color
                    self.draw_candle(f"vb_{self.target_line_cnt}_target", color, vb)

            if self.volume_bar_slow.cum_value == 0:
                print("TrendLineSlow")
                # pre_vb = self.volume_bar_slow.total_data[-2]
                vb = self.volume_bar_slow.total_data[-1]
                self.slow_line_cnt += 1
                # self.chart_tool.trend_line([f"vb_{self.slow_line_cnt}_slow"], [pre_vb['Time']], [pre_vb['WAP']],
                #                            [vb['Time']], [vb['WAP']], color="0,0,255")
                if self.vb_slow_enable:
                    color = self.slow_up_color
                    if vb['Close'] < vb['Open']:
                        color = self.slow_down_color
                    self.draw_candle(f"vb_{self.target_line_cnt}_slow", color, vb)

            if self.gp_enable and len(self.volume_bar_slow.total_data) > 0:
                fast_data = self.volume_bar_fast.total_data[-self.data_window:]
                if len(self.volume_bar_target.total_data) >= self.data_window:
                    target_data = self.volume_bar_target.total_data[-self.data_window:]
                else:
                    target_data = self.volume_bar_target.total_data
                if len(self.volume_bar_slow.total_data) >= self.data_window:
                    slow_data = self.volume_bar_slow.total_data[-self.data_window:]
                else:
                    slow_data = self.volume_bar_slow.total_data

                target_obs = target_data + fast_data[self.get_pre_index_time(fast_data, target_data):]
                slow_obs = slow_data + target_data[self.get_pre_index_time(target_data, slow_data):] + fast_data[self.get_pre_index_time(fast_data, target_data):]

                target_predict_data = self.volume_bar_fast.total_data[self.get_pre_index_time(self.volume_bar_fast.total_data, target_data) - len(target_data) * 12:]
                slow_predict_data = self.volume_bar_fast.total_data[self.get_pre_index_time(self.volume_bar_fast.total_data, slow_data) - len(slow_data) * 48:]

                total_data = self.volume_bar_fast.total_data

                fastPredWAP, fastStdWAP, fastWAPInterpolate, fastStdInterpolate, targetPredWAP, targetStdWAP, \
                targetWAPInterpolate, targetStdInterpolate, slowPredWAP, slowStdWAP, slowWAPInterpolate,\
                slowStdInterpolate, xpred = self.gp_indicator.update(self.new_week, self.new_day, total_data,
                                                                     slow_data, target_data, fast_data, slow_obs, target_obs, target_predict_data, slow_predict_data, self.prediction_multiplayer+1)
                if fast_data[-1]['WAP'] - fast_data[-2]['WAP'] > 0:
                    direction = 1
                else:
                    direction = -1

                self.fast_pre_predict, self.fast_correct, self.fast_wrong = self.statistic_counter(self.fast_pre_predict, direction, self.fast_correct, self.fast_wrong, fastPredWAP)
                self.target_pre_predict, self.target_correct, self.target_wrong = self.statistic_counter(self.target_pre_predict, direction, self.target_correct, self.target_wrong, targetPredWAP)
                self.slow_pre_predict, self.slow_correct, self.slow_wrong = self.statistic_counter(self.slow_pre_predict, direction, self.slow_correct, self.slow_wrong, slowPredWAP)

                self.fast_gap_list.append(self.calculate_gap(fast_data, fastPredWAP, fastStdWAP))
                self.target_gap_list.append(self.calculate_gap(fast_data, targetPredWAP, targetStdWAP))
                self.slow_gap_list.append(self.calculate_gap(fast_data, slowPredWAP, slowStdWAP))

                self.draw_interpolate_line("FastInterpolate", fast_data, fastWAPInterpolate, len(fastWAPInterpolate), width=1, color="255,255,255")
                self.draw_predict_line("FastPredict", fast_data, fastPredWAP, color="255,255,255")

                self.draw_interpolate_line("TargetInterpolate", target_predict_data, targetWAPInterpolate, self.pre_target_len, width=2, color=self.target_up_color)
                self.draw_predict_line("TargetPredict", fast_data, targetPredWAP, color=self.target_up_color)
                self.pre_target_len = len(targetWAPInterpolate)

                self.draw_interpolate_line("SlowInterpolate", slow_predict_data, slowWAPInterpolate, self.pre_slow_len,
                                           width=3, color=self.slow_up_color)
                self.draw_predict_line("SlowPredict", fast_data, slowPredWAP, color=self.slow_up_color)
                self.pre_slow_len = len(slowWAPInterpolate)

                print(f"Fast Correct : {self.fast_correct} , Fast Wrong : {self.fast_wrong}")
                print(f"Target Correct : {self.target_correct} , Target Wrong : {self.target_wrong}")
                print(f"Slow Correct : {self.slow_correct} , Slow Wrong : {self.slow_wrong}")

                print(f"Fast Gap Avg : {sum(self.fast_gap_list)/len(self.fast_gap_list)}")
                print(f"Target Gap Avg : {sum(self.target_gap_list)/len(self.target_gap_list)}")
                print(f"Slow Gap Avg : {sum(self.slow_gap_list)/len(self.slow_gap_list)}")

        if self.new_day:
            self.new_day = False
        if self.new_week:
            self.new_week = False

    def on_data(self, candle):
        self.data.pop(0)

        self.new_day = self.is_new_day(candle)
        self.new_week = self.is_new_week(candle)
        if self.new_week:
            self.last_week_volume = self.new_week_volume
            self.new_week_volume = 0

        self.data.append(candle)

    def get_last_week_index(self, data):
        last_week = -1
        end_last_week_index = -1
        start_last_week_index = -1
        current_week = data[-1]['Time'].isocalendar()[1]
        for i in range(len(data)-1, 0, -1):
            week = data[i]['Time'].isocalendar()[1]
            if week != current_week:
                last_week = week
                end_last_week_index = i
                break
        for i in range(end_last_week_index-1, 0, -1):
            week = data[i]['Time'].isocalendar()[1]
            if week != last_week:
                start_last_week_index = i+1

        return start_last_week_index, end_last_week_index

    def is_new_week(self, candle):
        current_week = candle['Time'].isocalendar()[1]
        pre_candle_week = self.data[-1]['Time'].isocalendar()[1]
        if current_week != pre_candle_week:
            return True
        return False

    def is_new_day(self, candle):
        current_day = candle['Time'].day
        pre_candle_day = self.data[-1]['Time'].day
        if current_day != pre_candle_day:
            return True
        return False

    def get_pre_index_time(self, data, higher_data):
        for i in range(len(data)-1, 0, -1):
            if data[i]['Time'] <= higher_data[-1]['Time']:
                return i+1

    def draw_candle(self, name, color, candle):
        self.chart_tool.rectangle([name+"Rect"], [candle['StartTime']], [candle['Open']], [candle['Time']], [candle['Close']], color=color, width=self.width)
        self.chart_tool.trend_line([name+"Line"], [candle['MiddleTime']], [candle['Low']], [candle['MiddleTime']], [candle['High']], color=color, width=self.width)
        self.chart_tool.arrow([name+"WAP"], [candle['MiddleTime']], [(candle['Open']+candle['Close'])/2], 251, self.chart_tool.EnumArrowAnchor.Top, width=2)

    def draw_interpolate_line(self, base_name, data, interpolate_data, pre_len, width, color):
        names = [f"{base_name}{i}" for i in range(1, len(interpolate_data))]
        times_start = [data[i]['Time'] for i in range(len(interpolate_data) - 1)]
        prices_start = [interpolate_data[i][0] for i in range(len(interpolate_data) - 1)]
        times_end = [data[i]['Time'] for i in range(1, len(interpolate_data))]
        prices_end = [interpolate_data[i][0] for i in range(1, len(interpolate_data))]

        delete_names = [f"{base_name}{i}" for i in range(1, pre_len)]
        self.chart_tool.delete(delete_names)
        self.chart_tool.trend_line(names, times_start, prices_start, times_end, prices_end, width=width, color=color)

    def draw_predict_line(self, base_name, data, pred_wap, color):
        diff_time = timedelta(seconds=300)

        names = [f"{base_name}{i}" for i in range(1, self.prediction_multiplayer + 1)]
        times_start = [data[-1]['Time'] + diff_time * i for i in range(self.prediction_multiplayer)]
        prices_start = [pred_wap[i][0] for i in range(self.prediction_multiplayer)]
        times_end = [data[-1]['Time'] + diff_time * i for i in range(1, self.prediction_multiplayer + 1)]
        prices_end = [pred_wap[i][0] for i in range(1, self.prediction_multiplayer + 1)]

        self.chart_tool.delete(names)
        self.chart_tool.trend_line(names, times_start, prices_start, times_end, prices_end,
                                   style=self.chart_tool.EnumStyle.Dot, color=color)

    def calculate_gap(self, fast_data, pred_wap, std_wap):
        if pred_wap[1][0] - std_wap[1][0] < fast_data[-1]['WAP'] < pred_wap[1][0] + std_wap[1][0]:
            return 0
        else:
            return min(abs((pred_wap[1][0] - std_wap[1][0]) - fast_data[-1]['WAP']), abs((pred_wap[1][0] + std_wap[1][0]) - fast_data[-1]['WAP']))

    def statistic_counter(self, pre_predict, direction, correct, wrong, pred_wap):
        if pre_predict != 0:
            if pre_predict == direction:
                correct += 1
            else:
                wrong += 1
        if pred_wap[1][0] > pred_wap[0][0]:
            pre_predict = 1
        else:
            pre_predict = -1
        return pre_predict, correct, wrong
