from PyQt5 import QtWidgets, uic
import sys

from Managers.MetaTraderHistoricalToolsManager import MetaTraderChartToolsManager
from Configuration.Tools.MetaTraderHistoricalToolsConfig import ChartConfig

from Market.BackTestManager import BackTestManager
from Simulation import Simulation
from Managers.LocalToolsManager import ChartLauncher


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('UIs/setup2.ui', self)

        ChartConfig.tool_name = "RangeRegion"

        self.plot_btn = self.findChild(QtWidgets.QPushButton, 'plot_btn')
        self.clear_btn = self.findChild(QtWidgets.QPushButton, 'clear_btn')
        self.back_test_btn = self.findChild(QtWidgets.QPushButton, 'back_test_btn')

        self.candles_tr_spin = self.findChild(QtWidgets.QSpinBox, 'candles_threshold_spin')
        self.higher_time_frame_cmb = self.findChild(QtWidgets.QComboBox, 'higher_time_frame_cmb')
        self.tp_sl_margin_spin = self.findChild(QtWidgets.QSpinBox, 'tp_sl_margin_spin')
        self.candles_breakout_threshold_spin = self.findChild(QtWidgets.QSpinBox, 'candles_breakout_threshold_spin')
        self.max_candles_spin = self.findChild(QtWidgets.QSpinBox, 'max_candles_spin')
        self.type1_enable_ckb = self.findChild(QtWidgets.QCheckBox, 'type1_enable_ckb')
        self.type2_enable_ckb = self.findChild(QtWidgets.QCheckBox, 'type2_enable_ckb')
        self.one_stop_loss_allowed_ckb = self.findChild(QtWidgets.QCheckBox, 'one_stop_loss_allowed_ckb')
        self.ma_filter_ckb = self.findChild(QtWidgets.QCheckBox, 'ma_filter_ckb')
        self.ma_type_cmb = self.findChild(QtWidgets.QComboBox, 'ma_type_cmb')
        self.ma_period_spin = self.findChild(QtWidgets.QSpinBox, 'ma_period_spin')


        self.symbol_cmb = self.findChild(QtWidgets.QComboBox, 'symbol_cmb')
        self.time_frame_cmb = self.findChild(QtWidgets.QComboBox, 'time_frame_cmb')
        self.account_management_cmb = self.findChild(QtWidgets.QComboBox, 'account_management_cmb')
        self.management_ratio_spin = self.findChild(QtWidgets.QSpinBox, 'management_ratio_spin')
        self.risk_free_enable_ckb = self.findChild(QtWidgets.QCheckBox, 'risk_free_enable_ckb')
        self.risk_free_price_percent_spin = self.findChild(QtWidgets.QSpinBox, 'risk_free_price_percent_spin')
        self.risk_free_volume_percent_spin = self.findChild(QtWidgets.QSpinBox, 'risk_free_volume_percent_spin')

        self.fib_enable_ckb = self.findChild(QtWidgets.QCheckBox, 'fib_enable_ckb')

        self.message_lbl = self.findChild(QtWidgets.QLabel, 'message_lbl')

        self.plot_btn.clicked.connect(self.plot)
        self.clear_btn.clicked.connect(self.clear)
        self.back_test_btn.clicked.connect(self.back_test)

        self.show()

    def plot(self):
        params = {'RangeCandleThreshold': self.candles_tr_spin.value(),
                  'UpTimeFrame': self.higher_time_frame_cmb.currentText(),
                  'CandlesBreakoutThreshold': self.candles_breakout_threshold_spin.value(),
                  'MaxCandles': self.max_candles_spin.value(),
                  'StopTargetMargin': self.tp_sl_margin_spin.value(), 'Type1Enable': self.type1_enable_ckb.isChecked(),
                  'Type2Enable': self.type2_enable_ckb.isChecked(),
                  'OneStopInRegion': self.one_stop_loss_allowed_ckb.isChecked(),
                  'FibEnable': self.fib_enable_ckb.isChecked()}
        launcher = MetaTraderChartToolsManager(params=params)
        if not launcher.meta_trader_connection:
            self.message_lbl.setText("Meta Trader Connection Problem")
        else:
            self.message_lbl.setText("")

    def clear(self):
        from MetaTrader.MetaTraderBase import MetaTraderBase
        meta_trader = MetaTraderBase()
        meta_trader.clear()
        meta_trader.connector.shutdown()

    def back_test(self):
        self.message_lbl.setText("Back test is running ...")
        self.clear_btn.setEnabled(False)
        self.plot_btn.setEnabled(False)
        self.back_test_btn.setEnabled(False)
        # Back Test
        params = {'RangeCandleThreshold': self.candles_tr_spin.value(),
                  'UpTimeFrame': self.higher_time_frame_cmb.currentText(),
                  'CandlesBreakoutThreshold': self.candles_breakout_threshold_spin.value(),
                  'MaxCandles': self.max_candles_spin.value(),
                  'StopTargetMargin': self.tp_sl_margin_spin.value(), 'Type1Enable': self.type1_enable_ckb.isChecked(),
                  'Type2Enable': self.type2_enable_ckb.isChecked(),
                  'OneStopInRegion': self.one_stop_loss_allowed_ckb.isChecked(),
                  'MaFilterEnable': self.ma_filter_ckb.isChecked(),
                  'MaType': self.ma_type_cmb.currentText(),
                  'MaPeriod': self.ma_period_spin.value(),
                  'AccountManagement': self.account_management_cmb.currentText(),
                  'ManagementRatio': self.management_ratio_spin.value(),
                  'RiskFreeEnable': self.risk_free_enable_ckb.isChecked(),
                  'RiskFreePricePercent': self.risk_free_price_percent_spin.value(),
                  'RiskFreeVolumePercent': self.risk_free_volume_percent_spin.value(),
                  'Symbol': self.symbol_cmb.currentText(), 'TimeFrame': self.time_frame_cmb.currentText()}
        launcher = BackTestManager(params)
        market_executed = launcher.run()
        Simulation.get_output(market_executed, backtest_with_market=True)
        # Reason
        launcher = ChartLauncher(params, with_market=True)
        launcher.launch()

        self.clear_btn.setEnabled(True)
        self.plot_btn.setEnabled(True)
        self.back_test_btn.setEnabled(True)
        self.message_lbl.setText("")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()
