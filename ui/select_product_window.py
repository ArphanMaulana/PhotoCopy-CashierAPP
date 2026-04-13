from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QAbstractItemView, QCheckBox  
)
from PyQt5.QtCore import Qt
import sqlite3
import os
from config import DB_NAME, get_app_dir


class SelectProductWindow(QWidget):
    def __init__(self, cashier_ref=None): 
        super().__init__()
        self.setWindowTitle("Pilih Barang untuk Kasir")
        self.setGeometry(100, 100, 1000, 700)
        self.db_path_full = os.path.join("database", DB_NAME)
        self.cashier_ref = cashier_ref 

        self.item_data = {} 
        self.initUI()
        self.load_items_to_table() 

    def initUI(self):
        layout = QVBoxLayout(self)

        self.title_label = QLabel("PILIH BARANG")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(self.title_label)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari Item...")
        self.search_input.textChanged.connect(self.search_items)
        search_layout.addWidget(QLabel("Cari:"))
        search_layout.addWidget(self.search_input)
        search_layout.addStretch(1)
        layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4) 
        self.table.setHorizontalHeaderLabels(
            ["Nama Barang", "Kategori", "Harga Jual", "Pilih"])  
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)  
        self.table.setColumnWidth(3, 50)  

        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)  
        layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)  
        self.add_selected_button = QPushButton("Tambahkan Item Terpilih")
        self.add_selected_button.clicked.connect(self.add_selected_items_to_cashier)
        button_layout.addWidget(self.add_selected_button)
        layout.addLayout(button_layout)

    def load_items_to_table(self):
        print("SelectProductWindow: Loading items to table...")
        self.table.setRowCount(0)
        conn = sqlite3.connect(self.db_path_full)
        cursor = conn.cursor()
        cursor.execute("SELECT nama, kategori, harga_jual, id FROM barang")
        items = cursor.fetchall()
        conn.close()

        print(f"SelectProductWindow: Retrieved {len(items)} items from database: {items}")

        self.item_data = {} 
        self.table.setRowCount(len(items))
        for row_idx, item in enumerate(items):
            nama, kategori, harga_jual, item_id = item
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(nama)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(kategori)))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(harga_jual)))

            checkbox = QCheckBox()
            checkbox.setChecked(False) 
            self.table.setCellWidget(row_idx, 3, checkbox)

            self.item_data[row_idx] = {
                'id': item_id,
                'nama': nama,
                'kategori': kategori, 
                'harga_jual': harga_jual,
                'checkbox_widget': checkbox  
            }
        print("SelectProductWindow: Table load complete.")

    def search_items(self, text):
        db_path_full = os.path.join(get_app_dir(), "database", DB_NAME)
        conn = sqlite3.connect(db_path_full)
        cursor = conn.cursor()
        query = f"SELECT nama, kategori, harga_jual, id FROM barang WHERE nama LIKE ? OR kategori LIKE ?"
        params = (f"%{text}%", f"%{text}%")

        if text.isdigit():
            query += " OR id LIKE ?"
            params += (f"%{text}%",)

        cursor.execute(query, params)
        items = cursor.fetchall()
        conn.close()

        self.item_data = {}
        self.table.setRowCount(len(items))
        for row_idx, item in enumerate(items):
            nama, kategori, harga_jual, item_id = item
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(nama)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(kategori)))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(harga_jual)))

            checkbox = QCheckBox()
            checkbox.setChecked(False)
            self.table.setCellWidget(row_idx, 3, checkbox)

            self.item_data[row_idx] = {
                'id': item_id,
                'nama': nama,
                'kategori': kategori,
                'harga_jual': harga_jual,
                'checkbox_widget': checkbox
            }

    def add_selected_items_to_cashier(self):
        if not self.cashier_ref:
            QMessageBox.critical(self, "Error", "Jendela kasir tidak ditemukan. Tidak dapat menambahkan barang.")
            return

        selected_items_list = []
        for row_idx in range(self.table.rowCount()):
            item_data = self.item_data.get(row_idx)
            if item_data and item_data['checkbox_widget'].isChecked():
                selected_items_list.append({
                    'id': item_data['id'],
                    'nama': item_data['nama'],
                    'harga_jual': item_data['harga_jual'],
                    'kategori': item_data['kategori']
                })

        if not selected_items_list:
            QMessageBox.warning(self, "Pilih Barang", "Pilih setidaknya satu barang untuk ditambahkan.")
            return

        self.cashier_ref.receive_selected_items(selected_items_list)
        self.close()