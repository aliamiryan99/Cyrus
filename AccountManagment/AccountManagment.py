from Shared.Variables import Variables


class RiskManagement:
    def __init__(self, ratio):
        self.risk_ratio = ratio

    def calculate(self, balance, symbol, open_price, stop_loss_price):
        if stop_loss_price == 0:
            return 0
        max_loss = (balance * self.risk_ratio) / 100
        lot = Variables.config.symbols_pip_value[symbol]
        volume = max_loss / (abs(stop_loss_price - open_price) * lot)
        if not Variables.config.symbols_with_usd[symbol]:
            volume /= stop_loss_price
        return volume

class BalanceManagement:
    def __init__(self, ratio):
        self.balance_ratio = ratio

    def calculate(self, balance, symbol, open_price, stop_loss_price):
        return (balance * self.balance_ratio) / 10 ** 5

