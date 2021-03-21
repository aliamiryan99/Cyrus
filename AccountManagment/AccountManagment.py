from Simulation.Config import Config


class RiskManagement:
    def __init__(self, ratio):
        self.risk_ratio = ratio

    def calculate(self, balance, stop_loss, symbol):
        if stop_loss == 0:
            return 0
        max_loss = (balance * self.risk_ratio) / 100
        return (max_loss / stop_loss) / 10 ** Config.symbols_digit[symbol]


class BalanceManagement:
    def __init__(self, ratio):
        self.balance_ratio = ratio

    def calculate(self, balance, stop_loss, symbol):
        return (balance * self.balance_ratio) / 10 ** 5

