

class Config:
    DEBUG = False
    time_frame = "M1"
    time_frame_show = "D"
    balance = 10000
    leverage = 100

    # in point
    spreads = {'EURUSD': 10, 'GBPUSD': 20, 'NZDUSD': 30, 'USDCAD': 30, 'USDCHF': 20, 'USDJPY': 20,
               'AUDUSD': 20, 'XAUUSD': 30, 'XAUUSD.I': 30, 'XAGUSD': 30, 'US30USD': 60, 'USATECHUSD': 100, 'US500USD': 100,
               'INDEXUSD': 80, 'BTCUSD': 500, 'OILUSD': 80}

    volume_digit = 2    # for example 2 -> at least 0.01 lot
    max_volume = 200
    start_date = "01.01.2020 00:00:00.000"
    end_date = "01.10.2021 00:00:00.000"
    date_format = "%d.%m.%Y %H:%M:%S.%f"

    symbols_dict = {'EURUSD': 0, 'GBPUSD': 1, 'NZDUSD': 2, 'USDCAD': 3, 'USDCHF': 4, 'USDJPY': 5, 'AUDUSD': 6,
                       'XAUUSD': 7, 'XAGUSD': 8, 'US30USD': 9, 'USATECHUSD': 10, 'US500USD': 11, 'INDEXUSD': 12,
                    'BTCUSD': 13, 'OILUSD': 14, 'XAUUSD.I': 15}
    symbols_list = ['EURUSD', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY', 'AUDUSD',
                    'XAUUSD', 'XAGUSD', 'US30USD', 'USATECHUSD', 'US500USD', 'INDEXUSD', 'BTCUSD', 'OILUSD', 'XAUUSD.I']
    categories_list = {'EURUSD': 'Major', 'GBPUSD': 'Major', 'NZDUSD': 'Major', 'USDCAD': 'Major', 'USDCHF': 'Major',
                       'USDJPY': 'Major', 'AUDUSD': 'Major', 'XAUUSD': 'Metal', 'XAGUSD': 'Metal', 'US30USD': 'CFD',
                       'USATECHUSD': 'CFD', 'US500USD': 'CFD', 'INDEXUSD': 'CFD', 'BTCUSD': 'Crypto', 'OILUSD': 'CFD',
                       'XAUUSD.I': 'Metal'}

    symbols_pip = {'EURUSD': 5, 'GBPUSD': 5, 'NZDUSD': 5, 'USDCAD': 5, 'USDCHF': 5, 'USDJPY': 3,
                   'AUDUSD': 5, 'XAUUSD': 2, 'XAGUSD': 3, 'US30USD': 1, 'USATECHUSD': 2, 'US500USD': 2, 'INDEXUSD': 3,
                   'BTCUSD': 2, 'OILUSD': 3, 'XAUUSD.I': 2}
    symbols_pip_value = {'EURUSD': 10**5, 'GBPUSD': 10**5, 'NZDUSD': 10**5, 'USDCAD': 10**5, 'USDCHF': 10**5,
                         'USDJPY': 10**5, 'AUDUSD': 10**5, 'XAUUSD': 10**2, 'XAGUSD': 500, 'US30USD': 5,
                         'USATECHUSD': 20, 'US500USD': 20, 'INDEXUSD': 10**3, 'BTCUSD': 1, 'OILUSD': 10**3,
                         'XAUUSD.I': 10**2}
    symbols_with_usd = {'EURUSD': True, 'GBPUSD': True, 'NZDUSD': True, 'USDCAD': False, 'USDCHF': False,
                        'USDJPY': False, 'AUDUSD': True, 'XAUUSD': True, 'XAGUSD': True, 'US30USD': True,
                        'USATECHUSD': True, 'US500USD': True, 'INDEXUSD': True, 'BTCUSD': True, 'OILUSD': True,
                        'XAUUSD.I': True}

    symbols_show = {'EURUSD': 0, 'GBPUSD': 0, 'NZDUSD': 0, 'USDCAD': 0, 'USDCHF': 0, 'USDJPY': 0,
                    'AUDUSD': 0, 'XAUUSD': 0, 'XAGUSD': 0, 'US30USD': 0, 'USATECHUSD': 0, 'US500USD': 0, 'INDEXUSD': 0,
                    'BTCUSD': 0, 'OILUSD': 0, 'XAUUSD.I': 0}
