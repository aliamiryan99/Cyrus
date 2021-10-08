
# %% -----------|| Main Section ||----------
from datetime import datetime
import copy
from Simulation import Utility as Ut

from tqdm import tqdm

from Configuration.Trade.MarketConfig import MarketConfig
from Configuration.Trade.BackTestConfig import Config

from Simulation import Simulation
from Simulation import Outputs

from Market.Simulator import Simulator

from Shared.Variables import Variables
from Shared.Functions import Functions

data = {}


class BackTestManager:

    def __init__(self):
        self.symbols = MarketConfig.symbols

        self.start_indexes, self.end_indexes, self.algorithm_data_total, self.algorithm_start_indexes, \
            self.algorithm_end_indexes, self.trailing_data_total, self.trailing_start_indexes,\
            self.trailing_end_indexes = self.initialize_data()

        self.configs, self.market, self.algorithm_data, self.trailing_data, self.history_size, self.strategies, self.simulation, self.last_ticket, self.last_algorithm_signal_ticket,\
            self.algorithm_histories, self.trailing_histories, self.buy_open_positions_lens,\
            self.sell_open_positions_lens, self.last_buy_closed, self.last_sell_closed,\
            self.trade_buy_in_candle_counts, self.trade_sell_in_candle_counts, self.virtual_buys, self.virtual_sells, \
            self.recovery_trades = self.initialize_algorithms()

    def run(self):
        # Back Test
        back_test_length = self.end_indexes[self.symbols[0]] - self.start_indexes[self.symbols[0]]
        for ii in tqdm(range(back_test_length)):
            i = self.start_indexes[self.symbols[0]] + ii
            data_time = data[self.symbols[0]]['Time'][i]
            # Market Update Section
            self.simulation.update(data_time)

            for symbol in self.symbols:
                i = self.start_indexes[symbol] + ii
                data_time = data[symbol]['Time'][i]
                self.market.time = data_time

                # Select Symbol Configuration
                tick_candle = Functions.item_data_list_to_dic(data[symbol], i)

                #Debug Section
                # if data_time == datetime(year=2020, month=9, day=21, hour=22, minute=0):
                #     print(data_time)

                # Ignore Holidays
                if tick_candle['Volume'] == 0:
                    continue

                # Update History
                self.update_history(tick_candle, symbol)


        # Exit Section
        self.simulation.exit()
        return self.simulation

    @staticmethod
    def initialize_data():
        # Simulation init
        Variables.config = Config
        global data
        symbols = MarketConfig.symbols
        time_frame = MarketConfig.time_frame
        Config.time_frame_show = time_frame
        Config.symbols_list.clear()
        Config.symbols_dict.clear()
        for i in range(len(symbols)):
            symbol = symbols[i]
            Config.symbols_list.append(symbol)
            Config.symbols_dict[symbol] = i
            Config.symbols_show[symbol] = 1
        Simulation.initialize()
        start_time = datetime.strptime(Config.start_date, Config.date_format)
        end_time = datetime.strptime(Config.end_date, Config.date_format)
        # algorithm init
        data_total = Simulation.data
        start_indexes = {}
        end_indexes = {}

        for i in range(len(symbols)):
            symbol = symbols[i]
            start_indexes[symbol] = Outputs.index_date_v3(data_total[Config.symbols_dict[symbol]], start_time)
            end_indexes[symbol] = Outputs.index_date_v3(data_total[Config.symbols_dict[symbol]], end_time)

        data_algorithm_paths = []
        data_trailing_paths = []
        for i in range(len(symbols)):
            symbol = symbols[i]
            data_algorithm_paths += ["Data/" + Config.categories_list[symbol] + "/" + symbol +
                                     "/" + time_frame + ".csv"]
            data_trailing_paths += ["Data/" + Config.categories_list[symbol] + "/" + symbol +
                                    "/" + time_frame + ".csv"]
        algorithm_data = Ut.csv_to_df(data_algorithm_paths, date_format=Config.date_format)
        trailing_data = Ut.csv_to_df(data_trailing_paths, date_format=Config.date_format)

        algorithm_start_indexes = {}
        trailing_start_indexes = {}
        algorithm_end_indexes = {}
        trailing_end_indexes = {}
        for i in range(len(symbols)):
            symbol = symbols[i]
            algorithm_data[i] = algorithm_data[i][algorithm_data[i].Volume != 0]
            trailing_data[i] = trailing_data[i][trailing_data[i].Volume != 0]
            algorithm_start_indexes[symbol] = Outputs.index_date(algorithm_data[i], start_time)
            trailing_start_indexes[symbol] = Outputs.index_date(algorithm_data[i], start_time)
            algorithm_end_indexes[symbol] = Outputs.index_date(algorithm_data[i], end_time)
            trailing_end_indexes[symbol] = Outputs.index_date(algorithm_data[i], end_time)

        for symbol in symbols:
            data[symbol] = data_total[Config.symbols_dict[symbol]]

        return start_indexes, end_indexes, algorithm_data, algorithm_start_indexes, algorithm_end_indexes, \
            trailing_data, trailing_start_indexes, trailing_end_indexes

    def initialize_algorithms(self):
        global data
        algorithm_data = {}
        trailing_data = {}

        for i in range(len(self.symbols)):
            algorithm_data[self.symbols[i]] = self.algorithm_data_total[i].to_dict('Records')
            trailing_data[self.symbols[i]] = self.trailing_data_total[i].to_dict('Records')
        # history
        history_size = MarketConfig.history_size

        # Market ChartConfig
        start_time = datetime.strptime(Config.start_date, Config.date_format)
        end_time = datetime.strptime(Config.end_date, Config.date_format)
        simulation = Simulation.Simulation(Config.leverage, Config.balance, start_time, end_time)
        market = Simulator(simulation, start_time)
        configs = {}
        symbols = MarketConfig.symbols
        for i in range(len(symbols)):
            symbol = symbols[i]
            algo_data = \
                algorithm_data[symbol][self.algorithm_start_indexes[symbol] -
                                                     MarketConfig.history_size:self.algorithm_start_indexes[symbol]]
            configs[symbol] = MarketConfig(market, symbol, algo_data, MarketConfig.strategy_name)

        strategies = {}
        for symbol in symbols:
            strategies[symbol] = configs[symbol].strategy

        # OnlineLauncher Requirement
        last_ticket = 0
        last_algorithm_signal_ticket = {}
        algorithm_histories = {}
        trailing_histories = {}
        buy_open_positions_lens = {}
        sell_open_positions_lens = {}
        last_buy_closed = {}
        last_sell_closed = {}
        trade_buy_in_candle_counts = {}
        trade_sell_in_candle_counts = {}
        virtual_buys = {}
        virtual_sells = {}
        recovery_trades = {}
        for symbol in self.symbols:

            algorithm_histories[symbol] =\
                algorithm_data[symbol][self.algorithm_start_indexes[symbol] -
                                       history_size:self.algorithm_start_indexes[symbol]]
            trailing_histories[symbol] = \
                trailing_data[symbol][self.trailing_start_indexes[symbol] -
                                      history_size:self.trailing_start_indexes[symbol]]

            buy_open_positions_lens[symbol] = 0
            sell_open_positions_lens[symbol] = 0

            trade_buy_in_candle_counts[symbol] = 0
            trade_sell_in_candle_counts[symbol] = 0

            virtual_buys[symbol] = []
            virtual_sells[symbol] = []

            recovery_trades[symbol] = []

        return configs, market, algorithm_data, trailing_data, history_size, strategies, simulation, last_ticket,\
            last_algorithm_signal_ticket, algorithm_histories, trailing_histories, buy_open_positions_lens,\
            sell_open_positions_lens, last_buy_closed, last_sell_closed, trade_buy_in_candle_counts,\
            trade_sell_in_candle_counts, virtual_buys, virtual_sells, recovery_trades

    def update_history(self, tick_candle, symbol):
        # Algorithm Time ID
        current_time = Functions.get_time_id(tick_candle['Time'], self.configs[symbol].time_frame)
        last_candle_time = Functions.get_time_id(self.algorithm_histories[symbol][-1]['Time'], self.configs[symbol].time_frame)
        if current_time != last_candle_time:
            # New Candle Open Section
            last_candle = {"Time": tick_candle['Time'], "Open": tick_candle['Open'], "High": tick_candle['High'],
                           "Low": tick_candle['Low'], "Close": tick_candle['Close'], "Volume": tick_candle['Volume']}
            self.algorithm_histories[symbol].append(last_candle)
            self.algorithm_histories[symbol].pop(0)
            self.strategies[symbol].on_data(self.algorithm_histories[symbol][-1])
        else:
            # Update Last Candle Section
            self.algorithm_histories[symbol][-1]['High'] = max(self.algorithm_histories[symbol][-1]['High'],tick_candle['High'])
            self.algorithm_histories[symbol][-1]['Low'] = min(self.algorithm_histories[symbol][-1]['Low'], tick_candle['Low'])
            self.algorithm_histories[symbol][-1]['Close'] = tick_candle['Close']
            self.algorithm_histories[symbol][-1]['Volume'] += tick_candle['Volume']
            # Signal Section
            self.strategies[symbol].on_tick()
