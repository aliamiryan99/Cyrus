from AlgorithmFactory.AlgorithmTools.LocalExtermums import get_local_extermums
import operator  # used for finding nearest index
import math


class TrailingStop:

    def __init__(self, win_local_extremum, is_update_window_local_extremum):
        self.win_local_extremum = win_local_extremum
        self.is_update_window_local_extremum = is_update_window_local_extremum

    def on_data(self, candle):
        pass

    def on_tick(self, history, entry_point, position_type, time):

        # entryPoint = 2999

        # %% ------- Step Wise algorithm. | Exit Point |
        stopCondition = False

        # ---- find local extremum in price
        localMin, localMax = get_local_extermums(history, self.win_local_extremum, 1)

        # ---- Buy Position
        if position_type == 'Buy':
            for j in range(entry_point, len(history)):
                # --- Update Resistance. find nearest previous localMin.
                if j == entry_point:  # for the first Resistance
                    # check to pick the first resistance between the previous local min or minimum of price in range of lookBack

                    # find minimum price in  range of lookBack
                    currentPoint = entry_point
                    lookBack = self.win_local_extremum
                    idxLookBack, min_val = min(enumerate([d['low'] for d in history[entry_point - lookBack:entry_point]]),
                                               key=operator.itemgetter(1))

                    if min_val < history[localMin[-1]]['low']:
                        nearestResistance = entry_point - lookBack + idxLookBack
                    else:
                        nearestResistance = localMin[-1]

                else:
                    currentPoint = j

                    if localMin[-1] > nearestResistance:
                        nearestResistance = localMin[
                            -1]  # check if the founded resistance index is newer than the prev index
                        if self.is_update_window_local_extremum:
                            win_local_extremum = math.ceil(self.win_local_extremum / 2)  # Update size of the Local Min
                            localMin, localMax = get_local_extermums(history, win_local_extremum, 1)

                currentPrice = history[currentPoint]['low']
                # --- Checking the Continuation Condition
                if (currentPrice < history[nearestResistance]['low']) and (
                        (currentPoint - entry_point) > 1):  # if prev resistance break and at leaset two candle proceed
                    # it can continue
                    stopCondition = True
                    break
        # ---- Sell Position
        elif position_type == 'Sell':
            for j in range(entry_point, len(history)):
                # --- Update Resistance. find nearest previous localMin.
                if j == entry_point:  # for the first Resistance
                    # check to pick the first resistance between the previous local max or maximum of price in range of lookBack

                    # find maximum price in  range of lookBack
                    currentPoint = entry_point
                    lookBack = self.win_local_extremum
                    idxLookBack, max_val = max(enumerate([d['high'] for d in history[entry_point - lookBack:entry_point]]),
                                               key=operator.itemgetter(1))

                    if max_val > history[localMax[-1]]['high']:
                        nearestResistance = entry_point - lookBack + idxLookBack
                    else:
                        nearestResistance = localMax[-1]

                else:
                    currentPoint = j
                    if localMax[-1] > nearestResistance:
                        nearestResistance = localMax[
                            -1]  # check if the founded resistance index is newer than the prev index
                        if self.is_update_window_local_extremum:
                            win_local_extremum = math.ceil(self.win_local_extremum / 2)  # Update size of the Local Min
                            localMin, localMax = get_local_extermums(history, win_local_extremum, 1)

                currentPrice = history[currentPoint]['high']
                # --- Checking the Continuation Condition
                if (currentPrice > history[nearestResistance]['high']) and (
                        (currentPoint - entry_point) > 1):  # if prev resistance break and at leaset two candle proceed
                    # it can continue
                    stopCondition = True
                    break

        return stopCondition

    def on_tick_end(self):
        pass
