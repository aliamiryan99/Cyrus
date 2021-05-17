
from Shared.Variables import Variables
from AlgorithmsOfRecovery import Tools


class CandleRecovery:

    def __init__(self, symbol, data, window_size, tp_mode, fix_tp, alpha_tp, volume_mode, alpha_volume):
        self.symbol = symbol
        self.alpha_volume = alpha_volume
        self.tp_mode = tp_mode
        self.volume_mode = volume_mode
        self.fix_tp = fix_tp * 10 ** -Variables.config.symbols_pip[symbol]
        self.alpha_tp = alpha_tp
        self.history = data[-window_size:]
        self.last_candle_direction = 0
        self.opened_data = False

    def on_data(self, candle):
        if self.history[-1]['Close'] < self.history[-1]['Open']:
            self.last_candle_direction = -1
        elif self.history[-1]['Close'] > self.history[-1]['Open']:
            self.last_candle_direction = 1
        self.opened_data = True
        self.history.pop(0)
        self.history.append(candle)

    def on_tick(self, open_positions):
        signal = self.detect_pattern(open_positions)
        if signal == 1:
            price, volume, tp, modify_array = self.get_tp_volume(open_positions)
            return {'Signal': 1, 'Price': price, 'TP': tp, 'Volume': volume}, modify_array
        elif signal == -1:
            price, volume, tp, modify_array = self.get_tp_volume(open_positions)
            return {'Signal': -1, 'Price': price, 'TP': tp, 'Volume': volume}, modify_array

        return {'Signal': 0, 'TP': 0, 'Volume': 0}, []

    def on_tick_end(self):
        self.opened_data = False

    def tp_touched(self, ticket):
        pass

    def detect_pattern(self, open_positions):
        if self.opened_data:
            if open_positions[0]['Type'] == 'Buy':
                if self.last_candle_direction == -1:
                    return 1
            elif open_positions[0]['Type'] == 'Sell':
                if self.last_candle_direction == 1:
                    return -1
        return 0

    def get_tp_volume(self, open_positions):
        price = self.history[-1]['Open']

        volume = Tools.calc_volume(open_positions, self.volume_mode, self.alpha_volume, self.fix_tp,
                                   self.history)

        tp = Tools.calc_tp(open_positions, price, self.tp_mode, self.alpha_tp, self.fix_tp)
        if open_positions[0]['Type'] == 'Sell':
            tp *= -1

        modify_array = []
        for position in open_positions:
            modify_array.append({'Ticket': position['Ticket'], 'TP': tp})

        return price, volume, tp, modify_array
