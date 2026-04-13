import sys
import multiprocessing 

from PyQt5.QtWidgets import QApplication
from ui.main_menu_window import MainMenuWindow
from config import get_resource_path

from db_setup import initialize_application_database 

if __name__ == "__main__":
    multiprocessing.freeze_support() 
    
    app = QApplication(sys.argv)
    
    # 2. PANGGIL FUNGSINYA DI SINI (Biar tabel otomatis kebuat kalau belum ada)
    initialize_application_database()
    
    qss_path = get_resource_path("resources/styles.qss")
    try:
        with open(qss_path, "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"Peringatan: File style tidak ditemukan di {qss_path}")

    window = MainMenuWindow()
    window.show()
    sys.exit(app.exec_())

from ui.main_menu_window import MainMenuWindow

def apply_stylesheet(app, filepath):
    try:
        with open(filepath, "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"Stylesheet file not found: {filepath}")

def main():
    app = QApplication(sys.argv)
    stylesheet_path = os.path.join(script_dir, "resources", "styles.qss")
    apply_stylesheet(app, stylesheet_path)

    db_setup_path = os.path.join(script_dir, "db_setup.py")
    try:
        db_exists = os.path.exists(os.path.join(script_dir, "database", "data.db"))
        if not db_exists:
            print("Checking/Initializing database...")
            subprocess.run([sys.executable, db_setup_path], check=True)
        else:
            print("Database already exists. Skipping initialization.")
    except subprocess.CalledProcessError as e:
        print(f"Error initializing database: {e}")
        sys.exit(1) 

    window = MainMenuWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

    multiprocessing.freeze_support() 
    
    app = QApplication(sys.argv)
    
    qss_path = get_resource_path("resources/styles.qss")
    try:
        with open(qss_path, "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"Peringatan: File style tidak ditemukan di {qss_path}")

    window = MainMenuWindow()
    window.show()
    sys.exit(app.exec_())