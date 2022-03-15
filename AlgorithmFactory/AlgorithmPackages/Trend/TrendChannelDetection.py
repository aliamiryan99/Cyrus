
import numpy as np
from AlgorithmFactory.AlgorithmTools.LineUtils import rotate_line


def detect_trend_channels(max_ext, min_ext, times, up_price, down_price, consecutive_ext_num, pip):
    bull_channels, bear_channels = [], []
    i, j = 1, 1

    bull, bear = 1, 1
    while i < len(max_ext) or j < len(min_ext):
        if i != len(max_ext) and (j == len(min_ext) or max_ext[i] < min_ext[j]):
            # Update Num of consecutives
            if up_price[max_ext[i]] > up_price[max_ext[i-1]]:
                bull += 1
                if bear >= consecutive_ext_num:
                    bear_channels.append(get_channel(min_ext, j-bear, j, "Bear", up_price, down_price, times, pip))
                bear = 0
            else:
                if bull >= consecutive_ext_num:
                    bull_channels.append(get_channel(max_ext, i-bull, i, "Bull", up_price, down_price, times, pip))
                bull = 1
            i += 1
        else:
            if down_price[min_ext[j]] < down_price[min_ext[j-1]]:
                bear += 1
                if bull >= consecutive_ext_num:
                    bull_channels.append(get_channel(max_ext, i-bull, i, "Bull", up_price, down_price, times, pip))
                bull = 0
            else:
                if bear >= consecutive_ext_num:
                    bear_channels.append(get_channel(min_ext, j-bear, j, "Bear", up_price, down_price, times, pip))
                bear = 1
            j += 1

    if bull >= consecutive_ext_num:
        bull_channels.append(get_channel(max_ext, i - bull, i, "Bull", up_price, down_price, times, pip))
    elif bear >= consecutive_ext_num:
        bear_channels.append(get_channel(min_ext, j - bear, j, "Bear", up_price, down_price, times, pip))

    return bull_channels, bear_channels


def get_channel(ext, start, end, type, up_price, down_price, times, pip):

    if type == "Bull":
        main_x, main_y = [], []
        for i in range(start, end):
            main_x.append(ext[i])
            main_y.append(up_price[ext[i]])
        main_line = np.polyfit(main_x, main_y, 1)

        max_i = ext[start]
        for i in range(start+1, end):
            if up_price[ext[i]] - np.polyval(main_line, ext[i]) > up_price[max_i] - np.polyval(main_line, max_i):
                max_i = ext[i]

        max_value = up_price[max_i] - np.polyval(main_line, max_i)
        up_x = [ext[start], ext[end-1]]
        up_y = [np.polyval(main_line, ext[start]) + max_value, np.polyval(main_line, ext[end-1]) + max_value]
        up_line = np.polyfit(up_x, up_y, 1)

        up_y2 = [up_y[0]*pip, up_y[1]*pip]
        up_line2 = np.polyfit(up_x, up_y2, 1)

        slope = np.rad2deg(np.arctan(up_line2[0]))

        r_up_x, r_up_y = rotate_line(np.array(up_x), np.array(up_y2), -slope)
        r_up_x = [max(round(r_up_x[0]), 0), round(r_up_x[1])]

        min_i = ext[start]
        for i in range(ext[start]+1, ext[end-1]+1):
            if down_price[i] - np.polyval(main_line, i) < down_price[min_i] - np.polyval(main_line, min_i):
                min_i = i

        min_value = down_price[min_i] - np.polyval(main_line, min_i)
        down_x = [ext[start], ext[end - 1]]
        down_y = [np.polyval(main_line, ext[start]) + min_value, np.polyval(main_line, ext[end - 1]) + min_value]
        down_line = np.polyfit(down_x, down_y, 1)

        down_y2 = [down_y[0] * pip, down_y[1] * pip]
        down_line2 = np.polyfit(down_x, down_y2, 1)

        slope = np.rad2deg(np.arctan(down_line2[0]))

        r_down_x, r_down_y = rotate_line(np.array(down_x), np.array(down_y2), -slope)
        r_down_x = [max(round(r_down_x[0]), 0), round(r_down_x[1])]

        mid_x = [ext[start], ext[end - 1]]
        mid_y = [(up_y[0]+down_y[0])/2, (up_y[1]+down_y[1])/2]
        mid_line = np.polyfit(mid_x, mid_y, 1)

        while np.polyval(up_line, r_up_x[0]) < np.polyval(down_line, down_x[0]):
            r_up_x[0] += 1

        if up_x[1] < len(times):
            end_time1 = times[up_x[1]]
        else:
            end_time1 = times[-1] + (times[-1]-times[-2]) * (up_x[1] - len(times)+1)

        while np.polyval(down_line, r_down_x[1]) > np.polyval(up_line, up_x[1]):
            r_down_x[1] -= 1

        if r_down_x[1] < len(times):
            end_time2 = times[r_down_x[1]]
        else:
            end_time2 = times[-1] + (times[-1]-times[-2]) * (r_down_x[1] - len(times)+1)

        return {'MainLine': {'StartTime': times[up_x[0]], 'EndTime': end_time1, 'StartPrice': np.polyval(main_line, up_x[0]), 'EndPrice': np.polyval(main_line, up_x[1]),'Line':main_line},
                'MidLine': {'StartTime': times[up_x[0]], 'EndTime': end_time1, 'StartPrice': np.polyval(mid_line, up_x[0]), 'EndPrice': np.polyval(mid_line, up_x[1]),'Line':mid_line},
                'UpLine': {'StartTime': times[r_up_x[0]], 'EndTime': end_time1, 'StartPrice': np.polyval(up_line, r_up_x[0]), 'EndPrice': np.polyval(up_line, up_x[1]),'Line':up_line},
                'DownLine': {'StartTime': times[down_x[0]], 'EndTime': end_time2, 'StartPrice': np.polyval(down_line, down_x[0]), 'EndPrice': np.polyval(down_line, r_down_x[1]),'Line':down_line}}
    elif type == "Bear":
        main_x, main_y = [], []
        for i in range(start, end):
            main_x.append(ext[i])
            main_y.append(down_price[ext[i]])
        main_line = np.polyfit(main_x, main_y, 1)

        min_i = ext[start]
        for i in range(start + 1, end):
            if down_price[ext[i]] - np.polyval(main_line, ext[i]) < down_price[min_i] - np.polyval(main_line, min_i):
                min_i = ext[i]

        min_value = down_price[min_i] - np.polyval(main_line, min_i)
        down_x = [ext[start], ext[end - 1]]
        down_y = [np.polyval(main_line, ext[start]) + min_value, np.polyval(main_line, ext[end - 1]) + min_value]
        down_line = np.polyfit(down_x, down_y, 1)

        down_y2 = [down_y[0] * pip, down_y[1] * pip]
        down_line2 = np.polyfit(down_x, down_y2, 1)

        slope = np.rad2deg(np.arctan(down_line2[0]))

        r_down_x, r_down_y = rotate_line(np.array(down_x), np.array(down_y2), -slope)
        r_down_x = [max(round(r_down_x[0]), 0), round(r_down_x[1])]

        max_i = ext[start]
        for i in range(ext[start] + 1, ext[end - 1] + 1):
            if up_price[i] - np.polyval(main_line, i) > up_price[max_i] - np.polyval(main_line, max_i):
                max_i = i

        max_value = up_price[max_i] - np.polyval(main_line, max_i)
        up_x = [ext[start], ext[end - 1]]
        up_y = [np.polyval(main_line, ext[start]) + max_value, np.polyval(main_line, ext[end - 1]) + max_value]
        up_line = np.polyfit(up_x, up_y, 1)

        up_y2 = [up_y[0] * pip, up_y[1] * pip]
        up_line2 = np.polyfit(up_x, up_y2, 1)

        slope = np.rad2deg(np.arctan(up_line2[0]))

        r_up_x, r_up_y = rotate_line(np.array(up_x), np.array(up_y2), -slope)
        r_up_x = [max(round(r_up_x[0]), 0), round(r_up_x[1])]

        mid_x = [ext[start], ext[end - 1]]
        mid_y = [(up_y[0] + down_y[0]) / 2, (up_y[1] + down_y[1]) / 2]
        mid_line = np.polyfit(mid_x, mid_y, 1)

        while np.polyval(up_line, r_up_x[1]) < np.polyval(down_line, down_x[1]):
            r_up_x[1] -= 1

        if up_x[1] < len(times):
            end_time1 = times[up_x[1]]
        else:
            end_time1 = times[-1] + (times[-1]-times[-2]) * (up_x[1] - len(times)+1)

        while np.polyval(down_line, r_down_x[0]) > np.polyval(up_line, up_x[0]):
            r_down_x[0] += 1

        if r_up_x[1] < len(times):
            end_time2 = times[r_up_x[1]]
        else:
            end_time2 = times[-1] + (times[-1]-times[-2]) * (r_up_x[1] - len(times)+1)

        return {'MainLine': {'StartTime': times[down_x[0]], 'EndTime': end_time1, 'StartPrice': np.polyval(main_line, down_x[0]), 'EndPrice': np.polyval(main_line, down_x[1]), 'Line': main_line},
                'MidLine': {'StartTime': times[down_x[0]], 'EndTime': end_time1, 'StartPrice': np.polyval(mid_line, down_x[0]), 'EndPrice': np.polyval(mid_line, down_x[1]), 'Line': mid_line},
                'UpLine': {'StartTime': times[ext[start]], 'EndTime': end_time2, 'StartPrice': np.polyval(up_line, up_x[0]), 'EndPrice': np.polyval(up_line, r_up_x[1]), 'Line': up_line},
                'DownLine': {'StartTime': times[r_down_x[0]], 'EndTime': end_time1, 'StartPrice': np.polyval(down_line, r_down_x[0]), 'EndPrice': np.polyval(down_line, down_x[1]), 'Line': down_line}}
