from Combiners.BacktestCombiner import BacktestCombiner
from Combiners.EnterPositionCombiner import EnterPositionCombiner


# Main Parameters
combiner = 'Backtest'
new_time_frame = "H1"
backtests = [["H4", "H4", "M1", "SuperStrongSupportResistance", "GBPUSD"]]

# Enter Position Parameters
colors = ['#1254bb', '#62ba21']
width = 8

# Backtest Parameter
balance = 10000

if combiner == 'Backtest':
    combiner = BacktestCombiner(backtests, balance, new_time_frame)
elif combiner == 'EnterPosition':
    combiner = EnterPositionCombiner(backtests, new_time_frame, colors, width)

combiner.get_output()
