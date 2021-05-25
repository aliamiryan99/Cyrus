from Combiners.BacktestCombiner import BacktestCombiner
from Combiners.EnterPositionCombiner import EnterPositionCombiner


# Main Parameters
combiner = 'EnterPosition'

# BackTest Parameters
new_time_frame = "D"
backtests = [["D", "D", "M1", "SimpleIdea", "EURUSD"],
             ["D", "D", "M1", "SimpleIdeaRefinement", "EURUSD"]]

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
