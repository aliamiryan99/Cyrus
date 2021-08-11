from abc import abstractmethod


class AccountManagement:

    @abstractmethod
    def calculate(self, balance, symbol, open_price, stop_loss_price):
        pass
