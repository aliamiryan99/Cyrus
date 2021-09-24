
from Market.Market import Market


class MetaTrader(Market):

    def __init__(self, online_manger):
        self.online_manger = online_manger

    def buy(self, price, symbol, take_profit, stop_loss, volume):
        self.online_manger.buy(symbol, volume, take_profit, stop_loss)

    def sell(self, price, symbol, take_profit, stop_loss, volume):
        self.online_manger.sell(symbol, volume, take_profit, stop_loss, )

    def modify(self, ticket, take_profit, stop_loss):
        self.modify(ticket, take_profit, stop_loss)

    def close(self, ticket, price):
        self.online_manger.close(ticket)

    def close_partial(self, ticket, price, volume):
        pass

    def close_all(self, symbol, price):
        self.online_manger._zmq._DWX_MTX_CLOSE_ALL_TRADES_()

    def get_open_buy_positions(self):
        open_buy_positions = []
        for symbol in self.online_manger.open_buy_trades.keys():
            open_buy_positions += self.online_manger.open_buy_trades[symbol]
        return open_buy_positions

    def get_open_sell_positions(self):
        open_sell_positions = []
        for symbol in self.online_manger.open_sell_trades.keys():
            open_sell_positions += self.online_manger.open_sell_trades[symbol]
        return open_sell_positions

    # return tuple( type('Buy','Sell') , position )
    def get_position(self, ticket):
        open_buy_positions = self.get_open_buy_positions()
        open_sell_positions = self.get_open_sell_positions()
        for position in open_buy_positions:
            if ticket == position['Ticket']:
                return 'Buy', position
        for position in open_sell_positions:
            if ticket == position['Ticket']:
                return 'Sell', position
        return False, False

    def get_balance(self):
        return self.online_manger.balance

    def get_equity(self):
        return self.online_manger.equity

