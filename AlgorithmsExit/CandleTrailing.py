
class CandleTrailing:
    def __init__(self):
        self.closed_candle = False

    def on_data(self, history):
        return

    def on_tick(self, history, entry_point, position_type, time):
        if time.hour >= 23:
            return True, history[-1]['Close']
        return False, 0
