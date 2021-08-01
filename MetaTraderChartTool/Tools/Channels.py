
from MetaTraderChartTool.BasicChartTools import BasicChartTools
from AlgorithmTools.LocalExtermums import *

from AlgorithmTools.Channels import get_channels


class Channels:

    def __init__(self, data, extremum_window_start, extremum_window_end, extremum_window_step, extremum_mode, check_window, alpha):
        self.data = data

        self.up_channels, self.down_channels = get_channels(data, extremum_window_start, extremum_window_end, extremum_window_step, extremum_mode, check_window, alpha)

    def draw(self, chart_tool: BasicChartTools):

        ray = 0

        names_up, times1_up, prices1_up, times2_up, prices2_up = [], [], [], [], []
        names_down, times1_down, prices1_down, times2_down, prices2_down = [], [], [], [], []
        for i in range(len(self.up_channels)):
            names_up.append(f"UpChannel_UpLine{i}")
            names_down.append(f"UpChannel_DownLine{i}")

            times1_up.append(self.data[self.up_channels[i]['UpLine']['x'][0]]['Time'])
            times2_up.append(self.data[self.up_channels[i]['UpLine']['x'][1]]['Time'])
            prices1_up.append(self.up_channels[i]['UpLine']['y'][0])
            prices2_up.append(self.up_channels[i]['UpLine']['y'][1])

            times1_down.append(self.data[self.up_channels[i]['DownLine']['x'][0]]['Time'])
            times2_down.append(self.data[self.up_channels[i]['DownLine']['x'][1]]['Time'])
            prices1_down.append(self.up_channels[i]['DownLine']['y'][0])
            prices2_down.append(self.up_channels[i]['DownLine']['y'][1])


        chart_tool.trend_line(names_up, times1_up, prices1_up, times2_up, prices2_up, color="12,50,220", width=4, ray=ray)
        chart_tool.trend_line(names_down, times1_down, prices1_down, times2_down, prices2_down, color="12,50,220", width=4, ray=ray)

        names_up, times1_up, prices1_up, times2_up, prices2_up = [], [], [], [], []
        names_down, times1_down, prices1_down, times2_down, prices2_down = [], [], [], [], []
        for i in range(len(self.down_channels)):
            names_up.append(f"DownChannel_UpLine{i}")
            names_down.append(f"DownChannel_DownLine{i}")

            times1_up.append(self.data[self.down_channels[i]['UpLine']['x'][0]]['Time'])
            times2_up.append(self.data[self.down_channels[i]['UpLine']['x'][1]]['Time'])
            prices1_up.append(self.down_channels[i]['UpLine']['y'][0])
            prices2_up.append(self.down_channels[i]['UpLine']['y'][1])

            times1_down.append(self.data[self.down_channels[i]['DownLine']['x'][0]]['Time'])
            times2_down.append(self.data[self.down_channels[i]['DownLine']['x'][1]]['Time'])
            prices1_down.append(self.down_channels[i]['DownLine']['y'][0])
            prices2_down.append(self.down_channels[i]['DownLine']['y'][1])

        chart_tool.trend_line(names_up, times1_up, prices1_up, times2_up, prices2_up, color="220,50,12", width=4, ray=ray)
        chart_tool.trend_line(names_down, times1_down, prices1_down, times2_down, prices2_down, color="220,50,12", width=4, ray=ray)



