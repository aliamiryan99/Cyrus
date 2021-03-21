# Simulator

Simulate forex market in specific time range.

## Getting Started

### Dependencies

* Python 3.8

### Executing program

* How to run the script
```
python main.py
```

* main
```
We can choose what strategy is ran before running simulation in main script
```

## Simulation
```
Base script of simulator
```

## Simulation Config

* Config.py
```

DEBUG : if DEBUG is True the simulation running in debug mode
time_frame : ("D","H4","H1","M30",...)data must be exist
balance
leverage
spread : fix spraed in point
volum_digit : for example 2 -> at least 0.01 lot
candlestick_start_date : begenning time of candlestick chart
candlestick_end_date : ending time of candlestick chart
date_format : the start_date and end_date format
symbols_digit : specify the minimum digit for each symbol
symbols_show : wich symbols charts shoud be show


```

## Strategy

```
different strategies {
    strategy_dr_anvari.py
    strategy_dr_ghiasi.py
    strategy_mr_negatian.py
    strategy_mr_rahimi.py
    strategy_mr_asghari.py
}

strategy return the orders.h5
it`s have all orders of buy and sell with specific format
```

## Strategy Config

* config.py

```
DEBUG : if DEBUG is True the strategy running in debug mode
tp : fix take profit (strategy can dosen't use it)
sl : fix stop loss (strategy can dosen't use it)
volume : fix volume (strategy can dosen't use it)
time_frame : ("D","H4","H1","M30",...)data must be exist
start_date : begenning time of predict
end_date : ending time of predict
date_format : the start_date and end_date format

```

## Order format (order.csv)

```
[date, ticket, type, symbol, volume, T/P, S/L, price(the price must be between high and low of the specific candle, if price be zero position start with the open price)]
date : for example (2019-01-01 05:00:00) this must exist in majors data
ticket : a uniqe id
type : ('buy', 'sell', 'close', 'modify', 'buy_limit', sell_limit', 'buy_stop', 'sell_stop')
symbol : (EUROUSD, GBPUSD, NZDUSD, USDCAD, USDCHF, USDJPY, AUDUSD, XAUUSD)
volume : LOT
T/P : take profit
S/L : stop loss
price : the open price of order( low <= price <= high else orders ignored [if price == 0 the position price start with open price of candle])

```

## Type of orders

```
buy : simulator open a buy position if possible
sell : simulator open a sell position if possible
close : close the position with specific ticket if exist
buy_limit : simulator open a buy position if the symbol price become more than (price) and it's possible
sell_limit : simulator open a sell position if the symbol price become less than (price) and it's possible
buy_stop : stop a buy_limit order with specific ticket if exist
sell_stop : stop a sell_limit order with specific ticket if exist

```

## Version History

* 2.0
    * fixed bugs
    * created better interface
    * changed simulation structure
