import math
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta

start_date = 0
end_date = 0
total_profit = 0
total_profit_in_pip = 0
simulate = 0
o_positions = 0
average_profit = 0
variance_profit = 0
sharpe_ratio = 0
average_aum = 0
capacity = 0
max_pos_size = 0
long_trades = 0
short_trades = 0
won_long_trade = 0
won_short_trade = 0
largest_profit_trade = 0
largest_profit_trade_pip = 0
largest_loss_trade = 0
largest_loss_trade_pip = 0
average_profit_trade = 0
average_profit_trade_pip = 0
average_loss_trade = 0
average_loss_trade_pip = 0
maximum_consecutive_wins = 0
maximum_consecutive_wins_amount = 0
maximum_consecutive_losses = 0
maximum_consecutive_losses_amount = 0
maximal_consecutive_wins = 0
maximal_consecutive_wins_count = 0
maximal_consecutive_losses = 0
maximal_consecutive_losses_count = 0
average_consecutive_wins = 0
average_consecutive_losses = 0

maximum_absolute_drawdown = 0
maximum_absolute_drawdown_percent = 0
maximal_absolute_drawdown = 0
maximal_absolute_drawdown_percent = 0
maximum_relative_drawdown = 0
maximum_relative_drawdown_percent = 0
maximal_relative_drawdown = 0
maximal_relative_drawdown_percent = 0
maximum_relative_details = []
maximal_relative_details = []

ratio_of_longs = 0
frequency_of_bets = 0
average_holding_period = 0
annualized_turnover = 0
df_balance_history = 0
df_equity_history = 0
df_margin_history = 0
df_free_margin_history = 0
df_profit_history = 0


def init_outputs(profits, positions, simulation, balance_history, equity_history, margin_history, backtest_years, s_d,
                 e_d, t_p, df_balance, df_equity, df_margin, df_free_margin, df_profit):
    global average_profit, variance_profit, sharpe_ratio, average_aum, capacity, max_pos_size, long_trades, \
        short_trades, total_profit_in_pip, ratio_of_longs, frequency_of_bets, average_holding_period, \
        annualized_turnover, won_long_trade, won_short_trade, average_profit_trade, average_profit_trade_pip,\
        average_loss_trade, average_loss_trade_pip, largest_profit_trade, largest_profit_trade_pip,\
        largest_loss_trade, largest_loss_trade_pip, start_date, end_date, total_profit, simulate, o_positions, \
        df_balance_history, df_equity_history, df_margin_history, df_free_margin_history, df_profit_history
    global maximum_consecutive_wins, maximum_consecutive_wins_amount, maximum_consecutive_losses, \
        maximum_consecutive_losses_amount, maximal_consecutive_wins, maximal_consecutive_wins_count, \
        maximal_consecutive_losses, maximal_consecutive_losses_count, average_consecutive_wins, average_consecutive_losses
    global maximum_absolute_drawdown, maximum_absolute_drawdown_percent, maximal_absolute_drawdown, maximal_absolute_drawdown_percent,\
        maximum_relative_drawdown, maximum_relative_drawdown_percent, maximal_relative_drawdown, maximal_relative_drawdown_percent, maximum_relative_details, maximal_relative_details
    #   average profit
    start_date = s_d
    end_date = e_d
    total_profit = t_p
    o_positions = positions
    simulate = simulation
    df_equity_history = df_equity
    df_margin_history = df_margin
    df_free_margin_history = df_free_margin
    df_profit_history = df_profit
    sum = 0
    count = 0
    total_profit_in_pip = 0
    for position in positions:
        total_profit_in_pip += position[12]
    total_profit_in_pip = round(total_profit_in_pip, 2)
    for profit in profits:
        sum += profit[2]
        count += 1
    average_profit = round(sum / count, 5)

    #   variance profit
    sum = 0
    count = 0
    for profit in profits:
        sum += (profit[2] - average_profit) ** 2
        count += 1
    variance_profit = round(math.sqrt(sum / count), 5)

    # sharpe ratio
    try:
        sharpe_ratio = round(average_profit / variance_profit, 5)
    except:
        sharpe_ratio = 0

    #   average_aum, capacity
    sum = 0
    count = 0
    max = 0
    for i in range(len(balance_history)):
        sum += margin_history[i][2]
        count += 1
        aum = margin_history[i][2]
        if aum > max:
            max = aum
    average_aum = round(sum / count, 5)
    capacity = round(max, 5)

    #   max_pos_size, long_trades, short trades, won's, bet_cnt, ratio_of_longs, frequency_of_bets, annualized_turnover
    max_pos_size = 0
    long_trades = 0
    short_trades = 0
    won_short_trade = 0
    won_long_trade = 0
    bet_cnt = 0
    day_cnt = 0
    sum = 0
    sum_profit_trade = 0
    sum_profit_trade_pip = 0
    sum_loss_trade = 0
    sum_loss_trade_pip = 0
    pre_position = positions[0]
    for position in positions:
        size = simulation.cal_margin(position[1], position[4], position[5], position[3])
        sum += size
        if position[11] > 0:
            sum_profit_trade += position[11]
            sum_profit_trade_pip += position[12]
            if position[11] > largest_profit_trade:
                largest_profit_trade = position[11]
            if position[12] > largest_profit_trade_pip:
                largest_profit_trade_pip = position[12]
        else:
            sum_loss_trade += position[11]
            sum_loss_trade_pip += position[12]
            if position[11] < largest_loss_trade:
                largest_loss_trade = position[11]
            if position[12] < largest_loss_trade_pip:
                largest_loss_trade_pip = position[12]
        if size > max_pos_size:
            max_pos_size = size
        if position[1] == 'Buy':
            long_trades += 1
            if position[11] > 0:
                won_long_trade += 1
        else:
            short_trades += 1
            if position[11] > 0:
                won_short_trade += 1
        if position == pre_position:
            continue
        if position[1] == pre_position[1]:
            pre_position = position
            continue
        else:
            d1 = pre_position[0]
            d2 = position[8]
            day_cnt += abs((d2 - d1).days)
            bet_cnt += 1
        pre_position = position
    ratio_of_longs = round(long_trades / len(positions), 2)
    if backtest_years == 0:
        frequency_of_bets = 0
    else:
        frequency_of_bets = round(bet_cnt / backtest_years, 2)
    if bet_cnt == 0:
        average_holding_period = 0
    else:
        average_holding_period = round(day_cnt/(bet_cnt), 2)
    if average_aum == 0:
        annualized_turnover = 0
    else:
        annualized_turnover = (round(abs((balance_history[-1][2] / balance_history[0][2])) ** (1/float(backtest_years)), 3) - 1) * 100
        if total_profit < 0:
            annualized_turnover *= -1
    if (won_short_trade + won_long_trade) == 0:
        average_profit_trade = 0
        average_profit_trade_pip = 0
    else:
        average_profit_trade = round(sum_profit_trade / (won_short_trade + won_long_trade), 2)
        average_profit_trade_pip = round(sum_profit_trade_pip / (won_short_trade + won_long_trade), 2)
    if (len(positions) - (won_short_trade + won_long_trade)) == 0:
        average_loss_trade = 0
        average_loss_trade_pip = 0
    else:
        average_loss_trade = round(sum_loss_trade / (len(positions) - (won_short_trade + won_long_trade)), 2)
        average_loss_trade_pip = round(sum_loss_trade_pip / (len(positions) - (won_short_trade + won_long_trade)), 2)

    # consecutive

    consecutive_wins_cnt = 0
    consecutive_wins_amount = 0
    consecutive_wins_sum = 0
    consecutive_wins_n = 0
    consecutive_losses_cnt = 0
    consecutive_losses_amount = 0
    consecutive_losses_sum = 0
    consecutive_losses_n = 0
    for position in positions:
        if consecutive_wins_cnt == 0 and consecutive_losses_cnt == 0:
            if position[11] > 0:
                consecutive_wins_cnt += 1
                consecutive_wins_amount += position[11]
            else:
                consecutive_losses_cnt += 1
                consecutive_losses_amount += position[11]
        elif consecutive_wins_cnt > 0:
            if position[11] > 0:
                consecutive_wins_cnt += 1
                consecutive_wins_amount += position[11]
            else:
                consecutive_wins_sum += consecutive_wins_amount
                consecutive_wins_n += 1
                if consecutive_wins_cnt > maximum_consecutive_wins:
                    maximum_consecutive_wins = consecutive_wins_cnt
                    maximum_consecutive_wins_amount = consecutive_wins_amount
                if consecutive_wins_amount > maximal_consecutive_wins:
                    maximal_consecutive_wins = consecutive_wins_amount
                    maximal_consecutive_wins_count = consecutive_wins_cnt
                consecutive_wins_cnt = 0
                consecutive_wins_amount = 0
                consecutive_losses_cnt += 1
                consecutive_losses_amount += position[11]
        elif consecutive_losses_cnt > 0:
            if position[11] > 0:
                consecutive_losses_sum += consecutive_losses_amount
                consecutive_losses_n += 1
                if maximum_consecutive_losses < consecutive_losses_cnt:
                    maximum_consecutive_losses = consecutive_losses_cnt
                    maximum_consecutive_losses_amount = consecutive_losses_amount
                if maximal_consecutive_losses > consecutive_losses_amount:
                    maximal_consecutive_losses = consecutive_losses_amount
                    maximal_consecutive_losses_count = consecutive_losses_cnt
                consecutive_losses_cnt = 0
                consecutive_losses_amount = 0
                consecutive_wins_cnt += 1
                consecutive_wins_amount += position[11]
            else:
                consecutive_losses_cnt += 1
                consecutive_losses_amount += position[11]
    if consecutive_wins_cnt > 0:
        consecutive_wins_sum += consecutive_wins_amount
        consecutive_wins_n += 1
        if consecutive_wins_cnt > maximum_consecutive_wins:
            maximum_consecutive_wins = consecutive_wins_cnt
            maximum_consecutive_wins_amount = consecutive_wins_amount
        if consecutive_wins_amount > maximal_consecutive_wins:
            maximal_consecutive_wins = consecutive_wins_amount
            maximal_consecutive_wins_count = consecutive_wins_cnt
    elif consecutive_losses_cnt > 0:
        consecutive_losses_sum += consecutive_losses_amount
        consecutive_losses_n += 1
        if maximum_consecutive_losses < consecutive_losses_cnt:
            maximum_consecutive_losses = consecutive_losses_cnt
            maximum_consecutive_losses_amount = consecutive_losses_amount
        if maximal_consecutive_losses > consecutive_losses_amount:
            maximal_consecutive_losses = consecutive_losses_amount
            maximal_consecutive_losses_count = consecutive_losses_cnt

    if consecutive_wins_n == 0:
        average_consecutive_wins = 0
    else:
        average_consecutive_wins = round(consecutive_wins_sum / consecutive_wins_n)
    if consecutive_losses_n == 0:
        average_consecutive_losses
    else:
        average_consecutive_losses = round(consecutive_losses_sum / (consecutive_losses_n))

    init_balance = balance_history[0][2]
    max_balance = balance_history[0][2]
    current_balance = balance_history[0][2]
    i = 0
    max_i = 0
    for position in positions:
        current_balance += position[11]
        relative_diff = max_balance - current_balance
        absolute_diff = init_balance - current_balance
        if relative_diff > maximum_relative_drawdown:
            maximum_relative_drawdown = abs(relative_diff)
            maximum_relative_drawdown_percent = (abs(relative_diff)/max_balance) * 100
            maximum_relative_details = [max_balance, current_balance, positions[max_i][0], positions[i][0]]
        if (relative_diff/max_balance) * 100 > maximal_relative_drawdown_percent:
            maximal_relative_drawdown = abs(relative_diff)
            maximal_relative_drawdown_percent = (abs(relative_diff) / max_balance) * 100
            maximal_relative_details = [max_balance, current_balance, positions[max_i][0], positions[i][0]]
        if absolute_diff > maximum_absolute_drawdown:
            maximum_absolute_drawdown = abs(absolute_diff)
            maximum_absolute_drawdown_percent = (abs(absolute_diff) / init_balance) * 100
        if (absolute_diff/init_balance) * 100 > maximal_absolute_drawdown_percent:
            maximal_absolute_drawdown = abs(absolute_diff)
            maximal_absolute_drawdown_percent = (abs(absolute_diff) / init_balance) * 100

        if current_balance > max_balance:
            max_balance = current_balance
            max_i = i
        i += 1
    print(f"{max_balance} , {current_balance}")

    maximum_absolute_drawdown = round(maximum_absolute_drawdown, 2)
    maximum_absolute_drawdown_percent = round(maximum_absolute_drawdown_percent, 2)
    maximal_absolute_drawdown = round(maximal_absolute_drawdown, 2)
    maximal_absolute_drawdown_percent = round(maximal_absolute_drawdown_percent, 2)
    maximum_relative_drawdown = round(maximum_relative_drawdown, 2)
    maximum_relative_drawdown_percent = round(maximum_relative_drawdown_percent, 2)
    maximal_relative_drawdown = round(maximal_relative_drawdown, 2)
    maximal_relative_drawdown_percent = round(maximal_relative_drawdown_percent, 2)


def index_date(data, date):
    start = 0
    end = len(data) - 1
    if date < data.iloc[start]['Time'] or date > data.iloc[end]['Time']:
        return -1
    i = 0
    while start <= end:
        i = int((start + end) / 2)
        if data.iloc[i]['Time'] == date:
            return i
        elif data.iloc[i]['Time'] < date:
            start = i + 1
        elif data.iloc[i]['Time'] > date:
            end = i - 1
    if data.iloc[i]['Time'] <= date:
        return i
    else:
        return i-1


def index_date_v2(data, date):
    start = 0
    end = len(data) - 1
    if date < data[start]['Time'] or date > data[end]['Time']:
        return -1
    i = 0
    while start <= end:
        i = int((start + end) / 2)
        if data[i]['Time'] == date:
            return i
        elif data[i]['Time'] < date:
            start = i + 1
        elif data[i]['Time'] > date:
            end = i - 1
    if data[i]['Time'] <= date:
        return i
    else:
        return i - 1


def index_date_v3(data, date):
    start = 0
    end = len(data['Time']) - 1
    if date < data['Time'][start] or date > data['Time'][end]:
        return -1
    i = 0
    while start <= end:
        i = int((start + end) / 2)
        if data['Time'][i] == date:
            return i
        elif data['Time'][i] < date:
            start = i + 1
        elif data['Time'][i] > date:
            end = i - 1
    if data['Time'][i] <= date:
        return i
    else:
        return i - 1

num = 0
def draw_chart(df, title):
    # style
    plt.style.use('seaborn-darkgrid')

    # create a color palette
    palette = plt.get_cmap('Set1')

    # multiple line plot
    global num
    if num == 5:
        num = 0
    for column in df.drop('x', axis=1):
        num += 1
    plt.plot(df['x'], df[column], marker='', color=palette(num), linewidth=1, alpha=0.9, label=column)

    # Add legend
    plt.legend(loc=2, ncol=2)

    # Add titles
    plt.title(title, loc='left', fontsize=16, fontweight=0, color='orange')
    plt.xlabel("Time")
    plt.ylabel(title)
    plt.show()


def print_help():
    print('WAP commands :')
    print('     balance -> get the balance history chart')
    print('     equity -> get the equity history chart')
    print('     equity_percent -> get the equity percent history chart')
    print('     free_margin -> get the free margin history chart')
    print('     profit -> get the daily profit history chart')
