
from Simulation import Simulation
from time import sleep

managers = ["LocalBackTest", "LocalTools", "OnlineAlgorithm", "OnlineHistoricalTools", "OnlineRealTimeTools",
            "Market", "TelegramMessage", "GetOnlineTick", "Combiner"]

manager = "OnlineAlgorithm"

if __name__ == "__main__":
    if manager == "LocalBackTest":
        from Managers.BackTestTradeManager import BackTestLauncher
        launcher = BackTestLauncher()
        market_executed = launcher.run()
        Simulation.get_output(market_executed)

    if manager == "LocalTools":
        from Managers.LocalToolsManager import ChartLauncher
        launcher = ChartLauncher()
        launcher.launch()

    if manager == "OnlineAlgorithm":
        from Managers.OnlineTradeManager import OnlineLauncher
        print('Loading Algorithm...')
        launcher = OnlineLauncher()

        print('Running Algorithm...')
        launcher.run()

        print('Algorithm is running...')
        while not launcher.isFinished():
            sleep(1)

    if manager == "OnlineHistoricalTools":
        from Managers.MetaTraderHistoricalToolsManager import MetaTraderChartToolsManager
        print('Loading Algorithm...')
        launcher = MetaTraderChartToolsManager()

    if manager == "OnlineRealTimeTools":
        from Managers.MetaTraderRealTimeToolManager import MetaTraderRealTimeToolsManager
        print('Loading ...')
        launcher = MetaTraderRealTimeToolsManager()

        print('Running')
        launcher.run()

        print('Chart tool is running...')
        while not launcher.is_finished():
            sleep(1)

    if manager == "Market":
        from Configuration.Trade.MarketConfig import MarketConfig
        from Market.BackTestManager import BackTestManager
        from Market.OnlineManager import OnlineManager

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

    if manager == "TelegramMessage":
        from Managers.TelegramMessageManager import OnlineMessagingLauncher

        print('Loading Algorithm...')
        launcher = OnlineMessagingLauncher()

        print('Running Algorithm...')
        launcher.run()

        # Waits example termination
        print('Algorithm is running...')
        while not launcher.isFinished():
            sleep(1)

    if manager == "GetOnlineTick":
        from Managers.GetOnlineTickData import OnlineTickDataWriter
        print('Loading Data Writer...')
        launcher = OnlineTickDataWriter()

        # Starts example execution
        print('Running Data Writer...')
        launcher.run()

        # Waits example termination
        print('Data writer is running...')
        while not launcher.isFinished():
            sleep(1)

    if manager == "Combiner":
        from Managers.Combiner import *
        from Combiners.BacktestCombiner import BacktestCombiner
        from Combiners.EnterPositionCombiner import EnterPositionCombiner

        if combiner == 'Backtest':
            combiner = BacktestCombiner(backtests, balance, new_time_frame)
        elif combiner == 'EnterPosition':
            combiner = EnterPositionCombiner(backtests, new_time_frame, colors, arrow_size)

        combiner.get_output()
