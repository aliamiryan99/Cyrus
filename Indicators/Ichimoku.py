
from AlgorithmFactory.AlgorithmTools.CandleTools import *


class Ichimoku:

    def __init__(self, data, tenkan_lookback=9, kijun_lookback=26,
                           senkou_span_b_lookback=52, chikou_loopback=26, senkou_span_projection=26):
        self.data = data
        open, high, low, close = get_ohlc(data)
        self.tenkan_lookback, self.kijun_lookback, self.senkou_span_b_lookback = tenkan_lookback, kijun_lookback,\
                                                                                 senkou_span_b_lookback

        self.result = self.ichimoku_calculate(open, high, low, close, tenkan_lookback, kijun_lookback,
                                              senkou_span_b_lookback, chikou_loopback, senkou_span_projection)

    def update(self, data):
        open, high, low, close = get_ohlc(data)

        tenkan_sen, kijun_sen, chikou_span, senkou_span_a, senkou_span_b =\
            self.update_ichimoku(open, high, low, close, self.tenkan_lookback, self.kijun_lookback,
                                 self.senkou_span_b_lookback)

        self.result['TenkanSen'] = np.append(self.result['TenkanSen'][1:], [tenkan_sen])
        self.result['KijunSen'] = np.append(self.result['KijunSen'][1:], [kijun_sen])
        self.result['ChikouSpan'] = np.append(self.result['ChikouSpan'][1:], [chikou_span])
        self.result['SenkouSpanA'] = np.append(self.result['SenkouSpanA'][1:], [senkou_span_a])
        self.result['SenkouSpanB'] = np.append(self.result['SenkouSpanB'][1:], [senkou_span_b])
        self.result['TenKijun'] = np.append(self.result['TenKijun'][1:], [senkou_span_a])

    @staticmethod
    def ichimoku_calculate(open, high, low, close,tenkan_lookback=9, kijun_lookback=26,
                           senkou_span_b_lookback=52, chikou_loopback=26, senkou_span_projection=26):

        result = {'KijunSen': np.array([open[0]] * len(open))}
        # Kijun-sen
        for i in range(kijun_lookback, len(open)):
            try:
                result['KijunSen'][i] = (max(high[i-kijun_lookback+1:i+1]) + min(low[i - kijun_lookback+1:i + 1]))/2
            except ValueError:
                pass

        # Tenkan-sen
        result['TenkanSen'] = np.array([open[0]]*len(open))
        for i in range(tenkan_lookback, len(open)):
            try:
                result['TenkanSen'][i] = (max(high[i - tenkan_lookback+1:i + 1]) + min(low[i - tenkan_lookback+1:i + 1]))/2
            except ValueError:
                pass

        # Chikou-span
        result['ChikouSpan'] = np.array([open[0]]*(len(open)-chikou_loopback))
        for i in range(len(open) - chikou_loopback):
            result['ChikouSpan'][i] = close[i+chikou_loopback]

        # Senkou-span A
        senkou_span_a = np.array([open[0]]*(len(open)+senkou_span_projection))
        for i in range(len(open)):
            senkou_span_a[i+senkou_span_projection] = (result['TenkanSen'][i] + result['KijunSen'][i])/2
        # Senkou-span B
        senkou_span_b = np.array([open[0]]*(len(open)+senkou_span_projection))
        for i in range(len(open)):
            try:
                senkou_span_b[i+senkou_span_projection] = (max(high[i - senkou_span_b_lookback+1:i + 1]) + min(low[i - senkou_span_b_lookback+1:i + 1]))/2
            except ValueError:
                pass

        result['SenkouSpanA'] = senkou_span_a
        result['SenkouSpanB'] = senkou_span_b

        # TenKijun
        ten_kijun = np.array([open[0]] * len(open))
        for i in range(len(open)):
            ten_kijun[i] = (result['TenkanSen'][i] + result['KijunSen'][i]) / 2

        result['TenKijun'] = ten_kijun
        return result

    def update_ichimoku(self, open, high, low, close,tenkan_lookback=9, kijun_lookback=26,
                           senkou_span_b_lookback=52):
        tenkan_sen = (max(high[-tenkan_lookback:]) + min(low[-tenkan_lookback:]))/2
        kijun_sen = (max(high[-kijun_lookback:]) + min(low[-kijun_lookback:]))/2
        chikou_span = close[-1]
        senkou_span_a = (tenkan_sen + kijun_sen) / 2
        senkou_span_b = (max(high[-senkou_span_b_lookback:]) + min(low[-senkou_span_b_lookback:]))/2

        return tenkan_sen, kijun_sen, chikou_span, senkou_span_a, senkou_span_b
