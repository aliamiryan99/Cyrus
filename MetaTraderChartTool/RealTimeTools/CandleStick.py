from MetaTrader.MetaTraderBase import MetaTraderBase
from MetaTraderChartTool.RealTimeTools.RealTimeTool import RealTimeTool

from AlgorithmFactory.AlgorithmPackages.CandleSticks import CandleSticks
from Utilities.Statistics import *


class CandleStick(RealTimeTool):

    def __init__(self, chart_tool: MetaTraderBase, data, symbol, candle_type, trade_enable, telegram):
        super().__init__(chart_tool, data)

        self.symbol = symbol
        self.telegram_channel_name = "@polaris_candlestick_patterns"
        self.telegram = telegram
        self.trade_enable = trade_enable

        self.color = "40,180,60"
        self.width = 1
        self.candle_type = candle_type

        self.rect_color = "4,129,25"
        self.rect_x, self.rect_y = 20, 40
        self.rect_width, self.rect_height = 200, 200
        self.label = f"Candle Stick Patterns {candle_type}"

        detected_list = CandleSticks.get_candlesticks(self.data, candle_type)

        filter_direction = 1
        detected_list_new = []
        for i in range(len(detected_list)):
            if detected_list[i]['Direction'] == filter_direction or filter_direction == 0:
                    detected_list_new.append(detected_list[i])
        detected_list = detected_list_new

        statistic_window = 10
        results = get_bullish_bearish_ratio(self.data, [detected['Index'] for detected in detected_list], statistic_window)
        self.bullish_ratio_min, self.bullish_ratio_max, self.bullish_ratio_mean = get_min_max_mean([result['BullishRatio'] for result in results])
        self.bearish_ratio_min, self.bearish_ratio_max, self.bearish_ratio_mean = get_min_max_mean([result['BearishRatio'] for result in results])
        self.first_bullish_cnt, self.first_bearish_cnt = 0, 0
        for result in results:
            if result['FirstIncome'] == "Bull":
                self.first_bullish_cnt += 1
            else:
                self.first_bearish_cnt += 1

        self.last_index = 1
        self.draw(detected_list)

        self.data = self.data[-10:]

        self.chart_tool.set_speed(5000)
        self.chart_tool.set_candle_start_delay(20)

    def on_tick(self, time, bid, ask):
        pass

    def on_data(self, candle):
        self.data.pop(0)

        detected_list = CandleSticks.get_candlesticks(self.data, self.candle_type)
        if len(detected_list) > 0 and detected_list[-1]['Time'] == self.data[-1]['Time']:
            self.draw([detected_list[-1]])
            if self.telegram:
                self.take_photo(self.candle_type, self.last_index)
            if self.trade_enable:
                self.trade(detected_list[-1])

        self.data.append(candle)

    def draw(self, detected_list):
        names, times, prices = [], [], []
        for i in range(len(detected_list)):
            names.append(f"{self.candle_type} {self.last_index}")
            times.append(detected_list[i]['Time'])
            prices.append(detected_list[i]['Price'])
            self.last_index += 1
        self.chart_tool.arrow(names, times, prices, 252, self.chart_tool.EnumArrowAnchor.Top, width=self.width, color=self.color)

        self.chart_tool.rectangle_label(["RectLabel"], [self.rect_x + self.rect_width], [self.rect_y], [self.rect_width], [self.rect_height],
                                   back_color=self.rect_color, color="200,199,199", border=self.chart_tool.EnumBorder.Sunken, corner=self.chart_tool.EnumBaseCorner.RightUpper)
        division = 10
        names, x, y, texts = ["NameLabel"], [self.rect_x + (self.rect_width // 2)], [self.rect_y + (self.rect_height // division)], [self.label]
        self.add_label("BullishRatioMean", self.rect_x + (self.rect_width // 2), self.rect_y + 3 * (self.rect_height // division), f"Bullish Ratio Mean = {abs(round(self.bullish_ratio_mean, 3))} %", names, x, y, texts)
        self.add_label("BearishRatioMean", self.rect_x + (self.rect_width // 2), self.rect_y + 5 * (self.rect_height // division), f"Bearish Ratio Mean = {abs(round(self.bearish_ratio_mean, 3))} %", names, x, y, texts)
        self.add_label("BullishFirstIncome", self.rect_x + (self.rect_width // 2), self.rect_y + 7 * (self.rect_height // division), f"Bullish First Income = {self.first_bullish_cnt}", names, x, y, texts)
        self.add_label("BearishFirstIncome", self.rect_x + (self.rect_width // 2), self.rect_y + 9 * (self.rect_height // division), f"Bearish First Income = {self.first_bearish_cnt}", names, x, y, texts)

        self.chart_tool.label(names, x, y,texts, corner=self.chart_tool.EnumBaseCorner.RightUpper,
                              anchor=self.chart_tool.EnumAnchor.Top, font="Times New Roman", font_size=12)

    def add_label(self, name, x, y, text, name_list, x_list, y_list, text_list):
        name_list.append(name)
        x_list.append(x)
        y_list.append(y)
        text_list.append(text)

    def take_photo(self, name, counter):
        self.chart_tool.set_speed(0.01)

        self.chart_tool.take_screen_shot(f"{self.symbol}_{name}{counter}", self.symbol)
        caption = f"{name} Detected\nSymbol : {self.symbol}\nTime : {self.data[-1]['Time']}"
        self.chart_tool.send_telegram_photo(f"{self.chart_tool.screen_shots_directory}/{self.symbol}_{name}{counter}.png",
                                            self.telegram_channel_name, caption)

        self.chart_tool.set_speed(10000)

    def trade(self, detected):
        if detected['Direction'] == 1:
            self.chart_tool.buy(self.symbol, 0.1, 200, 200)
        else:
            self.chart_tool.sell(self.symbol, 0.1, 200, 200)

