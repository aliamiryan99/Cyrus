
from Market.Market import Market
from Simulation.Simulation import Simulation
from Shared.Variables import Variables


class Simulator(Market):

    def __init__(self, simulation: Simulation, start_time):
        self.simulation = simulation
        self.last_ticket = 1
        self.time = start_time

    def buy(self, price, symbol, take_profit, stop_loss, volume):
        if take_profit != 0:
            take_profit = price + take_profit * 10 ** -Variables.config.symbols_pip[symbol]
        if stop_loss != 0:
            stop_loss = price - stop_loss * 10 ** -Variables.config.symbols_pip[symbol]
        self.simulation.buy(self.time, price, symbol, take_profit, stop_loss, volume, self.last_ticket)
        self.last_ticket += 1

    def sell(self, price, symbol, take_profit, stop_loss, volume):
        take_profit = price - take_profit * 10 ** -Variables.config.symbols_pip[symbol]
        stop_loss = price + stop_loss * 10 ** -Variables.config.symbols_pip[symbol]
        self.simulation.sell(self.time, price, symbol, take_profit, stop_loss, volume, self.last_ticket)
        self.last_ticket += 1

    def modify(self, ticket, take_profit, stop_loss):
        type, position = self.get_position(ticket)
        price = position['OpenPrice']
        symbol = position['Symbol']
        sign = 1
        if type == 'Sell':
            sign = -1
        if take_profit != 0:
            take_profit = price + sign * take_profit * 10 ** -Variables.config.symbols_pip[symbol]
        if stop_loss != 0:
            stop_loss = price - sign * stop_loss * 10 ** -Variables.config.symbols_pip[symbol]
        self.simulation.modify(ticket, take_profit, stop_loss)

    def close(self, ticket, price):
        type, position = self.get_position(ticket)
        self.simulation.close(self.time, price, position['Volume'], ticket)

    def close_partial(self, ticket, price, volume):
        self.simulation.close(self.time, price, volume, ticket)

    def close_all(self, symbol, price):
        self.simulation.close_all_symbol('buy', symbol, self.time, price)
        self.simulation.close_all_symbol('sell', symbol, self.time, price)

    def get_open_buy_positions(self):
        return self.simulation.open_buy_positions

    def get_open_sell_positions(self):
        return self.simulation.open_sell_positions

    # return tuple( type('Buy','Sell') , position )
    def get_position(self, ticket):
        return self.simulation.get_position(ticket)

    def get_balance(self):
        return self.simulation.balance

    def get_equity(self):
        return self.simulation.equity