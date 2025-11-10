"""
رابط کاربری نمایش سوابق بیمار
"""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, 
    QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class PatientHistoryDialog(QDialog):
    """پنجره نمایش سوابق بیمار"""
    
    def __init__(self, parent, patient_summary):
        super().__init__(parent)
        self.patient_summary = patient_summary
        self.setWindowTitle(f"📋 سوابق بیمار: {patient_summary['name']}")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.resize(900, 600)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # بخش اطلاعات خلاصه
        summary_group = QGroupBox("🔍 اطلاعات خلاصه")
        summary_layout = QVBoxLayout()
        
        summary_text = f"""
👤 نام بیمار: {self.patient_summary['name']}
🏥 بیمه: {self.patient_summary['insurance']}
🆔 کد ملی: {self.patient_summary['national_code']}
📊 تعداد مراجعات: {self.patient_summary['total_invoices']}
💰 جمع کل پرداختی: {self.patient_summary['total_amount']:,} ریال
📅 آخرین مراجعه: {self.patient_summary['last_visit']}
        """
        
        summary_label = QLabel(summary_text)
        summary_label.setFont(QFont("Vazirmatn", 11))
        summary_label.setStyleSheet("""
            background-color: #e3f2fd;
            padding: 15px;
            border-radius: 8px;
            color: #01579b;
            font-weight: bold;
        """)
        summary_layout.addWidget(summary_label)
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # جدول فاکتورها
        invoices_group = QGroupBox("📋 لیست فاکتورها")
        invoices_layout = QVBoxLayout()
        
        self.invoices_table = QTableWidget()
        self.invoices_table.setColumnCount(6)
        self.invoices_table.setHorizontalHeaderLabels([
            "تاریخ", "کد پیگیری", "نوع تعرفه", 
            "جمع کل", "سهم بیمار", "عملیات"
        ])
        self.invoices_table.setFont(QFont("Vazirmatn", 10))
        
        # پر کردن جدول
        for invoice in reversed(self.patient_summary['invoices']):
            row = self.invoices_table.rowCount()
            self.invoices_table.insertRow(row)
            
            self.invoices_table.setItem(row, 0, QTableWidgetItem(invoice['date']))
            self.invoices_table.setItem(row, 1, QTableWidgetItem(invoice['tracking_code']))
            self.invoices_table.setItem(row, 2, QTableWidgetItem(invoice['tariff_type']))
            self.invoices_table.setItem(row, 3, QTableWidgetItem(f"{invoice['total']:,}"))
            self.invoices_table.setItem(row, 4, QTableWidgetItem(f"{invoice['patient_pay']:,}"))
            
            # دکمه باز کردن PDF
            btn_open = QPushButton("📄 مشاهده")
            btn_open.clicked.connect(lambda ch, path=invoice['pdf_path']: self.open_pdf(path))
            self.invoices_table.setCellWidget(row, 5, btn_open)
        
        self.invoices_table.resizeColumnsToContents()
        invoices_layout.addWidget(self.invoices_table)
        invoices_group.setLayout(invoices_layout)
        layout.addWidget(invoices_group)
        
        # دکمه بستن
        btn_close = QPushButton("❌ بستن")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)
        
        self.setLayout(layout)
    
    def open_pdf(self, pdf_path):
        """باز کردن فایل PDF"""
        try:
            if os.path.exists(pdf_path):
                os.startfile(pdf_path)
            else:
                QMessageBox.warning(self, "خطا", f"⚠️ فایل یافت نشد:\n{pdf_path}")
        except Exception as e:
            QMessageBox.warning(self, "خطا", f"❌ خطا در باز کردن فایل:\n{str(e)}")
