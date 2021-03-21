
class Config:
    DEBUG = True
    tp = 620    # in point
    sl = 580    # in point
    volume = 1
    time_frame = "H1"
    start_date = "01.01.2016 00:00:00"
    end_date = "02.01.2017 00:00:00"
    date_format = "%d.%m.%Y %H:%M:%S"
    risk = 3   # risk management - percent of account balance
    closing_strategy = "onReverse"  # 'TP_SL', 'onReverse'
    max_trades = 4  # 0 : disable
