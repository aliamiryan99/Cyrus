
class CandleTrailing:
    def __init__(self):
        self.closed_candle = False
        self.open_candle = False
        self.last_candle_direction = 0

    def on_data(self, history):
        if history[-2]['Close'] < history[-2]['Open']:
            self.last_candle_direction = -1
        elif history[-2]['Close'] > history[-2]['Open']:
            self.last_candle_direction = +1
        self.open_candle = True
        return

    def on_tick(self, history, entry_point, position_type, time):
        if self.open_candle:
            if entry_point == -1 or entry_point == len(history)-1:
                return False, 0
            if position_type == 'buy' and self.last_candle_direction == +1:
                return True, history[-1]['Close']
            if position_type == 'sell' and self.last_candle_direction == -1:
                return True, history[-1]['Close']
        return False, 0

    def on_tick_reset(self):
        self.open_candle = False
