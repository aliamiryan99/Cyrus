

base_directory = "SIReEntrance"

param_list = {
    'Symbol': ['XAUUSD'],
    'TimeFrame': ['M30', 'H1', 'H4', 'D1'],
    'Role': [1, 2, 3, 6, 8, 9],
    'Tenkan': [9*i for i in range(1,10)],
    'Kijun': [26*i for i in range(1,10)],
    'SenkouSpanProjection': [0, 26],
    'RangeFilterEnable': [False, True],
    'SequentialTrade': [False, True],
    'KomuCloudFilter': [False, True]
}
