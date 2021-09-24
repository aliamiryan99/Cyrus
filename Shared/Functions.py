

class Functions:

    @staticmethod
    def get_time_id(time, time_frame):
        identifier = time.day
        if time_frame == "MN":
            identifier = time.month
        if time_frame == "W1":
            identifier = time.isocalendar()[1]
        if time_frame == "H12":
            identifier = time.day * 2 + time.hour // 12
        if time_frame == "H4":
            identifier = time.day * 6 + time.hour // 4
        if time_frame == "H1":
            identifier = time.day * 24 + time.hour
        if time_frame == "M30":
            identifier = time.hour * 2 + time.minute // 30
        if time_frame == "M15":
            identifier = time.hour * 4 + time.minute // 15
        if time_frame == "M5":
            identifier = time.hour * 12 + time.minute // 5
        if time_frame == "M1":
            identifier = time.hour * 60 + time.minute
        return identifier

    @staticmethod
    def item_data_list_to_dic(data, i):
        return {'Time': data['Time'][i], 'Open': data['Open'][i], 'High': data['High'][i], 'Low': data['Low'][i],
                'Close': data['Close'][i], 'Volume': data['Volume'][i]}