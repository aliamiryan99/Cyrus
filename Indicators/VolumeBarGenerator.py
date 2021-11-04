

class VolumeGenerator:

    def __init__(self, count):
        self.count = count
        self.buffer_data = []
        self.total_data = []
        self.cum_value = 0

    def update(self, bar):

        self.buffer_data.append(bar)

        self.cum_value += 1
        if self.cum_value == self.count:

            time_value = self.buffer_data[-1]['Time']
            start_time = self.buffer_data[0]['StartTime']
            middle_time = start_time + ((time_value - start_time) / 2)
            open_value = self.buffer_data[0]['Open']
            high_value = max([bar['High'] for bar in self.buffer_data])
            low_value = min([bar['Low'] for bar in self.buffer_data])
            close_value = self.buffer_data[-1]['Close']
            WAP = sum([bar['WAP'] for bar in self.buffer_data]) / len(self.buffer_data)
            x = (self.buffer_data[-1]['CandleXCenter'] + self.buffer_data[0]['CandleXCenter']) / 2
            self.total_data.append({'StartTime': start_time, 'MiddleTime': middle_time, 'Time': time_value, 'Open': open_value, 'High': high_value, 'Low': low_value,
                                    'Close': close_value, 'WAP': WAP, 'Volume': self.cum_value, 'CandleXCenter': x})
            print(self.total_data[-1])
            self.cum_value = 0
            self.buffer_data = []


