from abc import abstractmethod


class Market:

    @abstractmethod
    def buy(self,  price, symbol, take_profit, stop_loss, volume):
        pass

    @abstractmethod
    def sell(self, price, symbol, take_profit, stop_loss, volume):
        pass

    @abstractmethod
    def modify(self, ticket, take_profit, stop_loss):
        pass

    @abstractmethod
    def close(self, ticket, price, volume):
        pass

    @abstractmethod
    def close_all(self, symbol, price):
        pass

    @abstractmethod
    def get_open_buy_positions(self):
        pass

    @abstractmethod
    def get_open_sell_positions(self):
        pass

    @abstractmethod
    def get_position(self, ticket):
        pass

    @abstractmethod
    def get_balance(self):
        pass

    @abstractmethod
    def get_equity(self):
        pass




