

from MetaTrader.MetaTraderBase import MetaTraderBase
from Configuration.Tools.MetaTraderHistoricalToolsConfig import ChartConfig
from Configuration.Trade.OnlineConfig import Config

#############################################################################
# Other required imports
#############################################################################

from time import sleep
from datetime import datetime
import pandas as pd


#############################################################################
# Class derived from ChartTools includes Data processor for PULL,SUB Data
#############################################################################

class MetaTraderChartToolsManager(MetaTraderBase):

    def __init__(self,
                 name="Polaris",
                 w_break=100,
                 delay=0.01,
                 broker_gmt=3,
                 verbose=False,
                 params=None):

        super().__init__(name=name, broker_gmt=broker_gmt, verbose=verbose)
        print("Connected")
        # This strategy's variables
        self.delay = delay
        self.verbose = verbose
        self._finished = False

        # Get Historical Data
        symbol = self.reporting.get_curr_symbol()

        if symbol == 0:
            self.connector.shutdown()
            super().__init__([], [], verbose)
            symbol = self.reporting.get_curr_symbol()

        if symbol == 0:
            self.meta_trader_connection = False
        else:
            self.meta_trader_connection = True
            time_frame = ChartConfig.time_frame
            if ChartConfig.auto_time_frame:
                period = self.reporting.get_period()
                time_frame = Config.timeframes_dic_rev[period]

            candles = ChartConfig.candles
            if ChartConfig.auto_candles:
                candles = self.reporting.get_bars_cnt()

            self.connector.send_hist_request(symbol=symbol, timeframe=Config.timeframes_dic[time_frame], count=candles)

            for i in range(w_break):
                sleep(delay)
                if symbol + '_' + time_frame in self.connector.history_db.keys():
                    break

            self.history = self.connector.history_db[symbol + '_' + time_frame]
            for item in self.history:
                item['Time'] = datetime.strptime(item['Time'], ChartConfig.date_format)
            print(pd.DataFrame(self.history))

            chart_config = ChartConfig(symbol, self.history, ChartConfig.tool_name, params)

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
