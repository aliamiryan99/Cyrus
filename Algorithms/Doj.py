
from AlgorithmTools.CandleTools import get_bottom_top


class Doji:

    def __init__(self, data_history, win, detect_mode, candle_mode):
        # Data window, moving average window
        self.win = win
        self.detect_mode = detect_mode
        self.candle_mode = candle_mode
        len_window = len(data_history)
        if len_window <= self.win:
            raise Exception("window len should be greater than window size")
        self.data_window = data_history[-self.win-5:]
        self.doji_trigger = 0

    def on_tick(self):
        if self.doji_trigger == 1:
            if self.data_window[-1]['High'] > self.data_window[-2]['High']:
                self.doji_trigger = 0
                return 1, self.data_window[-2]['High']
        elif self.doji_trigger == -1:
            if self.data_window[-1]['Low'] < self.data_window[-2]["Low"]:
                self.doji_trigger = 0
                return -1, self.data_window[-2]['Low']
        return 0, 0

    def on_data(self, candle, cash):
        self.doji_trigger = self.doji_detect()
        self.data_window.pop(0)
        self.data_window.append(candle)
        return 0, 0

    def doji_detect(self):
        window = self.data_window
        win = self.win
        detect_mode = self.detect_mode
        candle_mode = self.candle_mode

        body_length = []
        total_length = []
        for data in window:
            body_length.append(abs(data['Close'] - data['Open']))
            total_length.append(abs(data['High'] - data['Low']))

        bottom_candle, top_candle = get_bottom_top(window)

        max_body, min_body = 0, 0
        if candle_mode == 1:
            max_body = body_length[-2]
            min_body = body_length[-2]
            for i in range(3, win + 2):
                max_body = max(body_length[-i], max_body)
                min_body = min(body_length[-i], min_body)
        elif candle_mode == -1:
            max_body = total_length[-2]
            min_body = total_length[-2]
            for i in range(3, win + 2):
                max_body = max(total_length[-i], max_body)
                min_body = min(total_length[-i], min_body)
        detection = 0

        if detect_mode == 1:  # High, Low
            cnt = 0
            for i in range(1, win + 1):
                if window[-i]['High'] < window[-i - 1]['High']:
                    cnt += 1
            if cnt == win:
                detection = 1
            cnt = 0
            for i in range(1, win + 1):
                if window[-i]['Low'] > window[-i - 1]['Low']:
                    cnt += 1
            if cnt == win:
                detection = -1
        elif detect_mode == 2:  # Top, Bottom
            cnt = 0
            for i in range(1, win + 1):
                if top_candle[-i] < top_candle[-i - 1]:
                    cnt += 1
            if cnt == win:
                detection = 1
            cnt = 0
            for i in range(1, win + 1):
                if bottom_candle[-i] > bottom_candle[-i - 1]:
                    cnt += 1
            if cnt == win:
                detection = -1
        elif detect_mode == 3:  # Last Candle
            if body_length[-2] >= max_body:
                if window[-2]['Close'] < window[-2]['Open']:
                    detection = 1
                else:
                    detection = -1

        if candle_mode == 1:  # body mode
            if body_length[-1] <= min_body:
                return detection

        if candle_mode == 2:  # total mode
            if total_length[-1] <= min_body:
                return detection

        return 0