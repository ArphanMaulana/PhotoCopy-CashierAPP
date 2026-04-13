from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QComboBox,
    QAbstractItemView
)
from PyQt5.QtCore import Qt
import sqlite3
import os
from config import DB_NAME, get_app_dir


class InputDataWindow(QWidget):
    def __init__(self):  
        super().__init__()
        self.setWindowTitle("Input Barang")
        self.setGeometry(100, 100, 1000, 700)
        self.db_path_full = os.path.join("database", DB_NAME)

        self.initUI()
        self.initialize_item_db()
        self.load_items_to_table()

    def initialize_item_db(self):
        db_path_full = os.path.join(get_app_dir(), "database", DB_NAME)
        conn = sqlite3.connect(db_path_full)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS barang (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT NOT NULL UNIQUE,
                kategori TEXT,
                harga_jual REAL NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def initUI(self):
        layout = QVBoxLayout(self)

        self.title_label = QLabel("INPUT BARANG")
        self.title_label.setAlignment(Qt.AlignLeft)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(self.title_label)

        self.input_form_layout = QHBoxLayout()
        self.input_nama = QLineEdit()
        self.input_nama.setPlaceholderText("Nama Barang")
        self.input_form_layout.addWidget(self.input_nama)

        self.input_kategori = QComboBox()
        self.input_kategori.addItems(["Barang", "Jasa"])
        self.input_kategori.setPlaceholderText("Pilih Kategori")
        self.input_form_layout.addWidget(self.input_kategori)

        self.input_harga_jual = QLineEdit()
        self.input_harga_jual.setPlaceholderText("Harga Jual")
        self.input_form_layout.addWidget(self.input_harga_jual)
        layout.addLayout(self.input_form_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Nama Barang", "Kategori", "Harga Jual"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.itemClicked.connect(self.populate_inputs_from_selection)
        layout.addWidget(self.table)

        self.button_layout = QHBoxLayout()
        self.add_button = QPushButton("Tambah")
        self.add_button.clicked.connect(self.add_item)
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_item)
        self.delete_button = QPushButton("Hapus")
        self.delete_button.clicked.connect(self.delete_item)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari...")
        self.search_input.textChanged.connect(self.search_items)
        self.search_input.setFixedWidth(200)

        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.edit_button)
        self.button_layout.addWidget(self.delete_button)
        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.search_input)

        layout.addLayout(self.button_layout)

    def load_items_to_table(self):
        print("InputDataWindow: Loading items to table...")
        self.table.setRowCount(0)
        db_path_full = os.path.join(get_app_dir(), "database", DB_NAME)
        conn = sqlite3.connect(db_path_full)
        cursor = conn.cursor()
        cursor.execute("SELECT nama, kategori, harga_jual, id FROM barang")
        items = cursor.fetchall()
        conn.close()

        print(f"InputDataWindow: Retrieved {len(items)} items from database: {items}")

        self.item_data = {}
        self.table.setRowCount(len(items))
        for row_idx, item in enumerate(items):
            nama, kategori, harga_jual, item_id = item
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(nama)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(kategori)))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(harga_jual)))
            self.item_data[row_idx] = {'id': item_id, 'nama': nama, 'kategori': kategori, 'harga_jual': harga_jual}
        print("InputDataWindow: Table load complete.")

    def add_item(self):
        nama = self.input_nama.text()
        kategori = self.input_kategori.currentText()
        harga_jual_str = self.input_harga_jual.text()

        print(f"InputDataWindow: Attempting to add: Nama={nama}, Kategori={kategori}, Harga={harga_jual_str}")

        if not nama or not harga_jual_str:
            QMessageBox.warning(self, "Input Tidak Lengkap", "Nama Barang dan Harga Jual harus diisi.")
            return

        try:
            harga_jual = float(harga_jual_str)
        except ValueError:
            QMessageBox.warning(self, "Format Salah", "Harga Jual harus berupa angka.")
            return

        db_path_full = os.path.join(get_app_dir(), "database", DB_NAME)
        conn = sqlite3.connect(db_path_full)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO barang (nama, kategori, harga_jual) VALUES (?, ?, ?)",
                (nama, kategori, harga_jual)
            )
            conn.commit()
            print("InputDataWindow: Item inserted into database and committed.")
            QMessageBox.information(self, "Berhasil", f"Barang '{nama}' berhasil ditambahkan.")
            self.clear_inputs()
            self.load_items_to_table()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Nama Barang sudah ada. Gunakan Nama yang unik.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan saat menambahkan barang: {e}")
            print(f"InputDataWindow: Error during add_item: {e}")
        finally:
            conn.close()

    def populate_inputs_from_selection(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        item_data = self.item_data.get(row)

        if item_data:
            print(f"InputDataWindow: Item selected in management mode: {item_data['nama']}. Populating inputs.")
            self.input_nama.setText(item_data['nama'])
            self.input_kategori.setCurrentText(item_data['kategori'])
            self.input_harga_jual.setText(str(item_data['harga_jual']))

    def edit_item(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Pilih Barang", "Pilih barang yang ingin diedit dari tabel.")
            return

        row = selected_rows[0].row()
        original_item_id = self.item_data[row]['id']

        nama = self.input_nama.text()
        kategori = self.input_kategori.currentText()
        harga_jual_str = self.input_harga_jual.text()

        if not nama or not harga_jual_str:
            QMessageBox.warning(self, "Input Tidak Lengkap", "Nama Barang dan Harga Jual harus diisi untuk edit.")
            return

        try:
            harga_jual = float(harga_jual_str)
        except ValueError:
            QMessageBox.warning(self, "Format Salah", "Harga Jual harus berupa angka.")
            return

        db_path_full = os.path.join(get_app_dir(), "database", DB_NAME)
        conn = sqlite3.connect(db_path_full)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE barang SET nama=?, kategori=?, harga_jual=? WHERE id=?",
                (nama, kategori, harga_jual, original_item_id)
            )
            conn.commit()
            QMessageBox.information(self, "Berhasil", f"Barang '{nama}' berhasil diperbarui.")
            self.clear_inputs()
            self.load_items_to_table()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Nama Barang sudah ada. Gunakan Nama yang unik.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan saat mengedit barang: {e}")
        finally:
            conn.close()

    def delete_item(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Pilih Barang", "Pilih barang yang ingin dihapus dari tabel.")
            return

        reply = QMessageBox.question(self, 'Konfirmasi Hapus',
                                     "Anda yakin ingin menghapus barang ini?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        row = selected_rows[0].row()
        item_id_to_delete = self.item_data[row]['id']

        db_path_full = os.path.join(get_app_dir(), "database", DB_NAME)
        conn = sqlite3.connect(db_path_full)
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM barang WHERE id=?", (item_id_to_delete,))
            conn.commit()
            QMessageBox.information(self, "Berhasil", "Barang berhasil dihapus.")
            self.clear_inputs()
            self.load_items_to_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan saat menghapus barang: {e}")
        finally:
            conn.close()

    def clear_inputs(self):
        self.input_nama.clear()
        self.input_kategori.setCurrentIndex(0)
        self.input_harga_jual.clear()

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
            self.item_data[row_idx] = {'id': item_id, 'nama': nama, 'kategori': kategori, 'harga_jual': harga_jual}