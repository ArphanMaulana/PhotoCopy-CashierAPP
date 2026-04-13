from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import sqlite3
import os
import pandas as pd
from config import DB_NAME


def get_transaction_data():
    db_path_full = os.path.join("database", DB_NAME)
    conn = sqlite3.connect(db_path_full)
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, barang, jumlah, harga, total_harga, metode_pembayaran FROM transaksi ORDER BY timestamp ASC")
    data = cursor.fetchall()
    conn.close()
    return data

def generate_pdf_report(output_path="laporan_bulanan.pdf"):
    data = get_transaction_data()

    c = canvas.Canvas(output_path, pagesize=A4)
    c.setFont("Helvetica", 12)
    c.drawString(50, 800, "Laporan Penjualan Bulanan")
    y = 770

    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Tanggal")
    c.drawString(150, y, "Barang")
    c.drawString(300, y, "Jumlah")
    c.drawString(350, y, "Harga/Item")
    c.drawString(450, y, "Subtotal")
    c.drawString(550, y, "Metode")
    y -= 15
    c.line(50, y, 600, y)
    y -= 10

    c.setFont("Helvetica", 10)
    grand_total = 0
    for item in data:
        trans_id, timestamp, barang, jumlah, harga_per_item, total_item_price, metode = item
        date_only = timestamp.split(' ')[0]

        c.drawString(50, y, date_only)
        c.drawString(150, y, barang)
        c.drawString(300, y, str(jumlah))
        c.drawString(350, y, f"Rp{harga_per_item:,.0f}")
        c.drawString(450, y, f"Rp{total_item_price:,.0f}")
        c.drawString(550, y, metode)
        grand_total += total_item_price
        y -= 20
        if y < 100:
            c.showPage()
            c.setFont("Helvetica", 12)
            c.drawString(50, 800, "Laporan Penjualan Bulanan (Lanjutan)")
            y = 770
            c.setFont("Helvetica-Bold", 10)
            c.drawString(50, y, "Tanggal")
            c.drawString(150, y, "Barang")
            c.drawString(300, y, "Jumlah")
            c.drawString(350, y, "Harga/Item")
            c.drawString(450, y, "Subtotal")
            c.drawString(550, y, "Metode")
            y -= 15
            c.line(50, y, 600, y)
            y -= 10
            c.setFont("Helvetica", 10)

    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, f"Grand Total Penjualan: Rp{grand_total:,.0f}")
    c.save()
    return output_path

def generate_excel_report(output_path="laporan_bulanan.xlsx"):
    data = get_transaction_data()
    columns = ["ID Transaksi", "Timestamp", "Nama Barang", "Jumlah", "Harga per Item", "Total Item Harga", "Metode Pembayaran"]
    df = pd.DataFrame(data, columns=columns)

    if output_path.lower().endswith('.csv'):
        df.to_csv(output_path, index=False)
    else:
        df.to_excel(output_path, index=False)
    return output_path