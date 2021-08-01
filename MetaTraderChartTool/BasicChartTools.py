from MetaTraderChartTool.Api.CyrusChartToolConnector import ChartToolConnector
from MetaTraderChartTool.Modules.Execution import Execution
from MetaTraderChartTool.Modules.Reporting import Reporting
from AlgorithmTools.FiboTools import get_fib_levels


class BasicChartTools(object):

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

    def __init__(self, _pulldata_handlers=[],  # Handlers to process Data received through PULL port.
                 _subdata_handlers=[],  # Handlers to process Data received through SUB port.
                 _verbose=False):
        self.date_format = "%Y.%m.%d %H:%M:%S"

        self.connector = ChartToolConnector(_pulldata_handlers=_pulldata_handlers,
                                            _subdata_handlers=_subdata_handlers,
                                            _verbose=_verbose)

        self.execution = Execution(self.connector)
        self.reporting = Reporting(self.connector)

    # Format : "VLINE" | ChartId | Name | SubWindow | Time | Color | Style | Width | Back | Selection | Hidden | ZOrder
    def v_line(self, names, times, chart_id=0, sub_window=0, color="255,255,255", style=0, width=1, back=0, selection=1,
               hidden=1, z_order=0):
        if not self._check_equal_lens(times, names, "Times len should be equal to Names len") or \
                not self._check_lens(times, "VLine Error (Time len can't be zero"):
            return

        names_str = self._get_str_list(names)
        times_str = self._get_str_time_list(times)

        params = "{};{};{};{};{};{};{};{};{};{};{};{}".format("VLINE", chart_id, names_str, sub_window,
                                                              times_str, color, style, width,
                                                              back, selection, hidden, z_order)

        self.execution.execute(params)

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

        self.execution.execute(params)

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

        self.execution.execute(params)

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

        self.execution.execute(params)

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

        self.execution.execute(params)

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

        self.execution.execute(params)

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

        self.execution.execute(params)

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

        self.execution.execute(params)

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

        self.execution.execute(params)

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

        self.execution.execute(params)

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

        self.execution.execute(params)

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

        self.execution.execute(params)

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

        self.execution.execute(params)

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

        self.execution.execute(params)

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

        for i in range(len(names)):
            fib_levels = get_fib_levels(prices1[i], prices2[i])
            for key in fib_levels.keys():
                fib_names.append(f"{key}_{names[i]}")
                fib_times1.append(times1[i])
                fib_times2.append(times2[i])
                fib_prices1.append(fib_levels[key])
                fib_prices2.append(fib_levels[key])

        self.trend_line(fib_names, fib_times1, fib_prices1, fib_times2, fib_prices2, chart_id, sub_window, color, style, width, back, selection, ray, hidden, z_order)



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
            out_str += "," + input_list[i].strftime(self.date_format)
        return out_str

    def _get_str_list(self, input_list):
        out_str = f"{input_list[0]}"
        for i in range(1, len(input_list)):
            out_str += f",{input_list[i]}"
        return out_str
