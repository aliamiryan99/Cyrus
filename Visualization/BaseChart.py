
from ta import trend
from pandas.plotting import register_matplotlib_converters
import pandas as pd
from bokeh.io import show
from bokeh.layouts import column
from bokeh.plotting import figure
from bokeh.io.state import curstate
from bokeh.models import CustomJS, ColumnDataSource, HoverTool, NumeralTickFormatter, Arrow, VeeHead, Range1d
from Configuration.Trade.BackTestConfig import Config
register_matplotlib_converters()


def get_base_fig(df, name):
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

    # # Color scheme for increasing and descending candles
    # increasing_color = '#17BECF'
    # decreasing_color = '#7F7F7F'
    increasing_color = '#FFFFFF'
    decreasing_color = '#000000'
    shadow_color = '#000000'
    # # sizing settings
    candle_width = 0.5

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

    # # Plot candles

    # High and low
    fig.segment(x0='x1', y0='high1', x1='x1', y1='low1', source=inc_source, color=shadow_color)
    fig.segment(x0='x2', y0='high2', x1='x2', y1='low2', source=dec_source, color=shadow_color)

    # Open and close
    r1 = fig.vbar(x='x1', width=candle_width, top='top1', bottom='bottom1', source=inc_source,
                  fill_color=increasing_color, line_color="black")
    r2 = fig.vbar(x='x2', width=candle_width, top='top2', bottom='bottom2', source=dec_source,
                  fill_color=decreasing_color, line_color="black")

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

    # Add date labels to x axis
    fig.xaxis.major_label_overrides = {
        i: date.strftime(xaxis_dt_format) for i, date in enumerate(pd.to_datetime(df["Time"], utc=True))
    }

    # JavaScript callback function to automatically zoom the Y axis to
    # view the Data properly
    source = ColumnDataSource({'Index': df.index, 'High': df.High, 'Low': df.Low})
    callback = CustomJS(args={'y_range_candle': fig.y_range, 'source': source}, code='''
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
                   var pad_candle = (max_candle - min_candle) * .1;
                   window._autoscale_timeout = setTimeout(function() {
                       y_range_candle.start = min_candle - pad_candle;
                       y_range_candle.end = max_candle + pad_candle;
                   });
               ''')

    # Finalise the figure
    fig.x_range.js_on_change('start', callback)
    curstate().file['title'] = name

    return fig


def get_secondary_fig(title, fig, height, df, indicators, min_indicator, max_indicator):
    secondary_fig = figure(sizing_mode="stretch_width",
                           plot_height=height,
                           tools="xpan,xwheel_zoom,reset,save",
                           active_drag='xpan',
                           active_scroll='xwheel_zoom',
                           x_axis_type='linear',
                           x_range=fig.x_range,
                           title=title)

    if indicators is not None and len(indicators) != 0:
        indicators_list = []
        number_format = '%0.3f'
        for indicator in indicators:
            df_indicator = indicator['df']
            indicators_list.append(df_indicator.to_dict('Records'))
            source = ColumnDataSource(data=dict(
                index1=df_indicator.index,
                value1=df_indicator.value
            ))
            indicator_line = secondary_fig.line(x='index1', y='value1', source=source, line_width=indicator['width'],
                                                line_color=indicator['color'])

            secondary_fig.add_tools(HoverTool(
                renderers=[indicator_line],
                tooltips=[
                    ("Value", "@value1{" + number_format + "}")
                ],
                formatters={
                    '@value1': 'printf'
                }))

        # JavaScript callback function to automatically zoom the Y axis to
        # view the Data properly
        source = ColumnDataSource({'Index': df.index, 'High': df.High, 'Low': df.Low,
                                   'Index_Indicator': max_indicator.index, 'Max_Value_Indicator': max_indicator.value,
                                   'Min_Value_Indicator': min_indicator.value})
        callback = CustomJS(args={'y_range_candle': fig.y_range, 'y_range_indicator': secondary_fig.y_range,
                                  'source': source}, code='''
                           clearTimeout(window._autoscale_timeout);
                           var indexCandle = source.data.Index,
                               low = source.data.Low,
                               high = source.data.High,
                               start = cb_obj.start,
                               end = cb_obj.end,
                               minCandle = Infinity,
                               maxCandle = -Infinity;
                           for (var i=0; i < indexCandle.length; ++i) {
                               if (start <= indexCandle[i] && indexCandle[i] <= end) {
                                   maxCandle = Math.max(high[i], maxCandle);
                                   minCandle = Math.min(low[i], minCandle);
                               }
                           }
                           var indexInd = source.data.Index_Indicator,
                                maxValue = source.data.Max_Value_Indicator,
                                minValue = source.data.Min_Value_Indicator,
                                minInd = Infinity,
                                maxInd = -Infinity;
                            for (var i=0; i < indexInd.length; ++i) {
                                if (start <= indexInd[i] && indexInd[i] <= end) {
                                    maxInd = Math.max(maxValue[i], maxInd);
                                    minInd = Math.min(minValue[i], minInd);
                                }
                            }
                           var padCandle = (maxCandle - minCandle) * .1;
                           var padInd = (maxInd - minInd) * .2;
                           window._autoscale_timeout = setTimeout(function() {
                               y_range_candle.start = minCandle - padCandle;
                               y_range_candle.end = maxCandle + padCandle;
                               y_range_be.start = minInd - padInd;
                               y_range_be.end = maxInd + padInd;
                           });
                       ''')

        # Finalise the figure
        fig.x_range.js_on_change('start', callback)

        return secondary_fig


def get_back_test_fig(df, position_df, name, start):
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

    # JavaScript callback function to automatically zoom the Y axis to
    # view the Data properly
    source = ColumnDataSource({'Index': df.index, 'High': df.High, 'Low': df.Low})
    callback = CustomJS(args={'y_range_candle': fig.y_range, 'source': source}, code='''
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
           var pad_candle = (max_candle - min_candle) * .1;
           window._autoscale_timeout = setTimeout(function() {
               y_range_candle.start = min_candle - pad_candle;
               y_range_candle.end = max_candle + pad_candle;
           });
       ''')

    # Finalise the figure
    fig.x_range.js_on_change('start', callback)

    curstate().file.title = name
    return fig


def candlestick_plot(df, name, indicator_enable = False, df_indicator=None, df_indicator2=None, divergence_line=None,
                     indicator_divergene_line=None, divergence_line_2=None,
                     indicator_divergene_line_2=None, indicatorLocalMax=None, indicatorLocalMin=None, indicatorLocalMax2=None,
                     indicatorLocalMin2=None, lines=None, extend_lines=None, localMax=None, localMin=None, localMax2=None,
                     localMin2=None, marker=None, buyMarker=None, sellMarker=None, resistance_lines=None, support_lines=None):
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

    # Colour scheme for increasing and descending candles
    INCREASING_COLOR = '#FFFFFF'
    DECREASING_COLOR = '#000000'
    SHADOW_COLOR = '#000000'


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

    candle_width = 0.5

    fig.segment(x0='x1', y0='high1', x1='x1', y1='low1', source=inc_source, color=SHADOW_COLOR)
    fig.segment(x0='x2', y0='high2', x1='x2', y1='low2', source=dec_source, color=SHADOW_COLOR)

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
        fig.circle(localMax, df.High[localMax], size=8, color="red")
    if localMin is not None:
        fig.circle(localMin, df.Low[localMin], size=8, color="blue")

    if localMax2 is not None:
        fig.circle(localMax2, df.High[localMax2], size=4, color="red")
    if localMin2 is not None:
        fig.circle(localMin2, df.Low[localMin2], size=4, color="blue")

    if divergence_line is not None:
        for line in divergence_line:
            fig.line(x=line['x'], y=line['y'], line_color='blue', line_width=1)

    if divergence_line_2 is not None:
        for line in divergence_line_2:
            fig.line(x=line['x'], y=line['y'], line_color='red', line_width=1)

    if resistance_lines is not None:
        for line in resistance_lines:
            fig.line(x=[1, line['x'][1]], y=[line['y'][1], line['y'][1]], line_color='red', line_width=2, line_dash='dotted')
            fig.line(x=line['x'], y=line['y'], line_color='red', line_width=2)
            fig.line(x=[line['x'][0], len(df)-2], y=[line['y'][0], line['y'][0]], line_color='red', line_width=2, line_dash='dotted')

    if support_lines is not None:
        for line in support_lines:
            fig.line(x=[1, line['x'][1]], y=[line['y'][1], line['y'][1]], line_color='blue', line_width=2, line_dash='dotted')
            fig.line(x=line['x'], y=line['y'], line_color='blue', line_width=2)
            fig.line(x=[line['x'][0], len(df) - 2], y=[line['y'][0], line['y'][0]], line_color='blue', line_width=2, line_dash='dotted')

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
        i: date.strftime(xaxis_dt_format) for i, date in enumerate(pd.to_datetime(df["Time"], utc=True))
    }

    if indicator_enable:
        top_fig = figure(sizing_mode="stretch_width",
                         plot_height=200,
                         tools="xpan,xwheel_zoom,reset,save",
                         active_drag='xpan',
                         active_scroll='xwheel_zoom',
                         x_axis_type='linear',
                         x_range=fig.x_range,
                         title="Indicator"
                         )

        indicator_color = '#72a1dc'
        indicator_color2 = '#d2a17c'

        indicator = ColumnDataSource(data=dict(
            index1=df_indicator.index,
            value1=df_indicator.value
        ))
        indicator2 = ColumnDataSource(data=dict(
            index2=df_indicator2.index,
            value2=df_indicator2.value
        ))

        top_fig.line(x='index1', y='value1', source=indicator, line_width=2, line_color=indicator_color)
        top_fig.line(x='index2', y='value2', source=indicator2, line_width=2, line_color=indicator_color2)

        if indicatorLocalMax is not None:
            top_fig.circle(indicatorLocalMax, df_indicator.value[indicatorLocalMax], size=6, color="red")
        if indicatorLocalMin is not None:
            top_fig.circle(indicatorLocalMin, df_indicator2.value[indicatorLocalMin], size=6, color="blue")

        if indicatorLocalMax2 is not None:
            top_fig.circle(indicatorLocalMax2, df_indicator.value[indicatorLocalMax2], size=3, color="red")
        if indicatorLocalMin2 is not None:
            top_fig.circle(indicatorLocalMin2, df_indicator2.value[indicatorLocalMin2], size=3, color="blue")

        if indicator_divergene_line != None:
            for line in indicator_divergene_line:
                top_fig.line(x=line['x'], y=line['y'], line_color='blue', line_width=1)

        if indicator_divergene_line_2 != None:
            for line in indicator_divergene_line_2:
                top_fig.line(x=line['x'], y=line['y'], line_color='red', line_width=1)

        # JavaScript callback function to automatically zoom the Y axis to
        # view the Data properly
        source = ColumnDataSource({'Index': df.index, 'High': df.High, 'Low': df.Low,
                                   'Index_Indicator': df_indicator.index, 'Value_Indicator': df_indicator.value})
        callback = CustomJS(args={'y_range_candle': fig.y_range, 'y_range_indicator': top_fig.y_range,
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
                   var Index_ind = source.data.Index_Indicator,
                        Value = source.data.Value_Indicator,
                        min_ind = Infinity,
                        max_ind = -Infinity;
                    for (var i=0; i < Index_ind.length; ++i) {
                        if (start <= Index_ind[i] && Index_ind[i] <= end) {
                            max_ind = Math.max(Value[i], max_ind);
                            min_ind = Math.min(Value[i], min_ind);
                        }
                    }
                   var pad_candle = (max_candle - min_candle) * .1;
                   var pad_ind = (max_ind - min_ind) * .2;
                   window._autoscale_timeout = setTimeout(function() {
                       y_range_candle.start = min_candle - pad_candle;
                       y_range_candle.end = max_candle + pad_candle;
                       y_range_be.start = min_ind - pad_ind;
                       y_range_be.end = max_ind + pad_ind;
                   });
               ''')

        # Finalise the figure
        fig.x_range.js_on_change('start', callback)

        show(column(top_fig, fig, sizing_mode='stretch_both'))

    else:

        # JavaScript callback function to automatically zoom the Y axis to
        # view the Data properly
        source = ColumnDataSource({'Index': df.index, 'High': df.High, 'Low': df.Low})
        callback = CustomJS(args={'y_range_candle': fig.y_range, 'source': source}, code='''
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
