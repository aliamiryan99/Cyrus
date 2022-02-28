
from AlgorithmFactory.AlgorithmTools.CandleTools import *
from copy import deepcopy


class SharpDetection:

    def __init__(self, atr_tr, minimum_candles):
        self.atr_tr = atr_tr
        self.minimum_candles = minimum_candles
        self.sharp_areas_up = None
        self.sharp_areas_down = None

    def get_sharps(self, data, price, atr_window):
        sharp_areas_up = []
        sharp_areas_down = []
        tr = self.atr_tr * get_body_mean(data, atr_window)
        i = 1
        while i < len(price):
            if abs(price[i] - price[i-1]) > tr:
                s = i
                e = len(price) - 1
                ext_i = len(price) - 1
                avg = price[i] - price[i-1]
                i += 1
                if avg > 0:
                    while i < len(price):
                        avg = (avg * (i-s) + (price[i] - price[i-1])) / (i-s+1)
                        if avg < tr:
                            e = i
                            ext_i = np.argmax(price[s:e]) + s
                            break
                        i += 1
                elif avg < 0:
                    while i < len(price):
                        avg = (avg * (i - s) + (price[i] - price[i - 1])) / (i - s + 1)
                        if avg > -tr:
                            e = i
                            ext_i = np.argmin(price[s:e]) + s
                            break
                        i += 1
                if e - s > self.minimum_candles:
                    if avg > 0:
                        sharp_areas_up.append({"Start": s, "End": e, "Ext": ext_i, "ExtPrice": price[ext_i], 'StartTime': data[s]['Time'], 'EndTime': data[e]['Time']})
                    else:
                        sharp_areas_down.append({"Start": s, "End": e, "Ext": ext_i, "ExtPrice": price[ext_i], 'StartTime': data[s]['Time'], 'EndTime': data[e]['Time']})
                else:
                    i = s
            i += 1
        self.sharp_areas_up = sharp_areas_up
        self.sharp_areas_down = sharp_areas_down
        return sharp_areas_up, sharp_areas_down

    def filter_intersections(self, type, other_sharps):
        result = None
        if type == "Demand":
            result = deepcopy(self.sharp_areas_up)
        elif type == "Supply":
            result = deepcopy(self.sharp_areas_down)

        if result is not None:
            i, j = 0, 0
            while i < len(result) and j < len(other_sharps):
                if result[i]['Start'] <= other_sharps[j]['End'] and result[i]['End'] >= other_sharps[j]['Start']:
                    result.pop(i)
                elif result[i]['End'] < other_sharps[j]['Start']:
                    i += 1
                elif result[i]['Start'] > other_sharps[j]['End']:
                    j += 1
            return result
        else:
            return None

    def filter_swings(self, type, extremums, price, window):
        results = []
        sharp_areas = self.sharp_areas_up if type == "Demand" else self.sharp_areas_down
        i, j = 0, 0
        while i < len(sharp_areas):
            while j < len(extremums) and extremums[j] < sharp_areas[i]["Start"]:
                j += 1
            j -= 1
            while j > 0 and extremums[j] > sharp_areas[i]["Start"] - window:
                j -= 1
            if j > 0:
                if type == "Demand":
                    max_i = np.argmax(price[extremums[j]:sharp_areas[i]['Start']]) + extremums[j]
                    if price[sharp_areas[i]['Ext']] > price[max_i]:
                        results.append(sharp_areas[i])
                elif type == "Supply":
                    min_i = np.argmin(price[extremums[j]:sharp_areas[i]['Start']]) + extremums[j]
                    if price[sharp_areas[i]['Ext']] < price[min_i]:
                        results.append(sharp_areas[i])
            else:
                j = 0
            i += 1
        return results

    def get_source_of_movement(self, type, data):
        results = []
        sharp_areas = self.sharp_areas_up if type == "Demand" else self.sharp_areas_down
        atr = get_body_mean(data, len(data))
        i = 0
        while i < len(sharp_areas):
            j = sharp_areas[i]['Start'] - 1
            if type == "Demand":
                while j >= 0 and data[j]['Close'] >= data[j]['Open']:
                    j -= 1
            elif type == "Supply":
                while j >= 0 and data[j]['Close'] <= data[j]['Open']:
                    j -= 1
            start = j
            up_price, down_price = data[start]['High'], data[start]['Low']

            if type == "Demand":
                down_price -= 1 * atr
            if type == "Supply":
                up_price += 1 * atr

            j = sharp_areas[i]['End']
            if type == "Demand":
                while j < len(data)-1 and data[j]['Low'] > up_price:
                    j += 1
            if type == "Supply":
                while j < len(data)-1 and data[j]['High'] < down_price:
                    j += 1
            end = j

            results.append({"Start": start, "End": end, "UpPrice": up_price, "DownPrice": down_price,
                           "StartTime": data[start]['Time'], "EndTime": data[end]['Time'], "Type": type})
            i += 1
        return results

    def set_sharp_area_up(self, sharp_areas):
        self.sharp_areas_up = sharp_areas

    def set_sharp_area_down(self, sharp_areas):
        self.sharp_areas_down = sharp_areas