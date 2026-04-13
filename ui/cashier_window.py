from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QLineEdit, QHBoxLayout, QPushButton,
    QComboBox, QMessageBox, QSpinBox, QHeaderView, QApplication,
    QGridLayout, QAbstractItemView, QCheckBox,
    QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize
from printer.escpos import Printer
from config import DISKON_PERSEN, BATAS_DISKON, PRINTER_VENDOR_ID, PRINTER_PRODUCT_ID, DB_NAME
from config import DB_NAME, get_app_dir
import sqlite3
import os



class CashierWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplikasi Kasir")
        self.setGeometry(150, 150, 1000, 700)
        self.total_harga = 0  
        self.current_subtotal = 0  
        self.diskon_persen_config = DISKON_PERSEN  
        self.batas_diskon_config = BATAS_DISKON  

        self.printer = Printer(vendor_id=PRINTER_VENDOR_ID, product_id=PRINTER_PRODUCT_ID)
        self.db_path_full = os.path.join("database", DB_NAME)

        self.selected_items_for_purchase = {}  

        self.initUI()

        self.calculate_totals()
        self.on_payment_method_changed(self.metode_pembayaran_bottom.currentText())

    def initialize_item_db(self):
        pass  

    def initUI(self):
        main_layout = QVBoxLayout(self)

        self.title_label = QLabel("Sistem Kasir Fotokopi")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(self.title_label)

        self.table = QTableWidget()

        self.table.setColumnCount(4)  
        self.table.setHorizontalHeaderLabels(["Nama Barang", "Jumlah", "Harga Satuan", "Subtotal"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)  
        self.table.setColumnWidth(1, 80)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  

        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.table)

        self.pilih_barang_button = QPushButton("Pilih Barang")
        self.pilih_barang_button.clicked.connect(self.open_select_product_window)
        self.pilih_barang_button.setFixedSize(QSize(200, 50)) 
        main_layout.addWidget(self.pilih_barang_button, alignment=Qt.AlignCenter)

        bottom_main_layout = QHBoxLayout()  

        left_controls_vertical_layout = QVBoxLayout()

        diskon_h_layout = QHBoxLayout()
        self.diskon_checkbox = QCheckBox("Diskon (%)")
        self.diskon_checkbox.stateChanged.connect(self.toggle_diskon_input)
        diskon_h_layout.addWidget(self.diskon_checkbox)  

        self.diskon_input = QLineEdit("0")
        self.diskon_input.setFixedWidth(80)
        self.diskon_input.setAlignment(Qt.AlignRight)
        self.diskon_input.setEnabled(False)  
        self.diskon_input.textChanged.connect(self.calculate_totals)
        diskon_h_layout.addWidget(self.diskon_input)  
        diskon_h_layout.addStretch(1) 
        left_controls_vertical_layout.addLayout(diskon_h_layout)

        metode_h_layout = QHBoxLayout()
        metode_h_layout.addWidget(QLabel("Metode Pembayaran:"))
        self.metode_pembayaran_bottom = QComboBox()
        self.metode_pembayaran_bottom.addItems(["Cash", "QRIS", "Debit", "E-Wallet"])
        self.metode_pembayaran_bottom.currentTextChanged.connect(self.on_payment_method_changed)
        metode_h_layout.addWidget(self.metode_pembayaran_bottom)
        metode_h_layout.addStretch(1)  
        left_controls_vertical_layout.addLayout(metode_h_layout)

        left_controls_vertical_layout.addStretch(1)  

        bottom_main_layout.addLayout(left_controls_vertical_layout)
        bottom_main_layout.addStretch(1)

        right_column_vertical_layout = QVBoxLayout() 
        totals_payment_grid = QGridLayout() 

        totals_payment_grid.addWidget(QLabel("Grand Total:"), 0, 0, alignment=Qt.AlignRight)
        self.grand_total_label = QLabel("Rp 0")
        self.grand_total_label.setAlignment(Qt.AlignRight)  
        self.grand_total_label.setStyleSheet("font-weight: bold; color: blue; font-size: 24px;")
        totals_payment_grid.addWidget(self.grand_total_label, 0, 1, alignment=Qt.AlignRight)

        totals_payment_grid.addWidget(QLabel("SubTotal:"), 1, 0, alignment=Qt.AlignRight)
        self.subtotal_label = QLabel("Rp 0")
        self.subtotal_label.setAlignment(Qt.AlignRight) 
        self.subtotal_label.setStyleSheet("font-weight: bold;")
        totals_payment_grid.addWidget(self.subtotal_label, 1, 1, alignment=Qt.AlignRight)

        totals_payment_grid.addWidget(QLabel("Tunai (Rp):"), 2, 0, alignment=Qt.AlignRight)
        self.tunai_input = QLineEdit("0")
        self.tunai_input.setFixedWidth(120)
        self.tunai_input.setAlignment(Qt.AlignRight)
        self.tunai_input.textChanged.connect(self.calculate_change)
        totals_payment_grid.addWidget(self.tunai_input, 2, 1, alignment=Qt.AlignRight)

        totals_payment_grid.addWidget(QLabel("Kembali:"), 3, 0, alignment=Qt.AlignRight)
        self.kembali_label = QLabel("Rp 0")
        self.kembali_label.setAlignment(Qt.AlignRight)
        self.kembali_label.setStyleSheet("font-weight: bold; color: green; font-size: 16px;")
        totals_payment_grid.addWidget(self.kembali_label, 3, 1, alignment=Qt.AlignRight)

        right_column_vertical_layout.addLayout(totals_payment_grid)  

        action_buttons_h_layout = QHBoxLayout()
        action_buttons_h_layout.addStretch(1)  
        self.pay_button = QPushButton("Bayar")
        self.pay_button.clicked.connect(self.process_payment)
        self.pay_button.setFixedSize(QSize(150, 50))
        action_buttons_h_layout.addWidget(self.pay_button)

        self.struk_button = QPushButton("Cetak Struk")
        self.struk_button.clicked.connect(
            lambda: self.print_receipt(items=None, subtotal_to_print=self.current_subtotal,
                                       grand_total_to_print=self.total_harga, is_reprint=True))
        self.struk_button.setFixedSize(QSize(150, 50))
        action_buttons_h_layout.addWidget(self.struk_button)

        right_column_vertical_layout.addLayout(action_buttons_h_layout)  

        bottom_main_layout.addLayout(right_column_vertical_layout) 
        main_layout.addLayout(bottom_main_layout)  

        self.calculate_totals()
        self.on_payment_method_changed(self.metode_pembayaran_bottom.currentText())

    def open_select_product_window(self):
        print("Kasir: 'Pilih Barang' button clicked. Opening SelectProductWindow.")
        from ui.select_product_window import SelectProductWindow
        self.select_product_window = SelectProductWindow(cashier_ref=self)
        self.select_product_window.show()

    def receive_selected_items(self, selected_items_list):
        print(f"Kasir: Received {len(selected_items_list)} selected items.")

        for item_from_picker in selected_items_list:
            item_id = item_from_picker['id']
            nama = item_from_picker['nama']
            harga_jual = item_from_picker['harga_jual']
            kategori = item_from_picker['kategori']  

            if item_id in self.selected_items_for_purchase:
                self.selected_items_for_purchase[item_id]['quantity'] += 1
                QMessageBox.information(self, "Item Diperbarui",
                                        f"Jumlah '{nama}' diperbarui menjadi {self.selected_items_for_purchase[item_id]['quantity']}.")
            else:
                self.selected_items_for_purchase[item_id] = {
                    'id': item_id, 
                    'nama': nama,
                    'harga_satuan': harga_jual,
                    'quantity': 1,
                    'kategori': kategori  
                }
                QMessageBox.information(self, "Item Ditambahkan", f"'{nama}' ditambahkan ke keranjang.")

        self._repopulate_kasir_table_from_purchase_list()

    def _repopulate_kasir_table_from_purchase_list(self):
        print("Kasir: Rebuilding main table from selected_items_for_purchase.")
        self.table.setUpdatesEnabled(False)
        self.table.setRowCount(0)

        ordered_item_ids = sorted(self.selected_items_for_purchase.keys(),
                                  key=lambda k: self.selected_items_for_purchase[k]['nama'])

        for row_idx, item_id in enumerate(ordered_item_ids):
            item_info = self.selected_items_for_purchase[item_id]  

            self.table.insertRow(row_idx)

            item_name_widget = QTableWidgetItem(item_info['nama'])
            item_name_widget.setFlags(item_name_widget.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 0, item_name_widget)

            spinbox = QSpinBox()
            spinbox.setMinimum(0)
            spinbox.setMaximum(9999)
            spinbox.setValue(item_info['quantity'])

            spinbox.valueChanged.connect(
                lambda value, item_id_for_callback=item_info['id']:  
                self.update_purchase_quantity(item_id_for_callback, value)
            )
            self.table.setCellWidget(row_idx, 1, spinbox) 

            item_price_widget = QTableWidgetItem(f"Rp {item_info['harga_satuan']:,.0f}")
            item_price_widget.setFlags(item_price_widget.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 2, item_price_widget)

            current_subtotal_line = item_info['quantity'] * item_info['harga_satuan']
            item_subtotal_widget = QTableWidgetItem(f"Rp {current_subtotal_line:,.0f}")
            item_subtotal_widget.setFlags(item_subtotal_widget.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 3, item_subtotal_widget)

        print(f"Kasir: Main table rebuilt with {self.table.rowCount()} items.")
        self.table.setUpdatesEnabled(True)
        self.table.viewport().update()
        QApplication.processEvents()
        self.calculate_totals()

    def update_purchase_quantity(self, item_id, new_quantity):
        print(f"Kasir: Updating purchase quantity for ID: {item_id} to {new_quantity}.")

        if new_quantity > 0:
            if item_id in self.selected_items_for_purchase:
                self.selected_items_for_purchase[item_id]['quantity'] = new_quantity
        else:
            if item_id in self.selected_items_for_purchase:
                del self.selected_items_for_purchase[item_id]
                print(f"Kasir: Removed item ID {item_id} from purchase list.")

        self._repopulate_kasir_table_from_purchase_list()

    def calculate_totals(self):
        print("Kasir: Calculating totals.")
        self.current_subtotal = 0
        for item_id, item_info in self.selected_items_for_purchase.items():
            self.current_subtotal += item_info['quantity'] * item_info['harga_satuan']

        self.subtotal_label.setText(f"Rp {self.current_subtotal:,.0f}")

        final_grand_total = self.current_subtotal

        if self.diskon_checkbox.isChecked():
            diskon_percentage = 0
            try:
                diskon_percentage = float(self.diskon_input.text().replace(",", "").strip())
                if not (0 <= diskon_percentage <= 100):
                    raise ValueError("Percentage must be between 0 and 100")
            except ValueError:
                QMessageBox.warning(self, "Input Diskon Invalid", "Masukkan persentase diskon antara 0-100.")
                self.diskon_input.setText("0")
                diskon_percentage = 0

            diskon_amount = self.current_subtotal * (diskon_percentage / 100)
            final_grand_total = self.current_subtotal - diskon_amount

        if self.current_subtotal > self.batas_diskon_config:
            percentage_from_config_amount = self.current_subtotal * (self.diskon_persen_config / 100)
            final_grand_total = max(0, final_grand_total - percentage_from_config_amount)

        self.total_harga = max(0, final_grand_total)
        self.grand_total_label.setText(f"Rp {self.total_harga:,.0f}")
        print(f"Kasir: SubTotal: {self.current_subtotal}, Grand Total (self.total_harga): {self.total_harga}.")
        self.calculate_change()

    def toggle_diskon_input(self, state):
        self.diskon_input.setEnabled(state == Qt.Checked)
        if not (state == Qt.Checked):
            self.diskon_input.setText("0")
        self.calculate_totals()

    def on_payment_method_changed(self, method):
        print(f"Kasir: Payment method changed to {method}.")
        if method == "Cash":
            self.tunai_input.setEnabled(True)
            self.tunai_input.setText("0")
            self.calculate_change()
        else:
            self.tunai_input.setText("0")
            self.tunai_input.setEnabled(False)
            self.kembali_label.setText("Rp 0")

    def calculate_change(self):
        print("Kasir: Calculating change.")
        tunai_received = 0
        try:
            tunai_received = float(self.tunai_input.text().replace("Rp", "").replace(",", "").strip())
        except ValueError:
            self.tunai_input.setText("0")
            tunai_received = 0

        change = tunai_received - self.total_harga
        self.kembali_label.setText(f"Rp {max(0, change):,.0f}")

        if self.metode_pembayaran_bottom.currentText() == "Cash":
            if tunai_received >= self.total_harga:
                self.tunai_input.setStyleSheet("background-color: lightgreen;")
            else:
                self.tunai_input.setStyleSheet("background-color: white;")
        else:
            self.tunai_input.setStyleSheet("")

    def process_payment(self):
        print("Kasir: Processing payment.")
        if not self.selected_items_for_purchase:
            QMessageBox.warning(self, "Keranjang Kosong", "Tambahkan barang terlebih dahulu sebelum pembayaran.")
            return

        metode = self.metode_pembayaran_bottom.currentText()

        if metode == "Cash":
            tunai_received = 0
            try:
                tunai_received = float(self.tunai_input.text().replace("Rp", "").replace(",", "").strip())
            except ValueError:
                pass
            if tunai_received < self.total_harga:
                QMessageBox.warning(self, "Pembayaran Kurang",
                                    f"Uang tunai kurang. Dibutuhkan: Rp {self.total_harga:,.0f}, Diterima: Rp {tunai_received:,.0f}")
                return

        db_path_full = os.path.join(get_app_dir(), "database", DB_NAME)
        conn = sqlite3.connect(db_path_full)
        cursor = conn.cursor()

        items_for_receipt = []
        for item_id, item_info in self.selected_items_for_purchase.items():
            nama = item_info['nama']
            jumlah = item_info['quantity']
            harga = item_info['harga_satuan']
            total_item_line = jumlah * harga

            items_for_receipt.append((nama, jumlah, harga))

            cursor.execute(
                "INSERT INTO transaksi (barang, jumlah, harga, total_harga, metode_pembayaran) VALUES (?, ?, ?, ?, ?)",
                (nama, jumlah, harga, total_item_line, metode)
            )

        conn.commit()
        conn.close()

        QMessageBox.information(self, "Pembayaran Berhasil", "Transaksi berhasil.")
        self.print_receipt(items=items_for_receipt, subtotal_to_print=self.current_subtotal,
                           grand_total_to_print=self.total_harga)

        self.selected_items_for_purchase = {}
        self._repopulate_kasir_table_from_purchase_list()  

        self.diskon_input.setText("0")
        self.diskon_checkbox.setChecked(False)
        self.tunai_input.setText("0")
        self.metode_pembayaran_bottom.setCurrentIndex(0)
        self.calculate_totals()
        print("Kasir: Cart cleared after payment.")

    def print_receipt(self, items=None, subtotal_to_print=None, grand_total_to_print=None, is_reprint=False):
        print("Kasir: Printing receipt.")

        if items is None:
            if not self.selected_items_for_purchase:
                QMessageBox.warning(self, "Keranjang Kosong", "Tidak ada barang untuk dicetak.")
                return
            items_to_print = []
            for item_id, item_info in self.selected_items_for_purchase.items():
                items_to_print.append((item_info['nama'], item_info['quantity'], item_info['harga_satuan']))
            items = items_to_print
            try:
                subtotal_to_print = float(self.subtotal_label.text().replace("Rp", "").replace(",", "").strip())
                grand_total_to_print = float(self.grand_total_label.text().replace("Rp", "").replace(",", "").strip())
            except ValueError:
                subtotal_to_print = 0.0
                grand_total_to_print = 0.0
                print("Warning: Could not parse total labels for printing. Using 0.")

        if not items:
            QMessageBox.warning(self, "Keranjang Kosong", "Tidak ada barang untuk dicetak.")
            return

        if self.printer.print_receipt(items, subtotal_to_print, grand_total_to_print):
            if not is_reprint:
                QMessageBox.information(self, "Struk", "Struk berhasil dicetak.")
            else:
                QMessageBox.information(self, "Struk", "Struk berhasil dicetak ulang.")
        else:
            QMessageBox.critical(self, "Error Printer",
                                 "Gagal mencetak struk. Pastikan printer terhubung dan konfigurasi ID benar.")