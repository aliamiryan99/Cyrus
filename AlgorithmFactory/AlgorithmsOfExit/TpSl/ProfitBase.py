
from Shared.Variables import Variables


class Fix:
    def __init__(self, symbol, tp, sl):
        self.symbol = symbol
        self.tp = tp * (10 ** -Variables.config.symbols_pip[self.symbol])
        self.sl = sl * (10 ** -Variables.config.symbols_pip[self.symbol])

    def on_data(self, candle):
        pass

    def on_tick(self, data, position_type):    # position_type : (buy or sell)
        tp, sl = self.tp, self.sl
        if position_type == 'Buy':
            sl *= -1
        elif position_type == 'Sell':
            tp *= -1
        return tp, sl

