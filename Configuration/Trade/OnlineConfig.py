
class Config:

    # in point
    spreads = {'EURUSD': 20, 'GBPUSD': 30, 'NZDUSD': 40, 'USDCAD': 40, 'USDCHF': 30, 'USDJPY': 30,
               'AUDUSD': 30, 'GOLD': 50, 'SILVER': 50, 'XAUUSD': 50, 'XAGUSD': 50, 'US30.MAY1': 60, 'US30.DEC1': 60,
               'EURUSD.I': 20, 'GBPUSD.I': 30, 'NZDUSD.I': 40, 'USDCAD.I': 40, 'USDCHF.I': 30, 'USDJPY.I': 30,
               'AUDUSD.I': 30, 'XAUUSD.I': 50, 'XAGUSD.I': 50, 'BTC': 500, 'LTC': 500, 'ETH': 400,
               'BTCUSD': 5000, 'ETHUSD': 1000, 'LTCUSD': 1000, 'DOGEUSD': 100,
               'AUDCAD': 60, 'AUDCHF': 50, 'AUDJPY': 50, 'AUDNZD': 60, 'CADCHF': 40, 'CADJPY': 50, 'CHFJPY': 50,
               'EURAUD': 60, 'EURCAD': 50, 'EURCHF': 40, 'EURGBP': 40, 'EURJPY': 50, 'EURNZD': 60, 'EURPLN': 50,
               'GBPAUD': 60, 'GBPCAD': 50, 'GBPCHF': 50, 'GBPJPY': 50, 'GBPNZD': 50, 'NZDCAD': 40, 'NZDCHF': 50,
               'NZDJPY': 50, 'USDCNH': 60, 'USDMXN': 70, 'USDPLN': 60, 'USDRUB': 60, 'USDZAR': 70,
               'AUDCAD.I': 60, 'AUDCHF.I': 50, 'AUDJPY.I': 50, 'AUDNZD.I': 60, 'CADCHF.I': 40, 'CADJPY.I': 50, 'CHFJPY.I': 50,
               'EURAUD.I': 60, 'EURCAD.I': 50, 'EURCHF.I': 40, 'EURGBP.I': 40, 'EURJPY.I': 50, 'EURNZD.I': 60, 'EURPLN.I': 50,
               'GBPAUD.I': 60, 'GBPCAD.I': 50, 'GBPCHF.I': 50, 'GBPJPY.I': 50, 'GBPNZD.I': 50, 'NZDCAD.I': 40, 'NZDCHF.I': 50,
               'NZDJPY.I': 50, 'USDCNH.I': 60, 'USDMXN.I': 70, 'USDPLN.I': 60, 'USDRUB.I': 60, 'USDZAR.I': 70
               }

    volume_digit = 2        # 2 -> at least 0.01 lot
    max_volume = 200

    date_format = '%Y.%m.%d %H:%M'
    date_order_format = '%Y.%m.%d %H:%M:%S'
    tick_date_format = '%Y.%m.%d %H:%M:%S'

    timeframes_dic = {'M1': 1, 'M5': 5, 'M15': 15, 'M30': 30, 'H1': 60, 'H4': 240, 'D1': 1440,
                      'W1': 10080, 'MN': 43200}
    timeframes_dic_rev = {1: 'M1', 5: 'M5', 15: 'M15', 30: 'M30', 60: 'H1', 240: 'H4', 1440: 'D1',
                      10080: 'W1', 43200: 'MN'}
    secondary_timefarmes = {"H12": "H4"}
    secondary_timefarmes_ratio = {"H12": 3}

    symbols_dict = {'EURUSD.I': 0, 'GBPUSD.I': 1, 'NZDUSD.I': 2, 'USDCAD.I': 3, 'USDCHF.I': 4, 'USDJPY.I': 5,
                    'AUDUSD.I': 6, 'XAUUSD.I': 7, 'XAGUSD.I': 8, 'US30.JUN1': 9, 'EURUSD': 10, 'GBPUSD': 11,
                    'NZDUSD': 12, 'USDCAD': 13, 'USDCHF': 14, 'USDJPY': 15,'AUDUSD': 16, 'GOLD': 17, 'SILVER': 18,
                    'US30.MAY1': 19, 'US30.DEC1': 20,'BTC': 21, 'LTC': 22, 'ETH': 23, 'XAUUSD': 24, 'XAGUSD': 25,
                    'BTCUSD': 26, 'ETHUSD': 27, 'LTCUSD': 28, 'DOGEUSD': 29,
                    'AUDCAD': 30, 'AUDCHF': 31, 'AUDJPY': 32, 'AUDNZD': 33, 'CADCHF': 34, 'CADJPY': 35, 'CHFJPY': 36,
                    'EURAUD': 37, 'EURCAD': 38, 'EURCHF': 39, 'EURGBP': 40, 'EURJPY': 41, 'EURNZD': 42, 'EURPLN': 43,
                    'GBPAUD': 44, 'GBPCAD': 45, 'GBPCHF': 46, 'GBPJPY': 47, 'GBPNZD': 48, 'NZDCAD': 49, 'NZDCHF': 50,
                    'NZDJPY': 51, 'USDCNH': 52, 'USDMXN': 53, 'USDPLN': 54, 'USDRUB': 55, 'USDZAR': 56,
                    'AUDCAD.I': 57, 'AUDCHF.I': 58, 'AUDJPY.I': 59, 'AUDNZD.I': 60, 'CADCHF.I': 61, 'CADJPY.I': 62, 'CHFJPY.I': 63,
                    'EURAUD.I': 64, 'EURCAD.I': 65, 'EURCHF.I': 66, 'EURGBP.I': 67, 'EURJPY.I': 68, 'EURNZD.I': 69, 'EURPLN.I': 70,
                    'GBPAUD.I': 71, 'GBPCAD.I': 72, 'GBPCHF.I': 73, 'GBPJPY.I': 74, 'GBPNZD.I': 75, 'NZDCAD.I': 76, 'NZDCHF.I': 77,
                    'NZDJPY.I': 78, 'USDCNH.I': 79, 'USDMXN.I': 80, 'USDPLN.I': 81, 'USDRUB.I': 82, 'USDZAR.I': 83
                    }
    symbols_list = ['EURUSD.I', 'GBPUSD.I', 'NZDUSD.I', 'USDCAD.I', 'USDCHF.I', 'USDJPY.I', 'AUDUSD.I',
                    'XAUUSD.I', 'XAGUSD.I', 'US30.JUN1', 'EURUSD', 'GBPUSD', 'NZDUSD', 'USDCAD', 'XAUUSD', 'XAGUSD'
                    'USDCHF', 'USDJPY', 'AUDUSD', 'GOLD', 'SILVER', 'US30.MAY1', 'US30.DEC1', 'BTC', 'LTC', 'ETH',
                    'BTCUSD', 'ETHUSD', 'LTCUSD', 'DOGEUSD', 'AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'CADCHF',
                    'CADJPY', 'CHFJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURNZD', 'EURPLN', 'GBPAUD',
                    'GBPCAD', 'GBPCHF', 'GBPJPY', 'GBPNZD', 'NZDCAD', 'NZDCHF', 'NZDJPY', 'USDCNH', 'USDMXN', 'USDPLN',
                    'USDRUB', 'USDZAR',
                    'CADJPY.I', 'CHFJPY.I', 'EURAUD.I', 'EURCAD.I', 'EURCHF.I', 'EURGBP.I', 'EURJPY.I', 'EURNZD.I',
                    'EURPLN.I', 'GBPAUD.I', 'GBPCAD.I', 'GBPCHF.I', 'GBPJPY.I', 'GBPNZD.I', 'NZDCAD.I', 'NZDCHF.I',
                    'NZDJPY.I', 'USDCNH.I', 'USDMXN.I', 'USDPLN.I', 'USDRUB.I', 'USDZAR.I'
                    ]

    symbols_pip = {'EURUSD.I': 5, 'GBPUSD.I': 5, 'NZDUSD.I': 5, 'USDCAD.I': 5, 'USDCHF.I': 5,
                    'USDJPY.I': 3, 'AUDUSD.I': 5, 'XAUUSD.I': 2, 'XAGUSD.I': 3, 'US30.JUN1': 0, 'XAUUSD': 2, 'XAGUSD': 3,
                   'EURUSD': 4, 'GBPUSD': 4, 'NZDUSD': 4, 'USDCAD': 4, 'USDCHF': 4, 'BTC': 0, 'LTC': 0, 'ETH': 0,
                   'USDJPY': 2, 'AUDUSD': 4, 'GOLD': 1, 'SILVER': 2, 'US30.MAY1': 1, 'US30.DEC1': 1,
                   'BTCUSD': 2, 'ETHUSD': 2, 'LTCUSD': 2, 'DOGEUSD': 5, 'AUDCAD': 5, 'AUDCHF': 5, 'AUDJPY': 3, 'AUDNZD': 5, 'CADCHF': 5,
                   'CADJPY': 3, 'CHFJPY': 3, 'EURAUD': 5, 'EURCAD': 5, 'EURCHF': 5, 'EURGBP': 5, 'EURJPY': 3, 'EURNZD': 5, 'EURPLN': 5, 'GBPAUD': 5,
                   'GBPCAD': 5, 'GBPCHF': 5, 'GBPJPY': 3, 'GBPNZD': 5, 'NZDCAD': 5, 'NZDCHF': 5, 'NZDJPY': 3, 'USDCNH': 5, 'USDMXN': 5, 'USDPLN': 5,
                   'USDRUB': 4, 'USDZAR': 5,
                   'CADJPY.I': 3, 'CHFJPY.I': 3, 'EURAUD.I': 5, 'EURCAD.I': 5, 'EURCHF.I': 5, 'EURGBP.I': 5,
                   'EURJPY.I': 3, 'EURNZD.I': 5, 'EURPLN.I': 5, 'GBPAUD.I': 5, 'GBPCAD.I': 5, 'GBPCHF.I': 5,
                   'GBPJPY.I': 3, 'GBPNZD.I': 5, 'NZDCAD.I': 5, 'NZDCHF.I': 5, 'NZDJPY.I': 3, 'USDCNH.I': 5,
                   'USDMXN.I': 5, 'USDPLN.I': 5, 'USDRUB.I': 4, 'USDZAR.I': 5
                   }
    symbols_pip_value = {'EURUSD.I': 10 ** 5, 'GBPUSD.I': 10 ** 5, 'NZDUSD.I': 10 ** 5, 'USDCAD.I': 10 ** 5,
                         'USDCHF.I': 10 ** 5, 'USDJPY.I': 10 ** 3, 'AUDUSD.I': 10 ** 5, 'XAUUSD.I': 10 ** 2,
                         'XAGUSD.I': 500, 'US30.JUN1': 5, 'EURUSD': 10**5, 'GBPUSD': 10**5, 'NZDUSD': 10**5,
                         'USDCAD': 10**5, 'USDCHF': 10**5, 'USDJPY': 10**5, 'AUDUSD': 10**5, 'XAUUSD': 10**2,
                         'XAGUSD': 500, 'US30.MAY1': 5, 'US30.DEC1': 5, 'USATECHUSD': 20, 'US500USD': 20, 'BTC': 1,
                         'LTC': 1, 'ETH': 1,
                         'BTCUSD': 10 ** 2, 'ETHUSD': 10 ** 2, 'LTCUSD': 10 ** 2, 'DOGEUSD': 10 ** 5, 'AUDCAD': 10 ** 5,
                         'AUDCHF': 10 ** 5, 'AUDJPY': 10 ** 3, 'AUDNZD': 10 ** 5, 'CADCHF': 10 ** 5, 'CADJPY': 10 ** 3,
                         'CHFJPY': 10 ** 3, 'EURAUD': 10 ** 5, 'EURCAD': 10 ** 5, 'EURCHF': 10 ** 5, 'EURGBP': 10 ** 5,
                         'EURJPY': 10 ** 3, 'EURNZD': 10 ** 5, 'EURPLN': 10 ** 5, 'GBPAUD': 10 ** 5, 'GBPCAD': 10 ** 5,
                         'GBPCHF': 10 ** 5, 'GBPJPY': 10 ** 3, 'GBPNZD': 10 ** 5, 'NZDCAD': 10 ** 5, 'NZDCHF': 10 ** 5,
                         'NZDJPY': 10 ** 3, 'USDCNH': 10 ** 5, 'USDMXN': 10 ** 5, 'USDPLN': 10 ** 5, 'USDRUB': 10 ** 4,
                         'USDZAR': 10 ** 5,
                         'CADJPY.I': 10 ** 3, 'CHFJPY.I': 10 ** 3, 'EURAUD.I': 10 ** 5, 'EURCAD.I': 10 ** 5,
                         'EURCHF.I': 10 ** 5, 'EURGBP.I': 10 ** 5, 'EURJPY.I': 10 ** 3, 'EURNZD.I': 10 ** 5,
                         'EURPLN.I': 10 ** 5, 'GBPAUD.I': 10 ** 5, 'GBPCAD.I': 10 ** 5, 'GBPCHF.I': 10 ** 5,
                         'GBPJPY.I': 10 ** 3, 'GBPNZD.I': 10 ** 5, 'NZDCAD.I': 10 ** 5, 'NZDCHF.I': 10 ** 5,
                         'NZDJPY.I': 10 ** 3, 'USDCNH.I': 10 ** 5, 'USDMXN.I': 10 ** 5, 'USDPLN.I': 10 ** 5,
                         'USDRUB.I': 10 ** 4, 'USDZAR.I': 10 ** 5
                         }
    symbols_with_usd = {'EURUSD.I': True, 'GBPUSD.I': True, 'NZDUSD.I': True, 'USDCAD.I': False, 'USDCHF.I': False,
                        'USDJPY.I': False, 'AUDUSD.I': True, 'XAUUSD.I': True, 'XAGUSD.I': True, 'US30.JUN1': True,
                        'EURUSD': True, 'GBPUSD': True, 'NZDUSD': True, 'USDCAD': False, 'USDCHF': False,
                        'USDJPY': False, 'AUDUSD': True, 'GOLD': True, 'BTC': True, 'LTC': True, 'ETH': True,
                        'SILVER': True, 'US30.MAY1': True, 'US30.DEC1': True,
                        'BTCUSD': True, 'ETHUSD': True, 'LTCUSD': True, 'DOGEUSD': True, 'AUDCAD': True,
                        'AUDCHF': True, 'AUDJPY': True, 'AUDNZD': True, 'CADCHF': True, 'CADJPY': True,
                        'CHFJPY': True, 'EURAUD': True, 'EURCAD': True, 'EURCHF': True, 'EURGBP': True,
                        'EURJPY': True, 'EURNZD': True, 'EURPLN': True, 'GBPAUD': True, 'GBPCAD': True,
                        'GBPCHF': True, 'GBPJPY': True, 'GBPNZD': True, 'NZDCAD': True, 'NZDCHF': True,
                        'NZDJPY': True, 'USDCNH': True, 'USDMXN': True, 'USDPLN': True, 'USDRUB': True,
                        'USDZAR': True,
                        'CADJPY.I': True, 'CHFJPY.I': True, 'EURAUD.I': True, 'EURCAD.I': True,
                        'EURCHF.I': True, 'EURGBP.I': True, 'EURJPY.I': True, 'EURNZD.I': True,
                        'EURPLN.I': True, 'GBPAUD.I': True, 'GBPCAD.I': True, 'GBPCHF.I': True,
                        'GBPJPY.I': True, 'GBPNZD.I': True, 'NZDCAD.I': True, 'NZDCHF.I': True,
                        'NZDJPY.I': True, 'USDCNH.I': True, 'USDMXN.I': True, 'USDPLN.I': True,
                        'USDRUB.I': True, 'USDZAR.I': True
                        }
