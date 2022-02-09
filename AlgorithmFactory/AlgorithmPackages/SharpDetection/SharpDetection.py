
from AlgorithmFactory.AlgorithmTools.CandleTools import *
from copy import deepcopy

class SharpDetection:

    def __init__(self, atr_tr, minimum_candles):
        self.atr_tr = atr_tr
        self.minimum_candles = minimum_candles
        self.sharp_areas = None

    def get_sharps(self, data, price):
        sharp_areas = []
        tr = self.atr_tr * get_body_mean(data, len(data))
        i = 1
        while i < len(price):
            if (price[i] - price[i-1]) > tr:
                s = i
                e = len(price) - 1
                max_i = len(price) - 1
                avg = price[i] - price[i-1]
                i += 1
                while i < len(price):
                    avg = (avg * (i-s) + (price[i] - price[i-1])) / (i-s+1)
                    if avg < tr:
                        e = i
                        max_i = np.argmax(price[s:e]) + s
                        break
                    i += 1
                if e - s > self.minimum_candles:
                    sharp_areas.append({"Start": s, "End": e, "Max": max_i})
            i += 1
        self.sharp_areas = sharp_areas
        return sharp_areas

    def filter_intersections(self, other_sharps):
        result = deepcopy(self.sharp_areas)
        if result is not None:
            i, j = 0, 0
            while i < len(result) and j < len(other_sharps):
                if result[i]['Start'] < other_sharps[j]['End'] and result[i]['End'] > other_sharps[j]['Start']:
                    result.pop(i)
                elif result[i]['End'] < other_sharps[j]['Start']:
                    i += 1
                elif result[i]['Start'] > other_sharps[j]['End']:
                    j += 1
            return result
        else:
            return None

    def filter_swings(self, extremums, price, window):
        results = []
        i, j = 0, 0
        while i < len(self.sharp_areas):
            while j < len(extremums) and extremums[j] < self.sharp_areas[i]["Start"]:
                j += 1
            j -= 1
            while j > 0 and extremums[j] > self.sharp_areas[i]["Start"] - window:
                j -= 1
            if j > 0:
                max_i = np.argmax(price[extremums[j]:self.sharp_areas[i]['Start']]) + extremums[j]
                if price[self.sharp_areas[i]['Max']] > price[max_i]:
                    results.append(self.sharp_areas[i])
            i += 1
        return results

    def get_source_of_movement(self, data):
        results = []
        i = 0
        while i < len(self.sharp_areas):
            j = self.sharp_areas[i]['Start'] - 1
            while j >= 0 and data[j]['Close'] >= data[j]['Open']:
                j -= 1
            start = j
            up_price, down_price = data[start]['High'], data[start]['Low']
            j = self.sharp_areas[i]['End']
            while j < len(data)-1 and data[j]['Low'] > up_price:
                j += 1
            end = j
            results.append({"Start": start, "End": end, "UpPrice": up_price, "DownPrice": down_price})
            i += 1
        return results



    def set_sharp_area(self, sharp_areas):
        self.sharp_areas = sharp_areas