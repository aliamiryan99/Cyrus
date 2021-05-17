from Simulation.Config import Config


class SignalRecovery:

    # tp mode : 1 : const TP, 2 : dynamic tp(candle) , 3 : dynamic tp(extremum), 4 : profit tp
    def __init__(self, symbol, data, window_size, alpha_volume, const_tp, price_th, algorithm, tp_mode):
        self.symbol = symbol
        self.alpha_volume = alpha_volume
        self.algorithm = algorithm
        self.tp_mode = tp_mode
        self.const_tp = const_tp
        self.signal = 0
        self.price = 0
        self.tick_signal = 0
        self.tick_price = 0
        self.price_th = price_th * 10 ** -Config.symbols_pip[symbol]
        self.history = data[-window_size:]
        self.position_type = {}
        self.limit_price = {}

    def on_data(self, candle):
        self.history.pop(0)
        self.history.append(candle)
        self.signal, self.price = self.algorithm.on_data(candle, 0)

    def on_tick(self, open_positions):
        candle = self.history[-1]
        ticket = open_positions[0]['Ticket']
        if open_positions[0]['Type'] == 'Buy':
            if not candle['Close'] < open_positions[-1]['OpenPrice'] - self.price_th:
                self.signal, self.tick_signal = 0, 0
            if self.signal == 1 or self.tick_signal == 1:
                price = candle['Close']
                self.signal, self.tick_signal = 0, 0
                tp = 0
                if self.tp_mode == 1:
                    tp = self.const_tp * 10 ** -Config.symbols_pip[self.symbol]
                elif self.tp_mode == 2:
                    pass
                elif self.tp_mode == 3:
                    pass
                elif self.tp_mode == 4:
                    pass
                volume = open_positions[-1]['Volume'] * self.alpha_volume
                # volume = 0
                # for position in open_positions:
                #     volume += position['Volume']
                # volume *= self.alpha_volume
                modify_array = []
                for position in open_positions:
                    modify_array.append({'Ticket': position['Ticket'], 'TP': tp})
                return {'Signal': 1, 'Price': price, 'TP': tp, 'Volume': volume}, modify_array
        elif open_positions[0]['Type'] == 'Sell':
            if not candle['Close'] > open_positions[-1]['OpenPrice'] + self.price_th:
                self.signal, self.tick_signal = 0, 0
            if self.signal == -1 or self.tick_signal == -1:
                price = candle['Close']
                if price > open_positions[-1]['OpenPrice'] + self.price_th:
                    self.signal, self.tick_signal = 0, 0
                    tp = 0
                    if self.tp_mode == 1:
                        tp = -self.const_tp * 10 ** -Config.symbols_pip[self.symbol]
                    elif self.tp_mode == 2:
                        pass
                    elif self.tp_mode == 3:
                        pass
                    elif self.tp_mode == 4:
                        pass
                    volume = open_positions[-1]['Volume'] * self.alpha_volume
                    # volume = 0
                    # for position in open_positions:
                    #     volume += position['Volume']
                    # volume *= self.alpha_volume
                    modify_array = []
                    for position in open_positions:
                        modify_array.append({'Ticket': position['Ticket'], 'TP': tp})
                    return {'Signal': -1, 'Price': price, 'TP': tp, 'Volume': volume}, modify_array
        return {'Signal': 0, 'TP': 0, 'Volume': 0}, []

    def on_tick_end(self):
        self.tick_signal, tick_price = self.algorithm.on_tick()

    def tp_touched(self, ticket):
        pass

