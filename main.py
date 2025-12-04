import sys
import os
from PyQt6.QtWidgets import QApplication
from ui_main import InsuranceApp

def get_resource_path(filename):
    """
    مسیر صحیح فایل رو برمی‌گردونه
    - اگه برنامه exe شده: از مسیر exe
    - اگه .py باشه: از مسیر فایل جاری
    """
    if getattr(sys, 'frozen', False):
        # برنامه exe شده (PyInstaller)
        base_path = sys._MEIPASS
    else:
        # برنامه هنوز .py هست
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, filename)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # مسیر صحیح فایل Excel
    excel_file = get_resource_path("ghardash.xlsx")
    
    win = InsuranceApp(excel_file)
    win.show()
    sys.exit(app.exec())
