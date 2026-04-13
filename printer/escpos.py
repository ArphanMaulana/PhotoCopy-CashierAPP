from escpos.printer import Usb
import usb.core # To re-check device existence
from config import DISKON_PERSEN, PRINTER_VENDOR_ID, PRINTER_PRODUCT_ID

class Printer:
    def __init__(self, vendor_id=None, product_id=None):
        self.vendor_id = vendor_id if vendor_id is not None else PRINTER_VENDOR_ID
        self.product_id = product_id if product_id is not None else PRINTER_PRODUCT_ID
        self.device = None
        self._connect_printer()

    def _connect_printer(self):
        try:
            dev = usb.core.find(idVendor=self.vendor_id, idProduct=self.product_id)
            if dev is None:
                print(f"Printer (Vendor ID: {hex(self.vendor_id)}, Product ID: {hex(self.product_id)}) not found.")
                self.device = None
            else:
                self.device = Usb(self.vendor_id, self.product_id)
                print("Printer connected successfully.")
        except Exception as e:
            print(f"Failed to connect printer (Vendor ID: {hex(self.vendor_id)}, Product ID: {hex(self.product_id)}): {e}")
            self.device = None

    def update_printer_ids(self, vendor_id, product_id):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self._connect_printer()

    def is_connected(self):
        return self.device is not None

    def print_receipt(self, items, subtotal, grand_total_after_discount):
        if not self.device:
            print("Printer tidak tersedia.")
            return False

        try:
            self.device.text("=== STRUK PEMBAYARAN ===\n")
            for nama, jumlah, harga in items:
                self.device.text(f"{nama} x{jumlah} @Rp{harga:,.0f}\n")

            self.device.text("-------------------------\n")
            self.device.text(f"Subtotal: Rp{subtotal:,.0f}\n")
            if subtotal != grand_total_after_discount:
                self.device.text(f"Grand Total: Rp{grand_total_after_discount:,.0f}\n")

            self.device.text("=========================\n\n")
            self.device.cut()
            return True
        except Exception as e:
            print(f"Error printing receipt: {e}")
            self.device = None
            return False

    def print_test_page(self):
        if not self.device:
            print("Printer tidak tersedia untuk test page.")
            return False
        try:
            self.device.text("=== TEST PRINT ===\n")
            self.device.text("Ini adalah halaman tes dari aplikasi kasir Anda.\n")
            self.device.text("Jika Anda bisa membaca ini, printer terhubung dengan baik.\n\n")
            self.device.cut()
            return True
        except Exception as e:
            print(f"Error printing test page: {e}")
            self.device = None
            return False