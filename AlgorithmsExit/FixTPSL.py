
from Simulation.Config import Config


class FixTPSL:
    def __init__(self, symbol, tp, sl):
        self.symbol = symbol
        self.tp = tp
        self.sl = sl

    def on_data(self):
        pass

    def on_tick(self, data, position_type):    # position_type : (buy or sell)
        tp = self.tp * (10 ** -Config.symbols_pip[self.symbol])
        sl = self.sl * (10 ** -Config.symbols_pip[self.symbol])
        if position_type == 'buy':
            sl *= -1
        elif position_type == 'sell':
            tp *= -1
        return tp, sl

