from abc import abstractmethod

class Market:

    @abstractmethod
    def buy(self):
        pass

    @abstractmethod
    def sell(self):
        pass

    @abstractmethod
    def buy_limit(self):
        pass

    @abstractmethod
    def sell_limit(self):
        pass

    @abstractmethod
    def close(self, ticket):
        pass

    @abstractmethod
    def close_all(self):
        pass

    @abstractmethod
    def get_open_positions(self):
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




