from Combiners.BacktestCombiner import BacktestCombiner
from Combiners.EnterPositionCombiner import EnterPositionCombiner


# Main Parameters
combiner = 'Backtest'

# BackTest Parameters
new_time_frame = "D"
backtests = [["H12", "H12", "M1", "SimpleIdea", "EURUSD"],
             ["H12", "H12", "M1", "SimpleIdeaRefinement", "EURUSD"]]

# Enter Position Parameters
colors = ['#1254bb', '#f2ba21']
arrow_size = 12

# Backtest Parameter
balance = 10000

if combiner == 'Backtest':
    combiner = BacktestCombiner(backtests, balance, new_time_frame)
elif combiner == 'EnterPosition':
    combiner = EnterPositionCombiner(backtests, new_time_frame, colors, arrow_size)

combiner.get_output()
