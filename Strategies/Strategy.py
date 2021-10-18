from abc import abstractmethod
from Market.Market import Market


class Strategy:

    def __init__(self, market: Market, bid_data, ask_data):
        self.market = market
        self.bid_data = bid_data
        self.ask_data = ask_data

    @abstractmethod
    def on_tick(self):
        pass

    @abstractmethod
    def on_data(self, bid_candle, ask_candle):
        pass
