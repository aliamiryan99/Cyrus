
from PyQt5 import QtWidgets, uic
import sys

from Managers.MetaTraderRealTimeToolManager import MetaTraderRealTimeToolsManager
from Configuration.Tools.MetaTraderRealTimeToolsConfig import ChartConfig


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('UIs/Channels.ui', self)

        ChartConfig.tool_name = "Channel"

        self.running = False
        self.start_stop_btn = self.findChild(QtWidgets.QPushButton, 'start_stop_btn')
        self.clear_btn = self.findChild(QtWidgets.QPushButton, 'clear_btn')

        self.type_cmb = self.findChild(QtWidgets.QComboBox, 'type_cmb')
        self.window_spin = self.findChild(QtWidgets.QSpinBox, 'window_spin')
        self.ext_start_spin = self.findChild(QtWidgets.QSpinBox, 'ext_start_spin')
        self.ext_step_spin = self.findChild(QtWidgets.QSpinBox, 'ext_step_spin')
        self.ext_end_spin = self.findChild(QtWidgets.QSpinBox, 'ext_end_spin')
        self.ext_mode_cmb = self.findChild(QtWidgets.QComboBox, 'ext_mode_cmb')
        self.check_window_spin = self.findChild(QtWidgets.QSpinBox, 'check_window_spin')
        self.alpha_dspin = self.findChild(QtWidgets.QDoubleSpinBox, 'alpha_dspin')
        self.extend_multiplier_dspin = self.findChild(QtWidgets.QDoubleSpinBox, 'extend_multiplier_dspin')

        self.message_lbl = self.findChild(QtWidgets.QLabel, 'message_lbl')

        self.start_stop_btn.clicked.connect(self.start_stop)
        self.clear_btn.clicked.connect(self.clear)

        self.launcher = MetaTraderRealTimeToolsManager()

        self.show()

    def start_stop(self):
        if not self.running:
            params = {'Type': self.type_cmb.currentText(),
                      'Window': self.window_spin.value(),
                      'ExtWindowStart': self.ext_start_spin.value(),
                      'ExtWindowStep': self.ext_step_spin.value(),
                      'ExtWindowEnd': self.ext_end_spin.value(), 'ExtMode': self.type_cmb.currentIndex() + 1,
                      'CheckWindow': self.check_window_spin.value(),
                      'Alpha': self.alpha_dspin.value(),
                      'ExtendMultiplier': self.extend_multiplier_dspin.value()}
            self.launcher.run(params)
            if not self.launcher.meta_trader_connection:
                self.message_lbl.setText("Meta Trader Connection Problem")
            else:
                self.running = True
                self.message_lbl.setText("")
                self.start_stop_btn.setText("Stop")
        else:
            self.launcher.stop()
            self.running = False
            self.start_stop_btn.setText("Start")

    def clear(self):
        self.launcher.clear()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()
