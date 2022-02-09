
from MetaTrader.Api.CyrusMetaConnector import CyrusMetaConnector
from MetaTrader.Modules.Execution import Execution
from MetaTrader.Modules.Reporting import Reporting
from AlgorithmFactory.AlgorithmTools.FiboTools import get_fib_levels
import requests


class MetaTraderBase:

    class EnumStyle:
        Solid = 0
        Dash = 1
        Dot = 2
        DashDot = 3
        DashDotDot = 4

    class EnumArrowAnchor:
        Top = 0
        Bottom = 1

    class EnumAnchor:
        LeftUpper = 0
        Left = 1
        LeftLower = 2
        Bottom = 3
        RightLower = 4
        Right = 5
        RightUpper = 6
        Top = 7

    class EnumBaseCorner:
        LeftUpper = 0
        RightUpper = 1
        LeftLower = 2
        RightLower = 3

    class EnumBorder:
        Flat = 0
        Raised = 1
        Sunken = 2
    
    def __init__(self, name="Polaris",
                 symbols=None,
                 broker_gmt=3,                 # GMT offset
                 pull_data_handlers=None,       # Handlers to process Data received through PULL port.
                 sub_data_handlers=None,        # Handlers to process Data received through SUB port.
                 verbose=False,
                 push_port=32768,  # Port for Sending commands
                 pull_port=32769,  # Port for Receiving responses
                 sub_port=32770):  # Print messages
                 
        self.name = name
        self.symbols = symbols
        self.broker_gmt = broker_gmt

        self.token = "2131560525:AAH4ajtB__uKllIFGnDTKEcenGjfyBMOO_s"
        self.screen_shots_directory = "C:/Users/Polaris-Maju1/AppData/Roaming/MetaQuotes/Terminal/4694969650DF66FD9340C36ED4D0052A/tester/Files"
        # Not entirely necessary here.
        self.connector = CyrusMetaConnector(pull_data_handlers=pull_data_handlers, sub_data_handlers=sub_data_handlers,
                                            verbose=verbose, push_port=push_port,  pull_port=pull_port, sub_port=sub_port)
        
        # Modules
        self.execution = Execution(self.connector)
        self.reporting = Reporting(self.connector)

        self.date_format = "%Y.%m.%d %H:%M:%S"
        self.names_splitter = "$"
    
    def __del__(self):
        self.connector.shutdown()

    def send_telegram_message(self, message, channel_name):
        request_url = f"https://api.telegram.org/bot{self.token}/sendMessage?chat_id={channel_name}&text={message}"
        requests.get(request_url)

    def send_telegram_photo(self, photo_directory, channel_name, caption=""):
        url = f"https://api.telegram.org/bot{self.token}/"
        requests.post(url + 'sendPhoto', data={'chat_id': channel_name, 'caption': caption},
                      files={'photo': open(f"{photo_directory}", 'rb')})

    def _take_order(self, type, symbol, volume, tp, sl):
        order = self.connector.generate_default_order_dict()
        order['_type'] = type
        order['_symbol'] = symbol
        order['_lots'] = volume
        order['_TP'] = tp
        order['_SL'] = sl
        trade = self.execution.trade_execute(order)
        return trade

    def buy(self, symbol, volume, tp, sl):
        return self._take_order(0, symbol, volume, tp, sl)

    def sell(self, symbol, volume, tp, sl):
        return self._take_order(1, symbol, volume, tp, sl)

    def modify(self, ticket, tp, sl):
        order = self.connector.generate_default_order_dict()
        order['_action'] = 'MODIFY'
        order['_ticket'] = ticket
        order['_TP'] = tp
        order['_SL'] = sl
        trade = self.execution.trade_execute(order)
        return trade

    def close(self, ticket):
        order = self.connector.generate_default_order_dict()
        order['_action'] = 'CLOSE'
        order['_ticket'] = ticket
        return self.execution.trade_execute(order)

    def get_open_positions(self):
        return self.reporting.get_open_trades()

    def take_screen_shot(self, name, symbol):
        self.execution.screenshot_execute(name, symbol)

    def set_scale(self, symbol, scale):
        self.execution.set_settings_execute(symbol, scale, type="Scale")

    def set_speed(self, speed):
        self.execution.set_settings_execute("", speed, "Speed")

    def set_candle_start_delay(self, ticks_number):
        self.execution.set_settings_execute("", ticks_number, "CandleDelay")

    def clear(self):
        self.connector.send_clear_request()

    def delete(self, names, chart_id=0):
        if not self._check_lens(names, "Delete (Name len can't be zero)"):
            return

        names_str = self._get_str_list(names)

        params = "{};{}".format(chart_id, names_str)

        self.execution.draw_execute(params, type="DELETE")

    # Format : "VLINE" | ChartId | Name | SubWindow | Time | Color | Style | Width | Back | Selection | Hidden | ZOrder
    def v_line(self, names, times, chart_id=0, sub_window=0, color="255,255,255", style=0, width=1, back=0, selection=1,
               hidden=1, z_order=0):
        if not self._check_equal_lens(times, names, "Times len should be equal to Names len") or \
                not self._check_lens(times, "VLine Error (Time len can't be zero)"):
            return

        names_str = self._get_str_list(names)
        times_str = self._get_str_time_list(times)

        params = "{};{};{};{};{};{};{};{};{};{};{};{}".format("VLINE", chart_id, names_str, sub_window,
                                                              times_str, color, style, width,
                                                              back, selection, hidden, z_order)

        self.execution.draw_execute(params)

    # Format : "HLINE" | ChartId | Name | SubWindow | Time | Color | Style | Width | Back | Selection | Hidden | ZOrder
    def h_line(self, names, prices, chart_id=0, sub_window=0, color="255,255,255", style=0, width=1, back=0,
               selection=1, hidden=1, z_order=0):
        if not self._check_equal_lens(prices, names, "Prices len should be equal to Names len") or \
                not self._check_lens(prices, "HLine Error (Prices len can't be zero"):
            return

        names_str = self._get_str_list(names)
        prices_str = self._get_str_list(prices)

        params = "{};{};{};{};{};{};{};{};{};{};{};{}".format("HLINE", chart_id, names_str, sub_window,
                                                              prices_str, color, style, width,
                                                              back, selection, hidden, z_order)

        self.execution.draw_execute(params)

    # Format : "TREND" | ChartId | Name | SubWindow | Time1 | Price1 | Time2 | Price2 | Color | Style | Width | Back | Selection | Ray | Hidden | ZOrder
    def trend_line(self, names, times1, prices1, times2, prices2, chart_id=0, sub_window=0, color="255,255,255", style=0, width=1, back=0,
               selection=1, ray=0, hidden=1, z_order=0):
        if not self._check_equal_lens(times1, names, "Times1 len should be equal to Names len") or \
                not self._check_equal_lens(times1, times2, "Times1 len should be equal to Times2 len") or \
                not self._check_equal_lens(prices1, prices2, "Prices1 len should be equal to Prices2 len") or \
                not self._check_lens(times1, "TREND Error (Time len can't be zero") or \
                not self._check_lens(times2, "TREND Error (Time len can't be zero") or \
                not self._check_lens(prices1, "TREND Error (Price len can't be zero") or \
                not self._check_lens(prices2, "TREND Error (Price len can't be zero"):
            return

        names_str = self._get_str_list(names)
        times1_str = self._get_str_time_list(times1)
        times2_str = self._get_str_time_list(times2)
        prices1_str = self._get_str_list(prices1)
        prices2_str = self._get_str_list(prices2)


        params = "{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{}".format("TREND", chart_id, names_str, sub_window,
                                                                       times1_str, prices1_str, times2_str, prices2_str, color, style, width,
                                                                       back, selection, ray, hidden, z_order)

        self.execution.draw_execute(params)

    # Format : "RECTANGLE" | ChartId | Name | SubWindow | Time1 | Price1 | Time2 | Price2 | Color | Style | Width | Back | Selection | Hidden | ZOrder
    def rectangle(self, names, times1, prices1, times2, prices2, chart_id=0, sub_window=0, color="255,255,255",
                   style=0, width=1, fill=0, back=0, selection=1, hidden=1, z_order=0):
        if not self._check_equal_lens(times1, names, "Times1 len should be equal to Names len") or \
                not self._check_equal_lens(times1, times2, "Times1 len should be equal to Times2 len") or \
                not self._check_equal_lens(prices1, prices2, "Prices1 len should be equal to Prices2 len") or \
                not self._check_lens(times1, "RECTANGLE Error (Time len can't be zero") or \
                not self._check_lens(times2, "RECTANGLE Error (Time len can't be zero") or \
                not self._check_lens(prices1, "RECTANGLE Error (Price len can't be zero") or \
                not self._check_lens(prices2, "RECTANGLE Error (Price len can't be zero"):
            return

        names_str = self._get_str_list(names)
        times1_str = self._get_str_time_list(times1)
        times2_str = self._get_str_time_list(times2)
        prices1_str = self._get_str_list(prices1)
        prices2_str = self._get_str_list(prices2)

        params = "{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{}".format("RECTANGLE", chart_id, names_str, sub_window,
                                                                          times1_str, prices1_str, times2_str,
                                                                          prices2_str, color, style, width,
                                                                          fill, back, selection, hidden, z_order)

        self.execution.draw_execute(params)

    # Format : "TRIANGLE" | ChartId | Name | SubWindow | Time1 | Price1 | Time2 | Price2 | Color | Style | Width | Back | Selection | Hidden | ZOrder
    def triangle(self, names, times1, prices1, times2, prices2, times3, prices3, chart_id=0, sub_window=0, color="255,255,255",
                  style=0, width=1, fill=0, back=0, selection=1, hidden=1, z_order=0):
        if not self._check_equal_lens(times1, names, "Times1 len should be equal to Names len") or \
                not self._check_equal_lens(times1, times2, "Times1 len should be equal to Times2 len") or \
                not self._check_equal_lens(prices1, prices2, "Prices1 len should be equal to Prices2 len") or \
                not self._check_lens(times1, "TRIANGLE Error (Time len can't be zero") or \
                not self._check_lens(times2, "TRIANGLE Error (Time len can't be zero") or \
                not self._check_lens(prices1, "TRIANGLE Error (Price len can't be zero") or \
                not self._check_lens(prices2, "TRIANGLE Error (Price len can't be zero") or\
                not self._check_lens(times3, "TRIANGLE Error (Time len can't be zero") or \
                not self._check_lens(prices3, "TRIANGLE Error (Price len can't be zero"):
            return

        names_str = self._get_str_list(names)
        times1_str = self._get_str_time_list(times1)
        times2_str = self._get_str_time_list(times2)
        times3_str = self._get_str_time_list(times3)
        prices1_str = self._get_str_list(prices1)
        prices2_str = self._get_str_list(prices2)
        prices3_str = self._get_str_list(prices3)

        params = "{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{}".format("TRIANGLE", chart_id, names_str,
                                                                          sub_window, times1_str, prices1_str, times2_str,
                                                                          prices2_str, times3_str, prices3_str, color, style, width,
                                                                          fill, back, selection, hidden, z_order)

        self.execution.draw_execute(params)

    # Format : "Ellipse" | ChartId | Name | SubWindow | Time1 | Price1 | Time2 | Price2 | EllipseScales | Color | Style | Width | Back | Selection | Hidden | ZOrder
    def ellipse(self, names, times1, prices1, times2, prices2, ellipse_scales, chart_id=0, sub_window=0, color="255,255,255",
                  style=0, width=1, fill=0, back=0, selection=1, hidden=1, z_order=0):
        if not self._check_equal_lens(times1, names, "Times1 len should be equal to Names len") or \
                not self._check_equal_lens(times1, times2, "Times1 len should be equal to Times2 len") or \
                not self._check_equal_lens(prices1, prices2, "Prices1 len should be equal to Prices2 len") or \
                not self._check_lens(times1, "ELLIPSE Error (Time len can't be zero") or \
                not self._check_lens(times2, "ELLIPSE Error (Time len can't be zero") or \
                not self._check_lens(prices1, "ELLIPSE Error (Price len can't be zero") or \
                not self._check_lens(prices2, "ELLIPSE Error (Price len can't be zero") or \
                not self._check_lens(ellipse_scales, "ELLIPSE Error (Scales len can't be zero"):
            return

        names_str = self._get_str_list(names)
        times1_str = self._get_str_time_list(times1)
        times2_str = self._get_str_time_list(times2)
        prices1_str = self._get_str_list(prices1)
        prices2_str = self._get_str_list(prices2)
        scales_str = self._get_str_list(ellipse_scales)

        params = "{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{}".format("ELLIPSE", chart_id, names_str,
                                                                          sub_window, times1_str, prices1_str, times2_str,
                                                                          prices2_str, scales_str, color, style, width,
                                                                          fill, back, selection, hidden, z_order)

        self.execution.draw_execute(params)

    # Format : "THUMBUP" | ChartId | Name | SubWindow | Time | Price | Anchor | Color | Style | Width | Back | Selection | Hidden | ZOrder
    def thumb_up(self, names, times, prices, anchor, chart_id=0, sub_window=0, color="255,255,255", style=0, width=1, back=0,
               selection=1,
               hidden=1, z_order=0):
        if not self._check_equal_lens(times, names, "Times len should be equal to Names len") or \
                not self._check_lens(times, "ThumbUp Error (Time len can't be zero"):
            return

        names_str = self._get_str_list(names)
        times_str = self._get_str_time_list(times)
        prices_str = self._get_str_list(prices)

        params = "{};{};{};{};{};{};{};{};{};{};{};{};{};{}".format("THUMBUP", chart_id, names_str, sub_window,
                                                              times_str, prices_str, anchor, color, style, width,
                                                              back, selection, hidden, z_order)

        self.execution.draw_execute(params)

    # Format : "THUMBDOWN" | ChartId | Name | SubWindow | Time | Price | Anchor | Color | Style | Width | Back | Selection | Hidden | ZOrder
    def thumb_down(self, names, times, prices, anchor, chart_id=0, sub_window=0, color="255,255,255", style=0,
                 width=1, back=0, selection=1, hidden=1, z_order=0):
        if not self._check_equal_lens(times, names, "Times len should be equal to Names len") or \
                not self._check_lens(times, "ThumbDown Error (Time len can't be zero"):
            return

        names_str = self._get_str_list(names)
        times_str = self._get_str_time_list(times)
        prices_str = self._get_str_list(prices)

        params = "{};{};{};{};{};{};{};{};{};{};{};{};{};{}".format("THUMBDOWN", chart_id, names_str, sub_window,
                                                                    times_str, prices_str, anchor, color, style,
                                                                    width,
                                                                    back, selection, hidden, z_order)

    # Format : "ARROW" | ChartId | Name | SubWindow | Time | Price | Arrow | Anchor | Color | Style | Width | Back | Selection | Hidden | ZOrder
    def arrow(self, names, times, prices, arrow_code, anchor, chart_id=0, sub_window=0, color="255,255,255", style=0,
                 width=1, back=0, selection=1, hidden=1, z_order=0):
        if not self._check_equal_lens(times, names, "Times len should be equal to Names len") or \
                not self._check_lens(times, "ArrowUp Error (Time len can't be zero"):
            return

        names_str = self._get_str_list(names)
        times_str = self._get_str_time_list(times)
        prices_str = self._get_str_list(prices)

        params = "{};{};{};{};{};{};{};{};{};{};{};{};{};{};{}".format("ARROW", chart_id, names_str, sub_window,
                                                                    times_str, prices_str, arrow_code, anchor, color, style,
                                                                    width, back, selection, hidden, z_order)

        self.execution.draw_execute(params)

    # Format : "ARROWUP" | ChartId | Name | SubWindow | Time | Price | Anchor | Color | Style | Width | Back | Selection | Hidden | ZOrder
    def arrow_up(self, names, times, prices, anchor, chart_id=0, sub_window=0, color="255,255,255", style=0,
                   width=1, back=0, selection=1, hidden=1, z_order=0):
        if not self._check_equal_lens(times, names, "Times len should be equal to Names len") or \
                not self._check_lens(times, "ArrowUp Error (Time len can't be zero"):
            return

        names_str = self._get_str_list(names)
        times_str = self._get_str_time_list(times)
        prices_str = self._get_str_list(prices)

        params = "{};{};{};{};{};{};{};{};{};{};{};{};{};{}".format("ARROWUP", chart_id, names_str, sub_window,
                                                                    times_str, prices_str, anchor, color, style, width,
                                                                    back, selection, hidden, z_order)

        self.execution.draw_execute(params)

    # Format : "ARROWDOWN" | ChartId | Name | SubWindow | Time | Price | Anchor | Color | Style | Width | Back | Selection | Hidden | ZOrder
    def arrow_down(self, names, times, prices, anchor, chart_id=0, sub_window=0, color="255,255,255", style=0,
                 width=1, back=0, selection=1, hidden=1, z_order=0):
        if not self._check_equal_lens(times, names, "Times len should be equal to Names len") or \
                not self._check_lens(times, "ArrowDown Error (Time len can't be zero"):
            return

        names_str = self._get_str_list(names)
        times_str = self._get_str_time_list(times)
        prices_str = self._get_str_list(prices)

        params = "{};{};{};{};{};{};{};{};{};{};{};{};{};{}".format("ARROWDOWN", chart_id, names_str, sub_window,
                                                                    times_str, prices_str, anchor, color, style,
                                                                    width, back, selection, hidden, z_order)

        self.execution.draw_execute(params)

    # Format : "ARROWBUY" | ChartId | Name | SubWindow | Time | Price | Color | Style | Width | Back | Selection | Hidden | ZOrder
    def arrow_buy(self, names, times, prices, chart_id=0, sub_window=0, color="255,255,255", style=0,
                   width=1, back=0, selection=1, hidden=1, z_order=0):
        if not self._check_equal_lens(times, names, "Times len should be equal to Names len") or \
                not self._check_lens(times, "ArrowBuy Error (Time len can't be zero"):
            return

        names_str = self._get_str_list(names)
        times_str = self._get_str_time_list(times)
        prices_str = self._get_str_list(prices)

        params = "{};{};{};{};{};{};{};{};{};{};{};{};{}".format("ARROWBUY", chart_id, names_str, sub_window,
                                                                    times_str, prices_str, color, style,
                                                                    width, back, selection, hidden, z_order)

        self.execution.draw_execute(params)

    # Format : "ARROWSELL" | ChartId | Name | SubWindow | Time | Price | Color | Style | Width | Back | Selection | Hidden | ZOrder
    def arrow_sell(self, names, times, prices, chart_id=0, sub_window=0, color="255,255,255", style=0,
                  width=1, back=0, selection=1, hidden=1, z_order=0):
        if not self._check_equal_lens(times, names, "Times len should be equal to Names len") or \
                not self._check_lens(times, "ArrowSell Error (Time len can't be zero"):
            return

        names_str = self._get_str_list(names)
        times_str = self._get_str_time_list(times)
        prices_str = self._get_str_list(prices)

        params = "{};{};{};{};{};{};{};{};{};{};{};{};{}".format("ARROWSELL", chart_id, names_str, sub_window,
                                                                 times_str, prices_str, color, style,
                                                                 width, back, selection, hidden, z_order)

        self.execution.draw_execute(params)

    # Format : "TEXT" | ChartId | Name | SubWindow | Time | Price | Text | Font | FontSize | Color | Angle | Anchor | Back | Selection | Hidden | ZOrder
    def text(self, names, times, prices, texts, font="Arial", font_size=10, angle=0.0, chart_id=0, sub_window=0,
             color="255,255,255", anchor=EnumAnchor.Top, back=0, selection=1, hidden=1, z_order=0):
        if not self._check_equal_lens(times, names, "Times len should be equal to Names len") or \
                not self._check_lens(times, "Text Error (Time len can't be zero"):
            return

        names_str = self._get_str_list(names)
        times_str = self._get_str_time_list(times)
        prices_str = self._get_str_list(prices)
        texts_str = self._get_str_list(texts)

        params = "{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{}".format("TEXT", chart_id, names_str, sub_window,
                                                                          times_str, prices_str, texts_str, font, font_size,
                                                                          color, angle, anchor,
                                                                          back, selection, hidden, z_order)

        self.execution.draw_execute(params)

    # Format : "LABEL" | ChartId | Name | SubWindow | X | Y | Corner | Text | Font | FontSize | Color | Angle | Anchor | Back | Selection | Hidden | ZOrder
    def label(self, names, x, y, texts, corner=EnumBaseCorner.LeftUpper, font="Arial", font_size=10, angle=0.0,
              chart_id=0, sub_window=0,
             color="255,255,255", anchor=EnumAnchor.Top, back=0, selection=1, hidden=1, z_order=0):
        if not self._check_equal_lens(x, names, "X len should be equal to Names len") or \
                not self._check_lens(y, "Y len should be equal to Names len") or \
                not self._check_lens(y, "Label Error (Y len can't be zero"):
            return

        names_str = self._get_str_list(names)
        x_str = self._get_str_list(x)
        y_str = self._get_str_list(y)
        texts_str = self._get_str_list(texts)

        params = "{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{}".format("LABEL", chart_id, names_str, sub_window,
                                                                          x_str, y_str, corner, texts_str, font,
                                                                          font_size, color, angle, anchor,
                                                                          back, selection, hidden, z_order)

        self.execution.draw_execute(params)

    # Format : "RECTLABEL" | ChartId | Name | SubWindow | X | Y | Width | Height | BackColor | Border | Corner | Color | Style | LineWidth | Back | Selection | Hidden | ZOrder
    def rectangle_label(self, names, x, y, width, height, chart_id=0, sub_window=0, back_color="40,200,255",
                        border=EnumBorder.Flat, corner=EnumBaseCorner.LeftUpper, style=EnumStyle.Solid, line_width=1,
                        color="200,200,255", back=0, selection=1, hidden=1, z_order=0):
        if not self._check_equal_lens(x, names, "X len should be equal to Names len") or \
                not self._check_lens(y, "Y len should be equal to Names len") or \
                not self._check_lens(y, "RectLabel Error (Y len can't be zero"):
            return

        names_str = self._get_str_list(names)
        x_str = self._get_str_list(x)
        y_str = self._get_str_list(y)
        width_str = self._get_str_list(width)
        height_str = self._get_str_list(height)

        params = "{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{}".format("RECTLABEL", chart_id, names_str,
                                                                                sub_window,
                                                                                x_str, y_str, width_str, height_str,
                                                                                back_color, border, corner, color,
                                                                                style, line_width, back, selection,
                                                                                hidden, z_order)

        self.execution.draw_execute(params)

    def fibonacci_retracement(self, names, times1, prices1, times2, prices2, chart_id=0, sub_window=0, color="255,255,255", style=0, width=1, back=0,
                              selection=1, ray=0, hidden=1, z_order=0):
        if not self._check_equal_lens(times1, names, "Times1 len should be equal to Names len") or \
                not self._check_equal_lens(times1, times2, "Times1 len should be equal to Times2 len") or \
                not self._check_equal_lens(prices1, prices2, "Prices1 len should be equal to Prices2 len") or \
                not self._check_lens(times1, "TREND Error (Time len can't be zero") or \
                not self._check_lens(times2, "TREND Error (Time len can't be zero") or \
                not self._check_lens(prices1, "TREND Error (Price len can't be zero") or \
                not self._check_lens(prices2, "TREND Error (Price len can't be zero"):
            return

        fib_names = []
        fib_times1, fib_times2 = [], []
        fib_prices1, fib_prices2 = [], []

        fib_names_text = []
        fib_times_text = []
        fib_prices_text = []
        fib_texts = []

        for i in range(len(names)):
            fib_levels = get_fib_levels(prices1[i], prices2[i])
            for key in fib_levels.keys():
                fib_names.append(f"{key}_{names[i]}")
                fib_times1.append(times1[i])
                fib_times2.append(times2[i])
                fib_prices1.append(fib_levels[key])
                fib_prices2.append(fib_levels[key])

                fib_names_text.append(f"{key}_{names[i]}t")
                fib_times_text.append(times2[i])
                fib_prices_text.append(fib_levels[key])
                fib_texts.append(f'{key}')

        self.trend_line(fib_names, fib_times1, fib_prices1, fib_times2, fib_prices2, chart_id, sub_window, color, style, width, back, selection, ray, hidden, z_order)
        self.text(fib_names_text, fib_times_text, fib_prices_text, fib_texts, anchor=MetaTraderBase.EnumAnchor.RightLower, color=color)

    def _check_lens(self, input_list, message):
        if len(input_list) == 0:
            print(message)
            return False
        return True

    def _check_equal_lens(self, input_list1, input_list2, message):
        if len(input_list1) != len(input_list2):
            print(message)
            return False
        return True

    def _get_str_time_list(self, input_list):
        out_str = input_list[0].strftime(self.date_format)
        for i in range(1, len(input_list)):
            out_str += f"{self.names_splitter}" + input_list[i].strftime(self.date_format)
        return out_str

    def _get_str_list(self, input_list):
        out_str = f"{input_list[0]}"
        for i in range(1, len(input_list)):
            out_str += f"{self.names_splitter}{input_list[i]}"
        return out_str
