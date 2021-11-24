
# %% -----------|| Main Section ||----------


from Configuration.Trade.MarketConfig import MarketConfig

from Market.BackTestManager import BackTestManager
from Simulation import Simulation

from Market.OnlineManager import OnlineManager
from time import sleep

if MarketConfig.market == "Simulator":
    # Output Section
    launcher = BackTestManager()
    market_executed = launcher.run()
    Simulation.get_output(market_executed, backtest_with_market=True)

elif MarketConfig.market == "MetaTrader":
    launcher = OnlineManager()
    launcher.run()
    while not launcher.isFinished():
        sleep(1)
