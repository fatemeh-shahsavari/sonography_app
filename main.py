import sys
import os
import ctypes
import platform
from PyQt6.QtWidgets import QApplication
from ui_main import InsuranceApp
from utils import resource_path  # ایمپورت تابع جدید

# 1. رفع مشکل تاری در ویندوز (High DPI Fix)
if platform.system() == "Windows":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    # تنظیم متغیر محیطی برای PyQt6
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # تنظیم فونت کلی برای کل برنامه (اختیاری ولی توصیه شده)
    # app.setFont(QFont("Vazirmatn", 10))

    # 2. استفاده از resource_path برای فایل اکسل
    # این کار باعث می‌شود اگر فایل اکسل را داخل exe گذاشتید، برنامه آن را پیدا کند
    excel_file = resource_path("ghardash.xlsx")
    
    win = InsuranceApp(excel_file)
    win.show()
    
    sys.exit(app.exec())
