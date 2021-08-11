from AlgorithmFactory.AccountManagment.AccountManagment import AccountManagement


class BalanceManagement(AccountManagement):

    def __init__(self, ratio):
        self.ratio = ratio

    def calculate(self, balance, symbol, open_price, stop_loss_price):
        return (balance * self.ratio) / 10 ** 5
