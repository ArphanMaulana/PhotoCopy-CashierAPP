import os
import sys

def get_resource_path(relative_path):
    """
    Untuk file bawaan yang di-bundle PyInstaller.
    Mengarah ke folder temporary Windows (_MEIPASS).
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.abspath(".")

# NAH INI YANG KEMAREN KETINGGALAN
DB_NAME = "data.db" 

# Biar file lain gampang manggilnya
DB_DIR = os.path.join(get_app_dir(), 'database')
DB_PATH = os.path.join(DB_DIR, DB_NAME)

DB_DIR = os.path.join(get_app_dir(), 'database')
DB_PATH = os.path.join(DB_DIR, 'data.db')

DISKON_PERSEN = 10
BATAS_DISKON = 500_000

PRINTER_VENDOR_ID = 0x04b8
PRINTER_PRODUCT_ID = 0x0e15

QRIS_BUSINESS_ID = "YOUR_DEFAULT_QRIS_ID_HERE"