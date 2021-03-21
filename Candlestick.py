
from ta import trend
from pandas.plotting import register_matplotlib_converters
import pandas as pd
from bokeh.io import show
from bokeh.layouts import column
from bokeh.plotting import figure
from bokeh.models import CustomJS, ColumnDataSource, HoverTool, NumeralTickFormatter, Arrow, VeeHead, Range1d
from Simulation.Config import Config
register_matplotlib_converters()



def candlestick_plot(df, name, lines = None, extend_lines = None, localMax = None, localMin = None, marker = None, buyMarker = None, sellMarker = None):
    # Select the datetime format for the x axis depending on the timeframe
    df = df.reset_index()

    xaxis_dt_format = '%d.%m.%Y %H:%M:%S'
    if name[-3:] == "JPY":
        number_format1 = '%0.3f'
    elif name == "XAUUSD":
        number_format1 = '%0.2f'
    else:
        number_format1 = '%0.5f'
    number_format2 = '%0.' + str(Config.volume_digit) + 'f'
    number_format3 = '%0.1f'
    # if df['GMT'][start].hour > 0:
    #     xaxis_dt_format = '%d %b %Y, %H:%M:%S'


    pad_x = 100
    fig = figure(sizing_mode='stretch_both',
                 tools="xpan,xwheel_zoom,reset,save",
                 active_drag='xpan',
                 active_scroll='xwheel_zoom',
                 x_axis_type='linear',
                 x_range=Range1d(df.index[0] - pad_x, df.index[-1] + pad_x, bounds="auto"),
                 title=name
                 )
    fig.yaxis[0].formatter = NumeralTickFormatter(format="7.5f")
    inc = df.Close > df.Open
    dec = ~inc

    # Colour scheme for increasing and descending candles
    # INCREASING_COLOR = '#17BECF'
    # DECREASING_COLOR = '#7F7F7F'
    INCREASING_COLOR = '#FFFFFF'
    DECREASING_COLOR = '#000000'
    SHADOW_COLOR = '#000000'
    BUY_COLOR = '#72a1dc'
    SELL_COLOR = '#f9584a'
    BUY_CLOSE_COLOR = '#5299D3'
    SELL_CLOSE_COLOR = '#F82F1C'
    BUY_LINE_COLOR = '#3f73aa'
    SELL_LINE_COLOR = '#bf1e21'
    UP_TREND_COLOR = '#11ee11'
    DOWN_TREND_COLOR = '#eeee11'


    inc_source = ColumnDataSource(data=dict(
        x1=df.index[inc],
        top1=df.Open[inc],
        bottom1=df.Close[inc],
        high1=df.High[inc],
        low1=df.Low[inc],
        date1=df.GMT[inc]
    ))

    dec_source = ColumnDataSource(data=dict(
        x2=df.index[dec],
        top2=df.Open[dec],
        bottom2=df.Close[dec],
        high2=df.High[dec],
        low2=df.Low[dec],
        date2=df.GMT[dec]
    ))

    # sizing settings
    candle_width = 0.5
    positions_line_width = 3
    arrow_size = 6

    # Plot candles
    # High and low

    fig.segment(x0='x1', y0='high1', x1='x1', y1='low1', source=inc_source, color=SHADOW_COLOR)
    fig.segment(x0='x2', y0='high2', x1='x2', y1='low2', source=dec_source, color=SHADOW_COLOR)

    # Open and close
    r1 = fig.vbar(x='x1', width=candle_width, top='top1', bottom='bottom1', source=inc_source,
                    fill_color=INCREASING_COLOR, line_color="black")
    r2 = fig.vbar(x='x2', width=candle_width, top='top2', bottom='bottom2', source=dec_source,
                    fill_color=DECREASING_COLOR, line_color="black")

    color = ['blue', 'red']
    j = -1
    if lines != None:
        for line in lines:
            j += 1
            index = line['x']
            price = line['y']
            for i in range(len(index)):
                fig.line(x=index[i], y=price[i], line_color=color[j], line_width=i + 1)

    j = -1
    if extend_lines != None:
        for extend in extend_lines:
            j += 1
            index = extend['x']
            price = extend['y']
            for i in range(len(index)):
                fig.line(x=index[i], y=price[i], line_color=color[j], line_width=2, line_dash="dotted")

    if localMax is not None:
        fig.circle(localMax, df.High[localMax], size=5, color="red")
    if localMax is not None:
        fig.circle(localMin, df.Low[localMin], size=5, color="blue")

    if marker is not None:
        marker_source = ColumnDataSource(data=dict(
            x=marker['x'],
            y=marker['y']
        ))
        markers = fig.circle(x='x', y='y', size=4, color="brown", source=marker_source)
        fig.add_tools(HoverTool(
            renderers=[markers],
            tooltips=[
                ("Value", "@y{" + number_format1 + "}"),
            ],
            formatters={
                '@y': 'printf'
            }))

    if buyMarker is not None:
        fig.circle(buyMarker['x'], buyMarker['y'], size=4, color="blue")

    if sellMarker is not None:
        fig.circle(sellMarker['x'], sellMarker['y'], size=4, color="red")

    # Set up the hover tooltip to display some useful Data
    fig.add_tools(HoverTool(
        renderers=[r1],
        tooltips=[
            ("Open", "@top1{" + number_format1 + "}"),
            ("High", "@high1{" + number_format1 + "}"),
            ("Low", "@low1{" + number_format1 + "}"),
            ("Close", "@bottom1{" + number_format1 + "}"),
            ("Date", "@date1{" + xaxis_dt_format + "}")
        ],
        formatters={
            '@date1': 'datetime',
            '@top1': 'printf',
            '@high1': 'printf',
            '@low1': 'printf',
            '@bottom1': 'printf'
        }))

    fig.add_tools(HoverTool(
        renderers=[r2],
        tooltips=[
            ("Open", "@top2{" + number_format1 + "}"),
            ("High", "@high2{" + number_format1 + "}"),
            ("Low", "@low2{" + number_format1 + "}"),
            ("Close", "@bottom2{" + number_format1 + "}"),
            ("Date", "@date2{" + xaxis_dt_format + "}")
        ],
        formatters={
            '@date2': 'datetime',
            '@top2': 'printf',
            '@high2': 'printf',
            '@low2': 'printf',
            '@bottom2': 'printf'
        }))

    # Add on extra lines (e.g. moving averages) here
    # fig.line(df.index, <your Data>)

    # Add on a vertical line to indicate a trading signal here
    # vline = Span(location=df.index[-<your index>, dimension='height',
    #              line_color="green", line_width=2)
    # fig.renderers.extend([vline])

    # Add date labels to x axis
    fig.xaxis.major_label_overrides = {
        i: date.strftime(xaxis_dt_format) for i, date in enumerate(pd.to_datetime(df["GMT"], utc=True))
    }



    # JavaScript callback function to automatically zoom the Y axis to
    # view the Data properly
    source = ColumnDataSource({'Index': df.index, 'High': df.High, 'Low': df.Low})
    callback = CustomJS(args={'y_range_candle': fig.y_range, 'source': source}, code='''
           clearTimeout(window._autoscale_timeout);
           var Index_candle = source.Data.Index,
               Low = source.Data.Low,
               High = source.Data.High,
               start = cb_obj.start,
               end = cb_obj.end,
               min_candle = Infinity,
               max_candle = -Infinity;
           for (var i=0; i < Index_candle.length; ++i) {
               if (start <= Index_candle[i] && Index_candle[i] <= end) {
                   max_candle = Math.max(High[i], max_candle);
                   min_candle = Math.min(Low[i], min_candle);
               }
           }
           var pad_candle = (max_candle - min_candle) * .1;
           window._autoscale_timeout = setTimeout(function() {
               y_range_candle.start = min_candle - pad_candle;
               y_range_candle.end = max_candle + pad_candle;
           });
       ''')

    # Finalise the figure
    fig.x_range.js_on_change('start', callback)

    show(fig)


def add_ema(figure, index, price, window_size, color, width):
    ema = trend.ema(price, window_size)
    figure.line(x=index, y=ema, line_color=color, line_width=width)
