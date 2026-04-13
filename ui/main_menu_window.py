from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QGridLayout
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont

from ui.cashier_window import CashierWindow
from ui.input_data_window import InputDataWindow
from ui.report_window import ReportWindow
from ui.settings_window import SettingsWindow

class MainMenuWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("APLIKASI KASIR FOTOCOPY PAGARUYUNG")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()

    def initUI(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setAlignment(Qt.AlignCenter)

        title_font = QFont("Times New Roman")
        title_font.setPointSize(36)
        title_font.setBold(True)

        self.title_label = QLabel("APLIKASI KASIR FOTOCOPY PAGARUYUNG")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(title_font)
        layout.addWidget(self.title_label)
        layout.addSpacing(50)

        buttons_grid = QGridLayout()
        buttons_grid.setAlignment(Qt.AlignCenter)

        button_font = QFont("Times New Roman")
        button_font.setPointSize(24)
        button_font.setBold(True)

        button_style_base = "color: white; font-weight: bold; border-radius: 10px;"
        button_size = QSize(300, 150)

        self.cashier_button = QPushButton("Kasir")
        self.cashier_button.setFixedSize(button_size)
        self.cashier_button.setFont(button_font)
        self.cashier_button.setStyleSheet(f"background-color: #4CAF50; {button_style_base}")
        self.cashier_button.clicked.connect(self.open_cashier_window)
        buttons_grid.addWidget(self.cashier_button, 0, 0)

        self.input_data_button = QPushButton("Input Data")
        self.input_data_button.setFixedSize(button_size)
        self.input_data_button.setFont(button_font)
        self.input_data_button.setStyleSheet(f"background-color: #1976D2; {button_style_base}")
        self.input_data_button.clicked.connect(self.open_input_data_window)
        buttons_grid.addWidget(self.input_data_button, 0, 1)

        self.report_button = QPushButton("Laporan Keuangan")
        self.report_button.setFixedSize(button_size)
        self.report_button.setFont(button_font)
        self.report_button.setStyleSheet(f"background-color: #3F51B5; {button_style_base}")
        self.report_button.clicked.connect(self.open_report_window)
        buttons_grid.addWidget(self.report_button, 1, 0, 1, 2, Qt.AlignCenter)

        layout.addLayout(buttons_grid)

    def open_cashier_window(self):
        self.cashier_window = CashierWindow()
        self.cashier_window.show()

    def open_input_data_window(self):
        self.input_data_window = InputDataWindow()
        self.input_data_window.show()

    def open_report_window(self):
        self.report_window = ReportWindow()
        self.report_window.show()

    def open_settings_window(self):
        self.settings_window = SettingsWindow()
        self.settings_window.show()