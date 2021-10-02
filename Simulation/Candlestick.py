

from ta import trend
from pandas.plotting import register_matplotlib_converters
import pandas as pd
from bokeh.io import show
from bokeh.io.state import curstate
from bokeh.layouts import column
from bokeh.plotting import figure
from bokeh.models import CustomJS, ColumnDataSource, HoverTool, NumeralTickFormatter, Arrow, VeeHead, Range1d
from Configuration.Trade.BackTestConfig import Config
register_matplotlib_converters()


def candlestick_plot(df, position_df, name, df_balance, df_equity, start, trends, extends):
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
    # if df['Time'][start].hour > 0:
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

    buy = position_df.Type == 'Buy'
    sell = ~buy

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
        date1=df.Time[inc]
    ))

    dec_source = ColumnDataSource(data=dict(
        x2=df.index[dec],
        top2=df.Open[dec],
        bottom2=df.Close[dec],
        high2=df.High[dec],
        low2=df.Low[dec],
        date2=df.Time[dec]
    ))


    buy_line_source = ColumnDataSource(data=dict(
        x7=position_df.Index[buy] - start,
        x8=position_df.IndexEnd[buy] - start,
        price7=position_df.OpenPrice[buy],
        price8=position_df.PriceClose[buy],
        date7=position_df.TimeOpen[buy],
        date8=position_df.TimeClose[buy],
        type1=position_df.Type[buy],
        volume1=position_df.Volume[buy],
        result1=position_df.Result[buy],
        TP1=position_df['T/P'][buy],
        SL1=position_df['S/L'][buy],
        profit1=position_df.Profit[buy],
        profit_in_pip1=position_df['Profit in pip'][buy]
    ))

    sell_line_source = ColumnDataSource(data=dict(
        x9=position_df.Index[sell] - start,
        x10=position_df.IndexEnd[sell] - start,
        price9=position_df.OpenPrice[sell],
        price10=position_df.PriceClose[sell],
        date9=position_df.TimeOpen[sell],
        date10=position_df.TimeClose[sell],
        type2=position_df.Type[sell],
        volume2=position_df.Volume[sell],
        result2=position_df.Result[sell],
        TP2=position_df['T/P'][sell],
        SL2=position_df['S/L'][sell],
        profit2=position_df.Profit[sell],
        profit_in_pip2=position_df['Profit in pip'][sell]
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

    buy_segment = fig.segment(x0='x7', y0='price7', x1='x8', y1='price8', source=buy_line_source,
                              color=BUY_LINE_COLOR, line_width=positions_line_width, line_dash="dotted")
    sell_segment = fig.segment(x0='x9', y0='price9', x1='x10', y1='price10', source=sell_line_source,
                               color=SELL_LINE_COLOR, line_width=positions_line_width, line_dash="dotted")

    open_buy_arrow = Arrow(x_start='x7', y_start='price7', x_end=0, y_end='price7', source=buy_line_source,
                           start=VeeHead(size=arrow_size, fill_color=BUY_COLOR, line_color=BUY_COLOR),
                           end=VeeHead(size=0), line_width=0)
    close_buy_arrow = Arrow(x_start='x8', y_start='price8', x_end=10000000, y_end='price8', source=buy_line_source,
                            start=VeeHead(size=arrow_size, fill_color=BUY_CLOSE_COLOR, line_color=BUY_CLOSE_COLOR),
                            line_width=0)

    fig.add_layout(open_buy_arrow)
    fig.add_layout(close_buy_arrow)

    open_sell_arrow = Arrow(x_start='x9', y_start='price9', x_end=0, y_end='price9', source=sell_line_source,
                            start=VeeHead(size=arrow_size, fill_color=SELL_COLOR, line_color=SELL_COLOR),
                            end=VeeHead(size=0), line_width=0)
    close_sell_arrow = Arrow(x_start='x10', y_start='price10', x_end=10000000, y_end='price10', source=sell_line_source,
                             start=VeeHead(size=arrow_size, fill_color=SELL_CLOSE_COLOR, line_color=SELL_CLOSE_COLOR),
                             line_width=0)

    fig.add_layout(open_sell_arrow)
    fig.add_layout(close_sell_arrow)

    if trends is not None:
        up_trend_source = ColumnDataSource(data=dict(
            x11=trends['xUpTrend']['open'],
            x12=trends['xUpTrend']['close'],
            price11=trends['yUpTrend']['open'],
            price12=trends['yUpTrend']['close']
        ))

        down_trend_source = ColumnDataSource(data=dict(
            x13=trends['xDownTrend']['open'],
            x14=trends['xDownTrend']['close'],
            price13=trends['yDownTrend']['open'],
            price14=trends['yDownTrend']['close']
        ))

        fig.segment(x0='x11', y0='price11', x1='x12', y1='price12', source=up_trend_source,
                    color=UP_TREND_COLOR, line_width=2)
        fig.segment(x0='x13', y0='price13', x1='x14', y1='price14', source=down_trend_source,
                    color=DOWN_TREND_COLOR, line_width=2)

    if extends is not None:
        up_extend_source = ColumnDataSource(data=dict(
            x15=extends['xExtendInc']['open'],
            x16=extends['xExtendInc']['close'],
            price15=extends['yExtendInc']['open'],
            price16=extends['yExtendInc']['close']
        ))

        down_extend_source = ColumnDataSource(data=dict(
            x17=extends['xExtendDec']['open'],
            x18=extends['xExtendDec']['close'],
            price17=extends['yExtendDec']['open'],
            price18=extends['yExtendDec']['close']
        ))

        fig.segment(x0='x15', y0='price15', x1='x16', y1='price16', source=up_extend_source,
                    color=UP_TREND_COLOR, line_width=2, line_dash='dotted')
        fig.segment(x0='x17', y0='price17', x1='x18', y1='price18', source=down_extend_source,
                    color=DOWN_TREND_COLOR, line_width=2, line_dash='dotted')

    # Add on extra lines (e.g. moving averages) here
    # fig.line(df.index, <your Data>)

    # Add on a vertical line to indicate a trading signal here
    # vline = Span(location=df.index[-<your index>, dimension='height',
    #              line_color="green", line_width=2)
    # fig.renderers.extend([vline])

    # Add date labels to x axis
    fig.xaxis.major_label_overrides = {
        i: date.strftime(xaxis_dt_format) for i, date in enumerate(pd.to_datetime(df["Time"], utc=True))
    }

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

    fig.add_tools(HoverTool(
        renderers=[buy_segment],
        tooltips=[
            ("Type", "@type1"),
            ("Date Open", "@date7{" + xaxis_dt_format + "}"),
            ("Date Close", "@date8{" + xaxis_dt_format + "}"),
            ("Price Open", "@price7{" + number_format1 + "}"),
            ("Price Close", "@price8{" + number_format1 + "}"),
            ("Volume", "@volume1{" + number_format2 + "}"),
            ("TP", "@TP1{" + number_format1 + "}"),
            ("SL", "@SL1{" + number_format1 + "}"),
            ("Result", "@result1"),
            ("Profit", "@profit1{" + number_format2 + "}"),
            ("Profit in pip", "@profit_in_pip1{" + number_format3 + "}")
        ],
        formatters={
            '@date7': 'datetime',
            '@date8': 'datetime',
            '@price7': 'printf',
            '@price8': 'printf',
            '@volume1': 'printf',
            '@TP1': 'printf',
            '@SL1': 'printf',
            '@profit1': 'printf',
            '@profit_in_pip1': 'printf',
        }
    ))

    fig.add_tools(HoverTool(
        renderers=[sell_segment],
        tooltips=[
            ("Type", "@type2"),
            ("Date Open", "@date9{" + xaxis_dt_format + "}"),
            ("Date Close", "@date10{" + xaxis_dt_format + "}"),
            ("Price Open", "@price9{" + number_format1 + "}"),
            ("Price Close", "@price10{" + number_format1 + "}"),
            ("Volume", "@volume2{" + number_format2 + "}"),
            ("TP", "@TP2{" + number_format1 + "}"),
            ("SL", "@SL2{" + number_format1 + "}"),
            ("Result", "@result2"),
            ("Profit", "@profit2{" + number_format2 + "}"),
            ("Profit in pip", "@profit_in_pip2{" + number_format3 + "}")
        ],
        formatters={
            '@date9': 'datetime',
            '@date10': 'datetime',
            '@price9': 'printf',
            '@price10': 'printf',
            '@volume2': 'printf',
            '@TP2': 'printf',
            '@SL2': 'printf',
            '@profit2': 'printf',
            '@profit_in_pip2': 'printf',
        }
    ))

    # top figure //////////////////////////////////////////////////

    top_fig = figure(sizing_mode="stretch_width",
                     plot_height=200,
                     tools="xpan,xwheel_zoom,reset,save",
                     active_drag='xpan',
                     active_scroll='xwheel_zoom',
                     x_axis_type='linear',
                     x_range=fig.x_range,
                     title="balance & equity"
                     )

    balance_color = '#72a1dc'
    equity_color = '#f9584a'
    balance = ColumnDataSource(data=dict(
        index1=df_balance.index,
        date1=df_balance.x,
        value1=df_balance.balance
    ))

    equity = ColumnDataSource(data=dict(
        index2=df_balance.index,
        date2=df_equity.x,
        value2=df_equity.equity
    ))

    equity_line = top_fig.line(x='index2', y='value2', source=equity, line_width=2, line_color=equity_color)
    balance_line = top_fig.line(x='index1', y='value1', source=balance, line_width=2, line_color=balance_color)

    top_fig.add_tools(HoverTool(
        renderers=[balance_line],
        tooltips=[
            ("Balance", "@value1{" + number_format2 + "}"),
            ("Date", "@date1{" + xaxis_dt_format + "}")
        ],
        formatters={
            '@date1': 'datetime',
            '@value1': 'printf'
        }))

    top_fig.add_tools(HoverTool(
        renderers=[equity_line],
        tooltips=[
            ("Equity", "@value2{" + number_format2 + "}"),
            ("Date", "@date2{" + xaxis_dt_format + "}")
        ],
        formatters={
            '@date2': 'datetime',
            '@value2': 'printf',
        }))
    top_fig.xaxis.major_label_overrides = {
        i: date.strftime(xaxis_dt_format) for i, date in enumerate(pd.to_datetime(df_balance["x"], utc=True))
    }

    # JavaScript callback function to automatically zoom the Y axis to
    # view the Data properly
    source = ColumnDataSource({'Index': df.index, 'High': df.High, 'Low': df.Low,
                               'Index_be': df_balance.index, 'Balance': df_balance.balance,
                               'Equity': df_equity.equity
                               })
    callback = CustomJS(args={'y_range_candle': fig.y_range, 'y_range_be': top_fig.y_range,
                              'source': source}, code='''
           clearTimeout(window._autoscale_timeout);
           var Index_candle = source.data.Index,
               Low = source.data.Low,
               High = source.data.High,
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
           var Index_be = source.data.Index_be,
                Balance = source.data.Balance,
                Equity = source.data.Equity,
                min_be = Infinity,
                max_be = -Infinity;
            for (var i=0; i < Index_be.length; ++i) {
                if (start <= Index_be[i] && Index_be[i] <= end) {
                    max_be = Math.max(Balance[i], max_be);
                    max_be = Math.max(Equity[i], max_be);
                    min_be = Math.min(Balance[i], min_be);
                    min_be = Math.min(Equity[i], min_be);
                }
            }
           var pad_candle = (max_candle - min_candle) * .1;
           var pad_be = (max_be - min_be) * .2;
           window._autoscale_timeout = setTimeout(function() {
               y_range_candle.start = min_candle - pad_candle;
               y_range_candle.end = max_candle + pad_candle;
               y_range_be.start = min_be - pad_be;
               y_range_be.end = max_be + pad_be;
           });
       ''')

    # Finalise the figure
    fig.x_range.js_on_change('start', callback)

    curstate().file['title'] = name
    show(column(top_fig, fig, sizing_mode='stretch_both'))


def add_ema(figure, index, price, window_size, color, width):
    ema = trend.ema(price, window_size)
    figure.line(x=index, y=ema, line_color=color, line_width=width)

