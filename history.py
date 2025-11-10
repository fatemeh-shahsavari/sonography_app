"""
ماژول تاریخچه فاکتورها
"""
import os
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton
from PyQt6.QtCore import Qt

class HistoryDialog(QDialog):
    """پنجره تاریخچه فاکتورها"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("📜 تاریخچه فاکتورها")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.resize(700, 500)
        
        layout = QVBoxLayout()
        
        # لیست فاکتورها
        self.history_list = QListWidget()
        self.load_history()
        layout.addWidget(self.history_list)
        
        # دکمه‌ها
        btn_layout = QHBoxLayout()
        
        btn_open = QPushButton("📂 باز کردن فاکتور")
        btn_open.clicked.connect(self.open_selected)
        btn_layout.addWidget(btn_open)
        
        btn_folder = QPushButton("📁 باز کردن پوشه")
        btn_folder.clicked.connect(lambda: os.startfile("invoices_history"))
        btn_layout.addWidget(btn_folder)
        
        btn_refresh = QPushButton("🔄 تازه‌سازی")
        btn_refresh.clicked.connect(self.load_history)
        btn_layout.addWidget(btn_refresh)
        
        btn_close = QPushButton("❌ بستن")
        btn_close.clicked.connect(self.close)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def load_history(self):
        """بارگذاری لیست فاکتورها"""
        self.history_list.clear()
        try:
            history_files = sorted(
                [f for f in os.listdir("invoices_history") if f.endswith('.pdf')], 
                reverse=True
            )
            
            if not history_files:
                self.history_list.addItem("هیچ فاکتوری یافت نشد")
                return
            
            for file in history_files:
                # فرمت نمایش بهتر
                parts = file.replace('.pdf', '').split('_')
                if len(parts) >= 3:
                    name = parts[0]
                    date = f"{parts[1][:4]}/{parts[1][4:6]}/{parts[1][6:8]}"
                    time = f"{parts[2][:2]}:{parts[2][2:4]}"
                    display = f"👤 {name} | 📅 {date} | 🕐 {time}"
                    self.history_list.addItem(display)
                else:
                    self.history_list.addItem(file)
        except Exception as e:
            self.history_list.addItem(f"خطا در بارگذاری: {str(e)}")
    
    def open_selected(self):
        """باز کردن فاکتور انتخاب‌شده"""
        current_item = self.history_list.currentItem()
        if not current_item:
            return
        
        # پیدا کردن فایل واقعی
        try:
            all_files = sorted(
                [f for f in os.listdir("invoices_history") if f.endswith('.pdf')], 
                reverse=True
            )
            selected_index = self.history_list.currentRow()
            if 0 <= selected_index < len(all_files):
                file_path = f"invoices_history/{all_files[selected_index]}"
                os.startfile(file_path)
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "خطا", f"خطا در باز کردن فایل:\n{str(e)}")
