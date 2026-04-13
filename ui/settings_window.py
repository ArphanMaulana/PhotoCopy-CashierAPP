from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QHBoxLayout, QGridLayout
)
from PyQt5.QtCore import Qt
from config import PRINTER_VENDOR_ID, PRINTER_PRODUCT_ID, QRIS_BUSINESS_ID
from printer.escpos import Printer
import json
import os

SETTINGS_FILE = "settings.json"

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pengaturan Admin")
        self.setGeometry(200, 200, 500, 400)
        self.printer = Printer()
        self.initUI()
        self.load_settings()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        self.title_label = QLabel("Pengaturan Sistem")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        printer_group_layout = QGridLayout()
        printer_group_label = QLabel("Pengaturan Printer ESC/POS:")
        printer_group_layout.addWidget(printer_group_label, 0, 0, 1, 2)

        self.label_vendor_id = QLabel("Vendor ID (Hex):")
        self.input_vendor_id = QLineEdit()
        self.input_vendor_id.setPlaceholderText("e.g., 0x04b8")
        printer_group_layout.addWidget(self.label_vendor_id, 1, 0)
        printer_group_layout.addWidget(self.input_vendor_id, 1, 1)

        self.label_product_id = QLabel("Product ID (Hex):")
        self.input_product_id = QLineEdit()
        self.input_product_id.setPlaceholderText("e.g., 0x0e15")
        printer_group_layout.addWidget(self.label_product_id, 2, 0)
        printer_group_layout.addWidget(self.input_product_id, 2, 1)

        test_print_layout = QHBoxLayout()
        self.test_printer_button = QPushButton("Test Printer")
        self.test_printer_button.clicked.connect(self.test_printer_connection)
        test_print_layout.addWidget(self.test_printer_button)
        printer_group_layout.addLayout(test_print_layout, 3, 0, 1, 2, Qt.AlignCenter)

        layout.addLayout(printer_group_layout)
        layout.addSpacing(20)

        qris_group_layout = QGridLayout()
        qris_group_label = QLabel("Pengaturan QRIS:")
        qris_group_layout.addWidget(qris_group_label, 0, 0, 1, 2)

        self.label_qris_id = QLabel("QRIS Business ID:")
        self.input_qris_id = QLineEdit()
        self.input_qris_id.setPlaceholderText("Masukkan ID Bisnis QRIS")
        qris_group_layout.addWidget(self.label_qris_id, 1, 0)
        qris_group_layout.addWidget(self.input_qris_id, 1, 1)

        layout.addLayout(qris_group_layout)
        layout.addSpacing(30)

        self.save_button = QPushButton("Simpan Pengaturan")
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button, alignment=Qt.AlignCenter)

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    settings = json.load(f)
                    self.input_vendor_id.setText(settings.get("printer_vendor_id", hex(PRINTER_VENDOR_ID)))
                    self.input_product_id.setText(settings.get("printer_product_id", hex(PRINTER_PRODUCT_ID)))
                    self.input_qris_id.setText(settings.get("qris_business_id", QRIS_BUSINESS_ID))
            except json.JSONDecodeError:
                QMessageBox.warning(self, "Error", "Gagal membaca file pengaturan. Menggunakan nilai default.")
                self._set_default_settings_inputs()
        else:
            self._set_default_settings_inputs()

    def _set_default_settings_inputs(self):
        self.input_vendor_id.setText(hex(PRINTER_VENDOR_ID))
        self.input_product_id.setText(hex(PRINTER_PRODUCT_ID))
        self.input_qris_id.setText(QRIS_BUSINESS_ID)

    def save_settings(self):
        try:
            vendor_id_str = self.input_vendor_id.text()
            product_id_str = self.input_product_id.text()
            qris_id = self.input_qris_id.text()

            vendor_id = int(vendor_id_str, 16) if vendor_id_str.startswith('0x') else int(vendor_id_str)
            product_id = int(product_id_str, 16) if product_id_str.startswith('0x') else int(product_id_str)

            settings = {
                "printer_vendor_id": hex(vendor_id),
                "printer_product_id": hex(product_id),
                "qris_business_id": qris_id
            }

            with open(SETTINGS_FILE, "w") as f:
                json.dump(settings, f, indent=4)

            self.printer.update_printer_ids(vendor_id, product_id)

            QMessageBox.information(self, "Berhasil", "Pengaturan berhasil disimpan.")

        except ValueError:
            QMessageBox.warning(self, "Format Tidak Valid", "Pastikan Vendor ID dan Product ID adalah nilai heksadesimal yang benar (misal: 0x04b8).")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan saat menyimpan pengaturan: {e}")

    def test_printer_connection(self):
        vendor_id_str = self.input_vendor_id.text()
        product_id_str = self.input_product_id.text()
        try:
            vendor_id = int(vendor_id_str, 16) if vendor_id_str.startswith('0x') else int(vendor_id_str)
            product_id = int(product_id_str, 16) if product_id_str.startswith('0x') else int(product_id_str)

            temp_printer = Printer(vendor_id=vendor_id, product_id=product_id)

            if temp_printer.is_connected():
                if temp_printer.print_test_page():
                    QMessageBox.information(self, "Test Printer", "Test page berhasil dicetak!")
                else:
                    QMessageBox.warning(self, "Test Printer", "Printer terdeteksi, namun gagal mencetak test page. Periksa koneksi atau driver.")
            else:
                QMessageBox.warning(self, "Test Printer", "Printer tidak terdeteksi dengan ID yang diberikan. Pastikan printer terhubung dan ID benar.")
        except ValueError:
            QMessageBox.warning(self, "Format Tidak Valid", "Pastikan Vendor ID dan Product ID adalah nilai heksadesimal yang benar (misal: 0x04b8).")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan saat melakukan test printer: {e}")