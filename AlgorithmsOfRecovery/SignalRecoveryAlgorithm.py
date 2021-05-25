from Simulation.Config import Config
from AlgorithmsOfRecovery import Tools


class SignalRecovery:

    # tp mode : 1 : const TP, 2 : dynamic tp(candle) , 3 : dynamic tp(extremum), 4 : profit tp
    def __init__(self, symbol, data, window_size, tp_mode, fix_tp, tp_alpha, volume_mode, volume_alpha, price_th,
                 algorithm):
        self.symbol = symbol
        self.volume_alpha = volume_alpha
        self.volume_mode = volume_mode
        self.algorithm = algorithm
        self.tp_mode = tp_mode
        self.tp_alpha = tp_alpha
        self.fix_tp = fix_tp * 10 ** -Config.symbols_pip[self.symbol]
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
        if open_positions[0]['Type'] == 'Buy':
            if not candle['Close'] < open_positions[-1]['OpenPrice'] - self.price_th:
                self.signal, self.tick_signal = 0, 0
            if self.signal == 1 or self.tick_signal == 1:
                price = candle['Close']
                self.signal, self.tick_signal = 0, 0
                tp = Tools.calc_tp(open_positions, price, self.tp_mode, self.tp_alpha, self.fix_tp)

                volume = Tools.calc_volume(open_positions, self.volume_mode, self.volume_alpha, self.fix_tp,
                                           self.history)
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
                    tp = -Tools.calc_tp(open_positions, price, self.tp_mode, self.tp_alpha, self.fix_tp)

                    volume = Tools.calc_volume(open_positions, self.volume_mode, self.volume_alpha, self.fix_tp,
                                               self.history)
                    modify_array = []
                    for position in open_positions:
                        modify_array.append({'Ticket': position['Ticket'], 'TP': tp})
                    return {'Signal': -1, 'Price': price, 'TP': tp, 'Volume': volume}, modify_array
        return {'Signal': 0, 'TP': 0, 'Volume': 0}, []

    def on_tick_end(self):
        self.tick_signal, tick_price = self.algorithm.on_tick()

    def tp_touched(self, ticket):
        pass

