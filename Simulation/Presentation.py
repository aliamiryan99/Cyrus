from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel,
                             QPushButton, QStyleFactory, QVBoxLayout)
from Simulation import Outputs


class Presentation(QDialog):
    def __init__(self, parent=None):
        super(Presentation, self).__init__(parent)

        self.originalPalette = QApplication.palette()

        styleComboBox = QComboBox()
        styleComboBox.addItems(QStyleFactory.keys())

        styleLabel = QLabel("&Style:")
        styleLabel.setBuddy(styleComboBox)

        self.useStylePaletteCheckBox = QCheckBox("&Use style's standard palette")
        self.useStylePaletteCheckBox.setChecked(True)

        disableWidgetsCheckBox = QCheckBox("&Disable widgets")

        self.createTopLeftGroupBox()
        self.createTopRightGroupBox()
        self.createBottomLeftTabWidget()
        self.createBottomRightGroupBox()
        self.createBottomLayout()

        topLayout = QHBoxLayout()
        topLayout.addWidget(styleLabel)
        topLayout.addWidget(styleComboBox)
        topLayout.addStretch(1)
        topLayout.addWidget(self.useStylePaletteCheckBox)
        topLayout.addWidget(disableWidgetsCheckBox)

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.topLeftGroupBox, 1, 0)
        mainLayout.addWidget(self.topRightGroupBox, 1, 1)
        mainLayout.addWidget(self.bottomLeftGroupBox, 2, 0)
        mainLayout.addWidget(self.bottomRightGroupBox, 2, 1)
        mainLayout.addLayout(self.bottomLayout, 3, 0, 1, 2)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle("Simulator")
        self.changeStyle('Fusion')

    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))
        self.changePalette()

    def changePalette(self):
        if (self.useStylePaletteCheckBox.isChecked()):
            QApplication.setPalette(QApplication.style().standardPalette())
        else:
            QApplication.setPalette(self.originalPalette)

    def createTopLeftGroupBox(self):
        self.topLeftGroupBox = QGroupBox()

        label = QLabel(f"Time range:  {Outputs.start_date} - {Outputs.end_date}")
        label1 = QLabel(f"Total Net Profit:  {int(Outputs.total_profit)}$")
        label2 = QLabel(f"Average AUM:  {Outputs.average_aum}")
        label3 = QLabel(f"Capacity:  {Outputs.capacity}")
        label4 = QLabel(f"Leverage:  {Outputs.simulate.leverage}")
        label5 = QLabel(f"Maximum dollar position size:  {Outputs.max_pos_size}")

        layout = QVBoxLayout()
        layout.addWidget(label1)
        layout.addWidget(label2)
        layout.addWidget(label3)
        layout.addWidget(label4)
        layout.addWidget(label5)
        layout.addStretch(1)
        self.topLeftGroupBox.setLayout(layout)

    def createTopRightGroupBox(self):
        self.topRightGroupBox = QGroupBox()

        # defaultPushButton = QPushButton("Default Push Button")
        # defaultPushButton.setDefault(True)
        label1 = QLabel(f"Frequency of bets:  {Outputs.frequency_of_bets}")
        label2 = QLabel(f"Sharpe ratio:  {Outputs.sharpe_ratio}")
        label3 = QLabel(f"Average holding period: {Outputs.average_holding_period}")
        label4 = QLabel(f"Annualized turnover: {Outputs.annualized_turnover}")
        label5 = QLabel(f"Total trades: {len(Outputs.o_positions)}")

        layout = QVBoxLayout()
        layout.addWidget(label1)
        layout.addWidget(label2)
        layout.addWidget(label3)
        layout.addWidget(label4)
        layout.addWidget(label5)
        layout.addStretch(1)
        self.topRightGroupBox.setLayout(layout)

    def createBottomLeftTabWidget(self):
        self.bottomLeftGroupBox = QGroupBox()

        label1 = QLabel(f"Long trades(won %):  {Outputs.long_trades}({int(round(Outputs.won_long_trade / Outputs.long_trades, 2) * 100)}%)")
        label2 = QLabel(f"Short trades(won %):  {Outputs.short_trades}({Outputs.short_trades}({int(round(Outputs.won_short_trade / Outputs.short_trades, 2) * 100)}%)")
        label3 = QLabel(f"Profit trades:  {Outputs.won_short_trade + Outputs.won_long_trade}")
        label4 = QLabel(f"Loss trades:  {len(Outputs.o_positions) - Outputs.won_long_trade - Outputs.won_short_trade}")
        label9 = QLabel(f"Accuracy:  {round((Outputs.won_short_trade + Outputs.won_long_trade) * 100 / len(Outputs.o_positions), 2)}%")
        label5 = QLabel(f"Largest profit trade:  {Outputs.largest_profit_trade}")
        label6 = QLabel(f"Largest loss trade:  {Outputs.largest_loss_trade}")
        label7 = QLabel(f"Average profit trade:  {Outputs.average_profit_trade}")
        label8 = QLabel(f"Average loss trade:  {Outputs.average_loss_trade}")

        layout = QVBoxLayout()
        layout.addWidget(label1)
        layout.addWidget(label2)
        layout.addWidget(label3)
        layout.addWidget(label4)
        layout.addWidget(label9)
        layout.addWidget(label5)
        layout.addWidget(label6)
        layout.addWidget(label7)
        layout.addWidget(label8)
        layout.addStretch(1)
        self.bottomLeftGroupBox.setLayout(layout)

    def createBottomRightGroupBox(self):
        self.bottomRightGroupBox = QGroupBox()

        # defaultPushButton = QPushButton("Default Push Button")
        # defaultPushButton.setDefault(True)
        label1 = QLabel(f"Maximum consecutive win($):  {Outputs.maximum_consecutive_wins}({Outputs.maximum_consecutive_wins_amount})")
        label2 = QLabel(f"Maximum consecutive loss($):  {Outputs.maximum_consecutive_losses}({Outputs.maximum_consecutive_losses_amount})")
        label3 = QLabel(f"Maximal consecutive win(count): {Outputs.maximal_consecutive_wins}({Outputs.maximal_consecutive_wins_count})")
        label4 = QLabel(f"Maximal consecutive loss(count):  {Outputs.maximal_consecutive_losses}({Outputs.maximal_consecutive_losses_count})")
        label5 = QLabel(f"Average consecutive win:  {Outputs.average_consecutive_wins}")
        label6 = QLabel(f"Average consecutive loss:  {Outputs.average_consecutive_losses}")

        layout = QVBoxLayout()
        layout.addWidget(label1)
        layout.addWidget(label2)
        layout.addWidget(label3)
        layout.addWidget(label4)
        layout.addWidget(label5)
        layout.addWidget(label6)
        layout.addStretch(1)
        self.bottomRightGroupBox.setLayout(layout)

    def createBottomLayout(self):
        self.bottomLayout = QHBoxLayout()
        balanceBtn = QPushButton("Balance")
        balanceBtn.setDefault(True)
        equityBtn = QPushButton("Equity")
        equityBtn.setDefault(True)
        marginBtn = QPushButton("Margin")
        marginBtn.setDefault(True)
        freeMarginBtn = QPushButton("Free Margin")
        freeMarginBtn.setDefault(True)
        profitBtn = QPushButton("profit")
        profitBtn.setDefault(True)

        balanceBtn.clicked.connect(self.balanceChart)
        equityBtn.clicked.connect(self.equityChart)
        marginBtn.clicked.connect(self.marginChart)
        freeMarginBtn.clicked.connect(self.freeMarginChart)
        profitBtn.clicked.connect(self.profitChart)

        self.bottomLayout.addWidget(balanceBtn)
        self.bottomLayout.addWidget(equityBtn)
        self.bottomLayout.addWidget(marginBtn)
        self.bottomLayout.addWidget(freeMarginBtn)
        self.bottomLayout.addWidget(profitBtn)

    def balanceChart(self):
        Outputs.draw_chart(Outputs.df_balance_history, "Balance")

    def equityChart(self):
        Outputs.draw_chart(Outputs.df_equity_history, "Equity")

    def marginChart(self):
        Outputs.draw_chart(Outputs.df_margin_history, "Margin")

    def freeMarginChart(self):
        Outputs.draw_chart(Outputs.df_free_margin_history, "Free Margin")

    def profitChart(self):
        Outputs.draw_chart(Outputs.df_profit_history, "Profit")




if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    presentation = Presentation()
    sys.exit(app.exec_())
