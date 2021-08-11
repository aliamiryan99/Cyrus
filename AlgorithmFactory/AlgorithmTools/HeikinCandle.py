import copy


class HeikinConverter:

    def __init__(self, first_candle):
        self.old = copy.deepcopy(first_candle)
        self.old['Open'] = (first_candle['Open'] + first_candle['Close']) / 2
        self.old['Close'] = (first_candle['Open'] + first_candle['High'] + first_candle['Low'] + first_candle['Close']) / 4

    def on_data(self, last_candle):
        self.old = self.convert(last_candle)
        return self.old

    def convert(self, candle):
        heikin = copy.deepcopy(candle)
        heikin['Open'] = (self.old['Open'] + self.old['Close']) / 2
        heikin['Close'] = (candle['Open'] + candle['High'] + candle['Low'] + candle['Close']) / 4
        heikin['High'] = max(candle['High'], heikin['Open'], heikin['Close'])
        heikin['Low'] = min(candle['Low'], heikin['Open'], heikin['Close'])
        return heikin

    def convert_many(self, data_history):
        heiking_data = [self.old]
        for candle in data_history:
            heiking_data.append(self.on_data(candle))
        return heiking_data

