import sqlite3
import os
from config import DB_NAME, get_app_dir 

def initialize_application_database():
    base_dir = get_app_dir()
    
    db_dir = os.path.join(base_dir, "database")
    
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    db_path_full = os.path.join(db_dir, DB_NAME)
    
    conn = sqlite3.connect(db_path_full)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barang TEXT NOT NULL,
            jumlah INTEGER NOT NULL,
            harga REAL NOT NULL,
            total_harga REAL NOT NULL,
            metode_pembayaran TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

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
    print(f"Database '{DB_NAME}' initialized successfully at {db_path_full}.")

if __name__ == "__main__":
    initialize_application_database()