from Combiners.BacktestCombiner import BacktestCombiner
from Combiners.EnterPositionCombiner import EnterPositionCombiner


# Main Parameters
combiner = 'EnterPosition'
new_time_frame = "D"
backtests = [["D", "D", "M1", "SI", "GBPUSD"], ["D", "D", "M1", "RSI", "GBPUSD"]]

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
