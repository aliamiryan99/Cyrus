from AlgorithmFactory.AlgorithmPackages.RefinementOfSimpleIdea import RefinementSI


class SimpleIdeaRefinement:

    def __init__(self, symbol, data_history, win_inc, win_dec, pivot, price_mode, alpha):
        # Data window, moving average window
        self.win_inc = win_inc
        self.win_dec = win_dec
        self.window_size = max(win_inc, win_dec)
        self.symbol = symbol
        self.pivot = pivot
        self.price_mode = price_mode
        self.alpha = alpha
        self.candle_submitted = False
        len_window = len(data_history)
        if len_window <= self.window_size:
            raise Exception("window len should be greater than window size")
        self.data_window = data_history[-self.window_size-5:]

    def on_tick(self):
        signal, price = 0, 0
        if not self.candle_submitted:
            signal, price = RefinementSI.refinement_si(self.data_window, self.win_inc, self.win_dec, self.pivot, self.price_mode, self.alpha)
            if signal != 0:
                self.candle_submitted = True
        return signal, price

    def on_data(self, candle, cash):
        self.data_window.pop(0)
        self.data_window.append(candle)
        self.candle_submitted = False
        return 0, 0



