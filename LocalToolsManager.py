from Simulation import Utility as ut
from Simulation import Outputs

from Configuration.Trade.BackTestConfig import Config
from Configuration.Tools.LocalToolsConfig import ChartConfig
from Visualization import BaseChart


from bokeh.io import output_file
import os
from datetime import datetime
import pandas as pd


class ChartLauncher:

    def __init__(self, params=None, with_market=False):

        if params is not None:
            ChartConfig.symbol = params['Symbol']
            ChartConfig.time_frame = params['TimeFrame']
            if with_market:
                ChartConfig.backtest[0] = params['TimeFrame']
            else:
                ChartConfig.backtest[0] = f"{params['TimeFrame']}_{params['TimeFrame']}_M1"

        if ChartConfig.with_back_test:
            backtest = ChartConfig.backtest
            self.positions = pd.read_excel(f"Outputs/{backtest[1]}/{backtest[0]}/{backtest[2]}/history.xlsx",
                          engine="openpyxl")
            self.positions = self.positions.sort_values(['TimeOpen'])
            self.positions = self.positions[self.positions.Symbol == ChartConfig.symbol]
            self.positions = self.positions.to_dict("Records")
            start_time = self.positions[0]['TimeOpen']
            end_time = self.positions[-1]['TimeClose']
        else:
            start_time = datetime.strptime(ChartConfig.start_date, ChartConfig.date_format)
            end_time = datetime.strptime(ChartConfig.end_date, ChartConfig.date_format)

        data_show_paths = ["Data/" + Config.categories_list[ChartConfig.symbol] + "/" + ChartConfig.symbol +
                           "/" + ChartConfig.time_frame + ".csv"]
        self.data_df = ut.csv_to_df(data_show_paths, date_format=ChartConfig.date_format)[0]
        self.start_index = Outputs.index_date(self.data_df, start_time)
        self.end_index = Outputs.index_date(self.data_df, end_time)
        self.data_df = self.data_df.iloc[self.start_index:self.end_index + 1]

        if not ChartConfig.holidays_show:
            self.data_df = self.data_df[self.data_df.Volume != 0]

        self.data = self.data_df.to_dict("Records")

        if ChartConfig.with_back_test:
            for position in self.positions:
                position['Index'] = Outputs.index_date_v2(self.data, position['TimeOpen'])
                if position['Index'] == -1:
                    position['Index'] = len(self.data) - 1
                position['IndexEnd'] = Outputs.index_date_v2(self.data, position['TimeClose'])
                if position['IndexEnd'] == -1:
                    position['IndexEnd'] = len(self.data) - 1

            positions_df = pd.DataFrame(self.positions)

        self.ChartConfig = ChartConfig(self.data, ChartConfig.visualizer, params=params)

        output_dir = "Visualization/Outputs/" + ChartConfig.visualizer + "/" + ChartConfig.time_frame + "/"
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        output_file(output_dir + ChartConfig.symbol + ".html")

        if ChartConfig.with_back_test:
            self.fig = BaseChart.get_back_test_fig(self.data_df, positions_df, ChartConfig.symbol, 0)
        else:
            self.fig = BaseChart.get_base_fig(self.data_df, ChartConfig.symbol)

        self.visualizer = self.ChartConfig.visualizer

    def launch(self):
        self.visualizer.draw(self.fig, ChartConfig.secondary_fig_height)


if __name__ == "__main__":
    launcher = ChartLauncher()
    launcher.launch()
