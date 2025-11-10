"""
پنجره جستجوی بیماران بر اساس نام
"""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class PatientSearchDialog(QDialog):
    """پنجره جستجوی بیمار"""
    
    # سیگنال برای ارسال اطلاعات بیمار انتخاب شده
    patient_selected = pyqtSignal(dict)
    
    def __init__(self, parent, patient_records_manager):
        super().__init__(parent)
        self.patient_records = patient_records_manager
        self.setWindowTitle("🔍 جستجوی بیمار")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.resize(900, 600)
        self.init_ui()
        
        # بارگذاری اولیه آخرین بیماران
        self.load_recent_patients()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # بخش جستجو
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍 جستجو با نام یا نام خانوادگی:"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("مثال: احمدی، محمد، علی...")
        self.search_input.textChanged.connect(self.search_patients)
        self.search_input.setFont(QFont("Vazirmatn", 11))
        search_layout.addWidget(self.search_input)
        
        btn_clear = QPushButton("🔄 پاک کردن")
        btn_clear.clicked.connect(self.clear_search)
        search_layout.addWidget(btn_clear)
        
        layout.addLayout(search_layout)
        
        # راهنما
        help_label = QLabel("💡 حداقل 2 حرف تایپ کنید تا جستجو شروع شود")
        help_label.setStyleSheet("color: #666; font-size: 10px; padding: 5px;")
        layout.addWidget(help_label)
        
        # جدول نتایج
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "نام و نام خانوادگی", "کد ملی", "بیمه", 
            "تعداد مراجعات", "آخرین مراجعه", "عملیات"
        ])
        self.results_table.setFont(QFont("Vazirmatn", 10))
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.results_table.doubleClicked.connect(self.on_row_double_clicked)
        
        layout.addWidget(self.results_table)
        
        # دکمه‌های پایین
        btn_layout = QHBoxLayout()
        
        btn_select = QPushButton("✅ انتخاب بیمار")
        btn_select.clicked.connect(self.select_patient)
        btn_select.setStyleSheet("background-color: #4caf50; font-weight: bold;")
        btn_layout.addWidget(btn_select)
        
        btn_view = QPushButton("📋 مشاهده سوابق کامل")
        btn_view.clicked.connect(self.view_full_history)
        btn_layout.addWidget(btn_view)
        
        btn_close = QPushButton("❌ بستن")
        btn_close.clicked.connect(self.close)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_recent_patients(self):
        """بارگذاری آخرین بیماران"""
        try:
            patients = self.patient_records.get_all_patients(limit=50)
            self.display_results(patients)
        except Exception as e:
            print(f"خطا در بارگذاری بیماران: {e}")
    
    def search_patients(self, text):
        """جستجوی بیماران"""
        if len(text.strip()) < 2:
            # اگر کمتر از 2 حرف، نمایش آخرین بیماران
            self.load_recent_patients()
            return
        
        results = self.patient_records.search_by_name(text)
        self.display_results(results)
    
    def display_results(self, patients):
        """نمایش نتایج در جدول"""
        self.results_table.setRowCount(0)
        
        if not patients:
            return
        
        for patient in patients:
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            
            # نام
            self.results_table.setItem(row, 0, QTableWidgetItem(patient['name']))
            
            # کد ملی
            self.results_table.setItem(row, 1, QTableWidgetItem(patient['national_code']))
            
            # بیمه
            self.results_table.setItem(row, 2, QTableWidgetItem(patient['insurance']))
            
            # تعداد مراجعات
            self.results_table.setItem(row, 3, QTableWidgetItem(str(patient['total_invoices'])))
            
            # آخرین مراجعه
            self.results_table.setItem(row, 4, QTableWidgetItem(patient['last_visit']))
            
            # دکمه انتخاب
            btn_select = QPushButton("✅ انتخاب")
            btn_select.clicked.connect(lambda ch, p=patient: self.emit_patient_data(p))
            self.results_table.setCellWidget(row, 5, btn_select)
    
    def clear_search(self):
        """پاک کردن جستجو"""
        self.search_input.clear()
        self.load_recent_patients()
    
    def select_patient(self):
        """انتخاب بیمار از ردیف فعلی"""
        current_row = self.results_table.currentRow()
        
        if current_row < 0:
            QMessageBox.warning(self, "خطا", "⚠️ لطفاً یک بیمار را انتخاب کنید!")
            return
        
        national_code = self.results_table.item(current_row, 1).text()
        patient = self.patient_records.get_patient_summary(national_code)
        
        if patient:
            self.emit_patient_data(patient)
    
    def on_row_double_clicked(self):
        """دوبار کلیک روی ردیف"""
        self.select_patient()
    
    def emit_patient_data(self, patient):
        """ارسال اطلاعات بیمار و بستن پنجره"""
        self.patient_selected.emit(patient)
        self.close()
    
    def view_full_history(self):
        """مشاهده سوابق کامل"""
        current_row = self.results_table.currentRow()
        
        if current_row < 0:
            QMessageBox.warning(self, "خطا", "⚠️ لطفاً یک بیمار را انتخاب کنید!")
            return
        
        national_code = self.results_table.item(current_row, 1).text()
        patient = self.patient_records.get_patient_summary(national_code)
        
        if patient:
            try:
                from ui_patient_history import PatientHistoryDialog
                dialog = PatientHistoryDialog(self, patient)
                dialog.exec()
            except ImportError:
                QMessageBox.warning(self, "خطا", "⚠️ ماژول نمایش سوابق یافت نشد!")
