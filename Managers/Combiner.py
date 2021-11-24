from Combiners.BacktestCombiner import BacktestCombiner
from Combiners.EnterPositionCombiner import EnterPositionCombiner


# Main Parameters
combiner = 'EnterPosition'

# BackTest Parameters
new_time_frame = "H1"
backtests = [["H1", "H1", "M1", "SimpleIdea", "EURUSD"],
             ["H1", "H1", "M1", "SimpleIdeaModified", "EURUSD"]]

# Enter Position Parameters
colors = ['#1254bb', '#f2ba21']
arrow_size = 12

# Backtest Parameter
balance = 10000

if __name__ == "__main__":
    if combiner == 'Backtest':
        combiner = BacktestCombiner(backtests, balance, new_time_frame)
    elif combiner == 'EnterPosition':
        combiner = EnterPositionCombiner(backtests, new_time_frame, colors, arrow_size)

    combiner.get_output()
