from Simulation.Config import Config

class CandleRecovery:

    def __init__(self, symbol, data, window_size, alpha, alpha_volume, mode, tp, volume_mode):
        self.symbol = symbol
        self.alpha = alpha
        self.alpha_volume = alpha_volume
        self.mode = mode
        self.volume_mode = volume_mode
        self.tp = tp * 10 ** -Config.symbols_pip[symbol]
        self.history = data[-window_size:]
        self.body_mean = {}
        self.position_type = {}
        self.fibo1 = {}
        self.fibo2 = {}
        self.limit_price = {}
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
        candle = self.history[-1]
        ticket = open_positions[0]['Ticket']
        if self.opened_data:
            if open_positions[0]['Type'] == 'Buy':
                if self.last_candle_direction == -1:
                    price = candle['Open']
                    volume = open_positions[-1]['Volume'] * self.alpha_volume
                    if self.volume_mode == 2:
                        volume = open_positions[-1]['Volume'] * (abs(self.history[-2]['Open'] - self.history[-1]['Open']) / self.tp) * self.alpha_volume
                    tp = 0
                    if self.mode == 2:
                        tp = self.tp
                    # volume = 0
                    # for position in open_positions:
                    #     volume += position['Volume']
                    # volume *= self.alpha_volume
                    modify_array = []
                    for position in open_positions:
                        modify_array.append({'Ticket': position['Ticket'], 'TP': tp})
                    return {'Signal': 1, 'Price': price, 'TP': tp, 'Volume': volume}, modify_array
            elif open_positions[0]['Type'] == 'Sell':
                if self.last_candle_direction == 1:
                    price = candle['Open']
                    volume = open_positions[-1]['Volume'] * self.alpha_volume
                    if self.volume_mode == 2:
                        volume = open_positions[-1]['Volume'] * (abs(self.history[-2]['Open'] - self.history[-1]['Open']) / self.tp) * self.alpha_volume
                    tp = 0
                    if self.mode == 2:
                        tp = -self.tp
                    # volume = 0
                    # for position in open_positions:
                    #     volume += position['Volume']
                    # volume *= self.alpha_volume
                    modify_array = []
                    for position in open_positions:
                        modify_array.append({'Ticket': position['Ticket'], 'TP': tp})
                    return {'Signal': -1, 'Price': price, 'TP': tp, 'Volume': volume}, modify_array
        return {'Signal': 0, 'TP': 0, 'Volume': 0}, []

    def on_tick_reset(self):
        self.opened_data = False

    def tp_touched(self, ticket):
        pass

