
class Config:
    date_format = '%Y.%m.%d %H:%M'
    date_order_format = '%Y.%m.%d %H:%M:%S'
    tick_date_format = '%Y.%m.%d %H:%M:%S'

    volume_digit = 2        # 2 -> at least 0.01 lot

    timeframes_dic = {'M1': 1, 'M5': 5, 'M15': 15, 'M30': 30, 'H1': 60, 'H4': 240, 'D1': 1440,
                      'W1': 10080, 'MN1': 43200}
    secondary_timefarmes = {"H12": "H4"}
    secondary_timefarmes_ratio = {"H12": 3}

    symbols_dict = {'EURUSD.I': 0, 'GBPUSD.I': 1, 'NZDUSD.I': 2, 'USDCAD.I': 3, 'USDCHF.I': 4, 'USDJPY.I': 5,
                    'AUDUSD.I': 6, 'XAUUSD.I': 7, 'XAGUSD.I': 8, 'US30.JUN1': 9, 'EURUSD': 10, 'GBPUSD': 11,
                    'NZDUSD': 12, 'USDCAD': 13, 'USDCHF': 14, 'USDJPY': 15,'AUDUSD': 16, 'GOLD': 17,
                    'SILVER': 18, 'US30.MAY1': 19}
    symbols_list = ['EURUSD.I', 'GBPUSD.I', 'NZDUSD.I', 'USDCAD.I', 'USDCHF.I', 'USDJPY.I', 'AUDUSD.I',
                    'XAUUSD.I', 'XAGUSD.I', 'US30.JUN1', 'EURUSD', 'GBPUSD', 'NZDUSD', 'USDCAD',
                    'USDCHF', 'USDJPY', 'AUDUSD', 'GOLD', 'SILVER', 'US30.MAY1']

    symbols_pip = {'EURUSD.I': 5, 'GBPUSD.I': 5, 'NZDUSD.I': 5, 'USDCAD.I': 5, 'USDCHF.I': 5,
                     'USDJPY.I': 3, 'AUDUSD.I': 5, 'XAUUSD.I': 2, 'XAGUSD.I': 3, 'US30.JUN1': 0,
                   'EURUSD': 4, 'GBPUSD': 4, 'NZDUSD': 4, 'USDCAD': 4, 'USDCHF': 4,
                   'USDJPY': 2, 'AUDUSD': 4, 'GOLD': 1, 'SILVER': 2, 'US30.MAY1': 1}
    symbols_pip_value = {'EURUSD.I': 10 ** 5, 'GBPUSD.I': 10 ** 5, 'NZDUSD.I': 10 ** 5, 'USDCAD.I': 10 ** 5,
                         'USDCHF.I': 10 ** 5, 'USDJPY.I': 10 ** 5, 'AUDUSD.I': 10 ** 5, 'XAUUSD.I': 10 ** 2,
                         'XAGUSD.I': 500, 'US30.JUN1': 5, 'EURUSD': 10**5, 'GBPUSD': 10**5, 'NZDUSD': 10**5,
                         'USDCAD': 10**5, 'USDCHF': 10**5, 'USDJPY': 10**5, 'AUDUSD': 10**5, 'XAUUSD': 10**2,
                         'XAGUSD': 500, 'US30.MAY1': 5, 'USATECHUSD': 20, 'US500USD': 20}
    symbols_with_usd = {'EURUSD.I': True, 'GBPUSD.I': True, 'NZDUSD.I': True, 'USDCAD.I': False, 'USDCHF.I': False,
                        'USDJPY.I': False, 'AUDUSD.I': True, 'XAUUSD.I': True, 'XAGUSD.I': True, 'US30.JUN1': True,
                        'EURUSD': True, 'GBPUSD': True, 'NZDUSD': True, 'USDCAD': False, 'USDCHF': False,
                        'USDJPY': False, 'AUDUSD': True, 'GOLD': True,
                        'SILVER': True, 'US30.MAY1': True}
