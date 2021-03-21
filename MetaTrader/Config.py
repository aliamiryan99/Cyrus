
class Config:
    date_format = '%Y.%m.%d %H:%M'
    date_order_format = '%Y.%m.%d %H:%M:%S'
    tick_date_format = '%Y.%m.%d %H:%M:%S'
    timeframes_dic = {'M1': 1, 'M5': 5, 'M30': 30, 'H1': 60, 'H4': 240, 'D1': 1440,
                      'W1': 10080, 'MN1': 43200}
    secondary_timefarmes = {"H12": "H4"}
    secondary_timefarmes_ratio = {"H12": 3}
    symbols_dict = {'EURUSD.I': 0, 'GBPUSD.I': 1, 'NZDUSD.I': 2, 'USDCAD.I': 3, 'USDCHF.I': 4, 'USDJPY.I': 5,
                    'AUDUSD.I': 6, 'XAUUSD.I': 7, 'XAGUSD.I': 8, 'US30.JUN1': 9}
    symbols_list = ['EURUSD.I', 'GBPUSD.I', 'NZDUSD.I', 'USDCAD.I', 'USDCHF.I', 'USDJPY.I', 'AUDUSD.I',
                    'XAUUSD.I', 'XAGUSD.I', 'US30.JUN1']
    symbols_pip = {'EURUSD.I': 5, 'GBPUSD.I': 5, 'NZDUSD.I': 5, 'USDCAD.I': 5, 'USDCHF.I': 5,
                     'USDJPY.I': 3, 'AUDUSD.I': 5, 'XAUUSD.I': 2, 'XAGUSD.I': 3, 'US30.JUN1': 0}