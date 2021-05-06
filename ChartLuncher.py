from Simulation import Utility as ut
from Simulation import Outputs

from Simulation.Config import Config as SimulationConfig
from Visualization.Config import Config
from Visualization import BaseChart


from bokeh.io import output_file
import os
from datetime import datetime


class ChartLauncher:

    def __init__(self):
        data_show_paths = ["Data/" + SimulationConfig.categories_list[Config.symbol] + "/" + Config.symbol + "/" + Config.time_frame + ".csv"]
        start_time = datetime.strptime(Config.start_date, Config.date_format)
        end_time = datetime.strptime(Config.end_date, Config.date_format)
        self.data_df = ut.csv_to_df(data_show_paths, date_format=Config.date_format)[0]
        self.start_index = Outputs.index_date(self.data_df, start_time)
        self.end_index = Outputs.index_date(self.data_df, end_time)
        self.data_df = self.data_df.iloc[self.start_index:self.end_index + 1]

        if not Config.holidays_show:
            self.data_df = self.data_df[self.data_df.Volume != 0]

        self.data = self.data_df.to_dict("Records")

        self.config = Config(self.data)

        output_dir = "Visualization/Outputs/" + Config.name + "/" + Config.time_frame + "/"
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        output_file(output_dir + Config.symbol + ".html")

        self.fig = BaseChart.get_base_fig(self.data_df, Config.symbol)

        self.visualizer = self.config.visualizer

    def launch(self):
        self.visualizer.draw(self.fig, Config.secondary_fig_height)


launcher = ChartLauncher()
launcher.launch()