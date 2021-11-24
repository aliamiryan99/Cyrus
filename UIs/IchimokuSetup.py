from PyQt5 import QtWidgets, uic
import sys

from Managers.BackTestTradeManager import BackTestLauncher
from Simulation import Simulation
from Managers.LocalToolsManager import ChartLauncher


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('Ichimoku.ui', self)

        self.back_test_btn = self.findChild(QtWidgets.QPushButton, 'back_test_btn')

        self.role_cmb = self.findChild(QtWidgets.QComboBox, 'role_cmb')
        self.tenkan_sen_spin = self.findChild(QtWidgets.QSpinBox, 'tenkan_sen_spin')
        self.kijun_sen_spin = self.findChild(QtWidgets.QSpinBox, 'kijun_sen_spin')
        self.senkou_span_projection_spin = self.findChild(QtWidgets.QSpinBox, 'senkou_span_projection_spin')
        self.range_filter_ckb = self.findChild(QtWidgets.QCheckBox, 'range_filter_ckb')
        self.sequential_trade_ckb = self.findChild(QtWidgets.QCheckBox, 'sequential_trade_ckb')
        self.komu_cloud_filter_ckb = self.findChild(QtWidgets.QCheckBox, 'komu_cloud_filter_ckb')

        self.role_cmb_2 = self.findChild(QtWidgets.QComboBox, 'role_cmb_2')
        self.tenkan_sen_spin_2 = self.findChild(QtWidgets.QSpinBox, 'tenkan_sen_spin_2')
        self.kijun_sen_spin_2 = self.findChild(QtWidgets.QSpinBox, 'kijun_sen_spin_2')
        self.senkou_span_projection_spin_2 = self.findChild(QtWidgets.QSpinBox, 'senkou_span_projection_spin_2')
        self.range_filter_ckb_2 = self.findChild(QtWidgets.QCheckBox, 'range_filter_ckb_2')
        self.sequential_trade_ckb_2 = self.findChild(QtWidgets.QCheckBox, 'sequential_trade_ckb_2')
        self.komu_cloud_filter_ckb_2 = self.findChild(QtWidgets.QCheckBox, 'komu_cloud_filter_ckb_2')

        self.symbol_cmb = self.findChild(QtWidgets.QComboBox, 'symbol_cmb')
        self.time_frame_cmb = self.findChild(QtWidgets.QComboBox, 'time_frame_cmb')
        self.account_management_cmb = self.findChild(QtWidgets.QComboBox, 'account_management_cmb')
        self.management_ratio_spin = self.findChild(QtWidgets.QSpinBox, 'management_ratio_spin')

        self.message_lbl = self.findChild(QtWidgets.QLabel, 'message_lbl')

        self.back_test_btn.clicked.connect(self.back_test)

        self.show()

    def back_test(self):
        self.message_lbl.setText("Back test is running ...")
        self.back_test_btn.setEnabled(False)
        # Back Test
        params = {'Role': int(self.role_cmb.currentText()),
                  'Tenkan': self.tenkan_sen_spin.value(),
                  'Kijun': self.kijun_sen_spin.value(), 'SenkouSpanProjection': self.senkou_span_projection_spin.value(),
                  'RangeFilterEnable': self.range_filter_ckb.isChecked(),
                  'SequentialTrade': self.sequential_trade_ckb.isChecked(),
                  'KomuCloudFilter': self.komu_cloud_filter_ckb.isChecked(),
                  'Role2': int(self.role_cmb_2.currentText()),
                  'Tenkan2': self.tenkan_sen_spin_2.value(),
                  'Kijun2': self.kijun_sen_spin_2.value(), 'SenkouSpanProjection2': self.senkou_span_projection_spin_2.value(),
                  'RangeFilterEnable2': self.range_filter_ckb_2.isChecked(),
                  'SequentialTrade2': self.sequential_trade_ckb_2.isChecked(),
                  'KomuCloudFilter2': self.komu_cloud_filter_ckb_2.isChecked(),
                  'AccountManagement': self.account_management_cmb.currentText(),
                  'ManagementRatio': self.management_ratio_spin.value(),
                  'Symbol': self.symbol_cmb.currentText(), 'TimeFrame': self.time_frame_cmb.currentText()}

        launcher = BackTestLauncher(params)
        market = launcher.run()
        Simulation.get_output(market)
        # Reason
        launcher = ChartLauncher(params)
        launcher.launch()

        self.back_test_btn.setEnabled(True)
        self.message_lbl.setText("")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()
