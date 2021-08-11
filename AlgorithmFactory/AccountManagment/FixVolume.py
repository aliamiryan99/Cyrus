from AlgorithmFactory.AccountManagment.AccountManagment import AccountManagement


class FixVolume(AccountManagement):

    def __init__(self, volume):
        self.volume = volume

    def calculate(self, balance, symbol, open_price, stop_loss_price):
        return self.volume
