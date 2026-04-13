from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QHeaderView
)
from PyQt5.QtCore import Qt
from reports.report_generator import generate_pdf_report, generate_excel_report
from config import DB_NAME, get_app_dir
import sqlite3
import os

class ReportWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Laporan Penjualan & Riwayat Transaksi")
        self.setGeometry(150, 150, 1000, 700)
        self.db_path_full = os.path.join("database", DB_NAME)
        self.initUI()
        self.load_transaction_history()

    def initUI(self):
        layout = QVBoxLayout(self)

        self.title_label = QLabel("Riwayat Transaksi & Laporan")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels([
            "ID Transaksi", "Tanggal", "Nama Barang", "Jumlah", "Harga/Item", "Total Item", "Metode Pembayaran"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.history_table)

        button_layout = QHBoxLayout()
        self.generate_pdf_button = QPushButton("Generate Laporan PDF")
        self.generate_pdf_button.clicked.connect(self.generate_pdf_report_action)
        button_layout.addWidget(self.generate_pdf_button)

        self.generate_excel_button = QPushButton("Generate Laporan Excel")
        self.generate_excel_button.clicked.connect(self.generate_excel_report_action)
        button_layout.addWidget(self.generate_excel_button)

        layout.addLayout(button_layout)

    def load_transaction_history(self):
        self.history_table.setRowCount(0)
        db_path_full = os.path.join(get_app_dir(), "database", DB_NAME)
        conn = sqlite3.connect(db_path_full)
        cursor = conn.cursor()
        cursor.execute("SELECT id, timestamp, barang, jumlah, harga, total_harga, metode_pembayaran FROM transaksi ORDER BY id DESC")
        transactions = cursor.fetchall()
        conn.close()

        self.history_table.setRowCount(len(transactions))
        for row_idx, transaction in enumerate(transactions):
            trans_id, timestamp, barang, jumlah, harga, total, metode = transaction
            self.history_table.setItem(row_idx, 0, QTableWidgetItem(str(trans_id)))
            self.history_table.setItem(row_idx, 1, QTableWidgetItem(timestamp))
            self.history_table.setItem(row_idx, 2, QTableWidgetItem(barang))
            self.history_table.setItem(row_idx, 3, QTableWidgetItem(str(jumlah)))
            self.history_table.setItem(row_idx, 4, QTableWidgetItem(f"Rp {harga:,.0f}"))
            self.history_table.setItem(row_idx, 5, QTableWidgetItem(f"Rp {total:,.0f}"))
            self.history_table.setItem(row_idx, 6, QTableWidgetItem(metode))

    def generate_pdf_report_action(self):
        try:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Simpan Laporan PDF", "laporan_bulanan.pdf", "PDF Files (*.pdf)", options=options)
            if file_name:
                output_path = generate_pdf_report(output_path=file_name)
                QMessageBox.information(self, "Laporan Berhasil", f"Laporan PDF berhasil dibuat di:\n{output_path}")
            else:
                QMessageBox.information(self, "Dibatalkan", "Pembuatan laporan PDF dibatalkan.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan saat membuat laporan PDF: {e}")

    def generate_excel_report_action(self):
        try:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Simpan Laporan Excel", "laporan_bulanan.xlsx", "Excel Files (*.xlsx);;CSV Files (*.csv)", options=options)
            if file_name:
                if not (file_name.lower().endswith('.xlsx') or file_name.lower().endswith('.csv')):
                    if QMessageBox.question(self, "Pilih Format", "Pilih format Excel (.xlsx) atau CSV (.csv)?",
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes) == QMessageBox.Yes:
                        file_name += ".xlsx"
                    else:
                        file_name += ".csv"

                output_path = generate_excel_report(output_path=file_name)
                QMessageBox.information(self, "Laporan Berhasil", f"Laporan Excel/CSV berhasil dibuat di:\n{output_path}")
            else:
                QMessageBox.information(self, "Dibatalkan", "Pembuatan laporan Excel/CSV dibatalkan.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan saat membuat laporan Excel/CSV: {e}")