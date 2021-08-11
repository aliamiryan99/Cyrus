from Simulation import Utility as ut
from Simulation import Outputs

from Configuration.Trade.BackTestConfig import Config
from Configuration.Tools.LocalToolsConfig import ChartConfig
from Visualization import BaseChart


from bokeh.io import output_file
import os
from datetime import datetime


class ChartLauncher:

    def __init__(self):
        data_show_paths = ["Data/" + Config.categories_list[ChartConfig.symbol] + "/" + ChartConfig.symbol +
                           "/" + ChartConfig.time_frame + ".csv"]
        start_time = datetime.strptime(ChartConfig.start_date, ChartConfig.date_format)
        end_time = datetime.strptime(ChartConfig.end_date, ChartConfig.date_format)
        self.data_df = ut.csv_to_df(data_show_paths, date_format=ChartConfig.date_format)[0]
        self.start_index = Outputs.index_date(self.data_df, start_time)
        self.end_index = Outputs.index_date(self.data_df, end_time)
        self.data_df = self.data_df.iloc[self.start_index:self.end_index + 1]

        if not ChartConfig.holidays_show:
            self.data_df = self.data_df[self.data_df.Volume != 0]

        self.data = self.data_df.to_dict("Records")

        self.ChartConfig = ChartConfig(self.data, ChartConfig.visualizer)

        output_dir = "Visualization/Outputs/" + ChartConfig.visualizer + "/" + ChartConfig.time_frame + "/"
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        output_file(output_dir + ChartConfig.symbol + ".html")

        self.fig = BaseChart.get_base_fig(self.data_df, ChartConfig.symbol)

        self.visualizer = self.ChartConfig.visualizer

    def launch(self):
        self.visualizer.draw(self.fig, ChartConfig.secondary_fig_height)


launcher = ChartLauncher()
launcher.launch()
