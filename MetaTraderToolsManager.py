

from MetaTraderChartTool.BasicChartTools import BasicChartTools
from Configuration.Tools.MetaTraderToolsConfig import ChartConfig
from Configuration.Trade.OnlineConfig import Config

#############################################################################
# Other required imports
#############################################################################

from threading import Thread, Lock
from time import sleep
from datetime import datetime
import pandas as pd


#############################################################################
# Class derived from ChartTools includes Data processor for PULL,SUB Data
#############################################################################

class MetaTraderChartToolsManager(BasicChartTools):

    def __init__(self,
                 _name="Polaris",
                 _delay=0.1,
                 _broker_gmt=3,
                 _verbose=False):

        super().__init__([],  # Registers itself as handler of pull Data via self.onPullData()
                         [],  # Registers itself as handler of sub Data via self.onSubData()
                         _verbose)
        print("Connected")
        # This strategy's variables
        self._delay = _delay
        self._verbose = _verbose
        self._finished = False

        # Get Historical Data

        symbol = self.reporting.get_curr_symbol()

        if symbol == 0:
            self.connector.shutdown()
            super().__init__([], [], _verbose)
            symbol = self.reporting.get_curr_symbol()

        time_frame = ChartConfig.time_frame

        self.connector.send_hist_request(_symbol=symbol,
                                          _timeframe=Config.timeframes_dic[time_frame],
                                          _count=ChartConfig.candles)
        sleep(4)
        self.history = self.connector._History_DB[symbol + '_' + time_frame]
        for item in self.history:
            item['Time'] = datetime.strptime(item['Time'], ChartConfig.date_format)
        print(pd.DataFrame(self.history))

        chart_config = ChartConfig(self.history, ChartConfig.tool_name)

        chart_config.tool.draw(self)



""" -----------------------------------------------------------------------------------------------
    -----------------------------------------------------------------------------------------------
    SCRIPT SETUP
    -----------------------------------------------------------------------------------------------
    -----------------------------------------------------------------------------------------------
"""
if __name__ == "__main__":

    # creates object with a predefined configuration: symbol list including EURUSD and GBPUSD
    print('Loading Algorithm...')
    launcher = MetaTraderChartToolsManager()

    print('Bye!!!')
