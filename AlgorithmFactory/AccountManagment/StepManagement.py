from AlgorithmFactory.AccountManagment.AccountManagment import AccountManagement


class StepManagement(AccountManagement):

    def __init__(self, ratio, step):
        self.ratio = ratio
        self.step = step
        self.balance = 0

    def calculate(self, balance, symbol, open_price, stop_loss_price):
        if self.balance == 0 or abs(balance/self.balance - 1) > self.step:
            self.balance = balance
        return (self.balance * self.ratio) / 10 ** 5
