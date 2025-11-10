"""
پنجره تنظیمات کامل برنامه - نسخه جدید برای all.xlsx
شامل: اطلاعات موسسه، فایلها، ضرایب کای (6 ضریب)، رنگها، ظاهر
"""

import json
import os
import subprocess
from PyQt6.QtWidgets import QComboBox
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QSpinBox, QMessageBox,
    QTabWidget, QWidget, QColorDialog, QGroupBox
)

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class SettingsDialog(QDialog):
    """پنجره تنظیمات کامل"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("⚙️ تنظیمات برنامه")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.resize(750, 650)
        self.init_ui()
        self.load_current_values()
    
    def init_ui(self):
        """ساخت رابط"""
        layout = QVBoxLayout()
        
        # تبها
        tabs = QTabWidget()
        
        # تب اطلاعات موسسه
        general_tab = self.create_general_tab()
        tabs.addTab(general_tab, "🏢 اطلاعات موسسه")
        
        # تب فایلها
        files_tab = self.create_files_tab()
        tabs.addTab(files_tab, "📁 فایلها")
        
        # تب ضرایب کای (جدید - 6 ضریب)
        coefficients_tab = self.create_coefficients_tab()
        tabs.addTab(coefficients_tab, "🔢 ضرایب کای")
        
        # تب رنگها
        colors_tab = self.create_colors_tab()
        tabs.addTab(colors_tab, "🎨 رنگها")
        
        # تب ظاهر
        appearance_tab = self.create_appearance_tab()
        tabs.addTab(appearance_tab, "✨ ظاهر")
        
        layout.addWidget(tabs)
        
        # دکمههای پایین
        buttons = QHBoxLayout()
        btn_save = QPushButton("💾 ذخیره تمام تنظیمات")
        btn_save.clicked.connect(self.save_all_settings)
        btn_save.setStyleSheet("background-color: #4caf50; color: white; font-weight: bold; padding: 12px;")
        buttons.addWidget(btn_save)
        
        btn_cancel = QPushButton("❌ انصراف")
        btn_cancel.clicked.connect(self.close)
        buttons.addWidget(btn_cancel)
        
        layout.addLayout(buttons)
        self.setLayout(layout)
    
    def create_general_tab(self):
        """تب اطلاعات موسسه"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # نام موسسه
        layout.addWidget(QLabel("🏢 نام موسسه:"))
        self.company_input = QLineEdit()
        self.company_input.setPlaceholderText("مثال: سونوگرافی تابش")
        layout.addWidget(self.company_input)
        
        # آدرس
        layout.addWidget(QLabel("📍 آدرس:"))
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("مثال: شیراز، خیابان مدرس")
        layout.addWidget(self.address_input)
        
        # تلفن
        layout.addWidget(QLabel("📞 تلفن تماس:"))
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("مثال: 07132655")
        layout.addWidget(self.phone_input)
        
        # نام پزشک
        layout.addWidget(QLabel("👨‍⚕️ نام پزشک:"))
        self.doctor_input = QLineEdit()
        self.doctor_input.setPlaceholderText("مثال: دکتر احمدی")
        layout.addWidget(self.doctor_input)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_files_tab(self):
        """تب فایلها"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # فایل اکسل
        layout.addWidget(QLabel("📊 فایل اکسل تعرفهها (all.xlsx):"))
        excel_row = QHBoxLayout()
        self.excel_input = QLineEdit()
        self.excel_input.setReadOnly(True)
        excel_row.addWidget(self.excel_input)
        
        btn_excel = QPushButton("📂 انتخاب")
        btn_excel.clicked.connect(self.select_excel)
        excel_row.addWidget(btn_excel)
        layout.addLayout(excel_row)
        
        # لوگو
        layout.addWidget(QLabel("🖼️ لوگو (اختیاری):"))
        logo_row = QHBoxLayout()
        self.logo_input = QLineEdit()
        self.logo_input.setReadOnly(True)
        self.logo_input.setPlaceholderText("لوگویی انتخاب نشده")
        logo_row.addWidget(self.logo_input)
        
        btn_logo = QPushButton("🖼️ انتخاب")
        btn_logo.clicked.connect(self.select_logo)
        logo_row.addWidget(btn_logo)
        
        btn_clear_logo = QPushButton("🗑️ حذف")
        btn_clear_logo.clicked.connect(lambda: self.logo_input.clear())
        logo_row.addWidget(btn_clear_logo)
        layout.addLayout(logo_row)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_coefficients_tab(self):
        """تب ضرایب کای - نسخه جدید با 6 ضریب"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # راهنمای بالا
        info = QLabel("💡 این ضرایب برای محاسبه خودکار هزینه خدمات استفاده می‌شوند")
        info.setWordWrap(True)
        info.setStyleSheet("background-color: #e3f2fd; padding: 10px; border-radius: 5px;")
        layout.addWidget(info)
        
        # گروه کایهای خدمات # دار
        group_hash = QGroupBox("🔵 ضرایب کای برای خدمات # دار")
        group_hash_layout = QVBoxLayout()
        
        # کای حرفه‌ای # دار
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("کای حرفه‌ای # دار:"))
        self.kai_prof_hash = QSpinBox()
        self.kai_prof_hash.setRange(0, 100000000)
        self.kai_prof_hash.setSingleStep(1000)
        self.kai_prof_hash.setSuffix(" ریال")
        self.kai_prof_hash.setMinimumWidth(200)
        row1.addWidget(self.kai_prof_hash)
        row1.addStretch()
        group_hash_layout.addLayout(row1)
        
        # کای فنی # دار
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("کای فنی # دار:"))
        self.kai_tech_hash = QSpinBox()
        self.kai_tech_hash.setRange(0, 100000000)
        self.kai_tech_hash.setSingleStep(1000)
        self.kai_tech_hash.setSuffix(" ریال")
        self.kai_tech_hash.setMinimumWidth(200)
        row2.addWidget(self.kai_tech_hash)
        row2.addStretch()
        group_hash_layout.addLayout(row2)
        
        group_hash.setLayout(group_hash_layout)
        layout.addWidget(group_hash)
        
        # گروه کایهای خدمات بدون # (جراحی)
        group_no_hash = QGroupBox("🟠 ضرایب کای برای خدمات بدون # (جراحی)")
        group_no_hash_layout = QVBoxLayout()
        
        # کای حرفه‌ای بدون #
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("کای حرفه‌ای بدون #:"))
        self.kai_prof_no_hash = QSpinBox()
        self.kai_prof_no_hash.setRange(0, 100000000)
        self.kai_prof_no_hash.setSingleStep(1000)
        self.kai_prof_no_hash.setSuffix(" ریال")
        self.kai_prof_no_hash.setMinimumWidth(200)
        row3.addWidget(self.kai_prof_no_hash)
        row3.addStretch()
        group_no_hash_layout.addLayout(row3)
        
        # کای فنی بدون #
        row4 = QHBoxLayout()
        row4.addWidget(QLabel("کای فنی بدون #:"))
        self.kai_tech_no_hash = QSpinBox()
        self.kai_tech_no_hash.setRange(0, 100000000)
        self.kai_tech_no_hash.setSingleStep(1000)
        self.kai_tech_no_hash.setSuffix(" ریال")
        self.kai_tech_no_hash.setMinimumWidth(200)
        row4.addWidget(self.kai_tech_no_hash)
        row4.addStretch()
        group_no_hash_layout.addLayout(row4)
        
        group_no_hash.setLayout(group_no_hash_layout)
        layout.addWidget(group_no_hash)
        
        # گروه کایهای دولتی
        group_gov = QGroupBox("🟢 ضرایب کای دولتی (برای هر دو نوع)")
        group_gov_layout = QVBoxLayout()
        
        # کای حرفه‌ای دولتی
        row5 = QHBoxLayout()
        row5.addWidget(QLabel("کای حرفه‌ای دولتی:"))
        self.kai_prof_gov = QSpinBox()
        self.kai_prof_gov.setRange(0, 100000000)
        self.kai_prof_gov.setSingleStep(1000)
        self.kai_prof_gov.setSuffix(" ریال")
        self.kai_prof_gov.setMinimumWidth(200)
        row5.addWidget(self.kai_prof_gov)
        row5.addStretch()
        group_gov_layout.addLayout(row5)
        
        # کای فنی دولتی
        row6 = QHBoxLayout()
        row6.addWidget(QLabel("کای فنی دولتی:"))
        self.kai_tech_gov = QSpinBox()
        self.kai_tech_gov.setRange(0, 100000000)
        self.kai_tech_gov.setSingleStep(1000)
        self.kai_tech_gov.setSuffix(" ریال")
        self.kai_tech_gov.setMinimumWidth(200)
        row6.addWidget(self.kai_tech_gov)
        row6.addStretch()
        group_gov_layout.addLayout(row6)
        
        group_gov.setLayout(group_gov_layout)
        layout.addWidget(group_gov)
        
        # راهنمای فرمول‌ها
        formulas = QLabel(
            "📐 فرمول‌های محاسبه:\n\n"
            "• خصوصی آزاد = (کای حرفه‌ای × ضریب حرفه‌ای) + (کای فنی × ضریب فنی)\n"
            "• دولتی = (کای حرفه‌ای دولتی × ضریب حرفه‌ای) + (کای فنی دولتی × ضریب فنی)\n"
            "• سهم سازمان = (دولتی × 70%)\n"
            "• بیمه شده = خصوصی آزاد - سهم سازمان"
        )
        formulas.setWordWrap(True)
        formulas.setStyleSheet(
            "background-color: #fff9e6; padding: 15px; "
            "border-radius: 5px; border: 1px solid #ffc107;"
        )
        layout.addWidget(formulas)
        
        # دکمه بازنشانی به پیشفرض
        btn_reset_kai = QPushButton("🔄 بازنشانی به مقادیر پیشفرض")
        btn_reset_kai.clicked.connect(self.reset_coefficients_to_default)
        layout.addWidget(btn_reset_kai)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_colors_tab(self):
        """تب رنگها"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        info = QLabel("🎨 رنگهای رابط کاربری را سفارشی کنید")
        info.setStyleSheet("background-color: #fff3cd; padding: 10px; border-radius: 5px;")
        layout.addWidget(info)
        
        # رنگ پس‌زمینه
        row1 = self.create_color_row("پس‌زمینه", "background")
        layout.addLayout(row1)
        
        # رنگ متن
        row2 = self.create_color_row("متن", "text")
        layout.addLayout(row2)
        
        # رنگ دکمه
        row3 = self.create_color_row("دکمه‌ها", "button")
        layout.addLayout(row3)
        
        # رنگ هدر جدول
        row4 = self.create_color_row("هدر جدول", "table_header")
        layout.addLayout(row4)
        
        # دکمه بازنشانی
        btn_reset_colors = QPushButton("🔄 بازنشانی به رنگهای پیشفرض")
        btn_reset_colors.clicked.connect(self.reset_colors_to_default)
        layout.addWidget(btn_reset_colors)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_color_row(self, label, key):
        """ساخت ردیف انتخاب رنگ"""
        row = QHBoxLayout()
        row.addWidget(QLabel(f"{label}:"))
        
        color_input = QLineEdit()
        color_input.setReadOnly(True)
        color_input.setPlaceholderText("#000000")
        setattr(self, f"color_{key}", color_input)
        row.addWidget(color_input)
        
        btn = QPushButton("🎨 انتخاب رنگ")
        btn.clicked.connect(lambda: self.select_color(key))
        row.addWidget(btn)
        
        return row
    
    def create_appearance_tab(self):
        """تب ظاهر"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # اندازه فونت
        layout.addWidget(QLabel("🔤 اندازه فونت:"))
        font_row = QHBoxLayout()
        self.font_spin = QSpinBox()
        self.font_spin.setRange(8, 16)
        self.font_spin.setSuffix(" pt")
        font_row.addWidget(self.font_spin)
        font_row.addStretch()
        layout.addLayout(font_row)
        
        # راهنما
        info = QLabel(
            "💡 نکته: تغییرات ظاهری ممکن است نیاز به راه‌اندازی مجدد برنامه داشته باشد."
        )
        info.setWordWrap(True)
        info.setStyleSheet("background-color: #fff3cd; padding: 10px; border-radius: 5px;")
        layout.addWidget(info)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def load_current_values(self):
        """بارگذاری مقادیر فعلی"""
        try:
            # اطلاعات موسسه
            self.company_input.setText(self.parent.company_name)
            self.address_input.setText(self.parent.address)
            self.phone_input.setText(self.parent.phone)
            self.doctor_input.setText(self.parent.doctor_name)
            
            # فایلها
            self.excel_input.setText(self.parent.excel_path)
            self.logo_input.setText(self.parent.logo_path)
            
            # ضرایب کای
            self.load_coefficients()
            
            # رنگها
            self.load_colors()
            
            # ظاهر
            self.font_spin.setValue(self.parent.font_size)
            
        except Exception as e:
            print(f"خطا در بارگذاری مقادیر: {e}")
    
    def load_coefficients(self):
        """بارگذاری ضرایب کای - نسخه جدید با 6 ضریب"""
        try:
            from calculator import PriceCalculator
            coefficients = PriceCalculator.load_coefficients_from_file()
            
            # بارگذاری 6 ضریب جدید
            self.kai_prof_hash.setValue(int(coefficients.get('کای حرفه‌ای # دار', 568000)))
            self.kai_tech_hash.setValue(int(coefficients.get('کای فنی # دار', 1777000)))
            self.kai_prof_no_hash.setValue(int(coefficients.get('کای حرفه‌ای بدون #', 1011000)))
            self.kai_tech_no_hash.setValue(int(coefficients.get('کای فنی بدون #', 2843000)))
            self.kai_prof_gov.setValue(int(coefficients.get('کای حرفه‌ای دولتی', 302000)))
            self.kai_tech_gov.setValue(int(coefficients.get('کای فنی دولتی', 428000)))
            
        except Exception as e:
            print(f"خطا در بارگذاری ضرایب: {e}")
            # مقادیر پیشفرض
            self.kai_prof_hash.setValue(568000)
            self.kai_tech_hash.setValue(1777000)
            self.kai_prof_no_hash.setValue(1011000)
            self.kai_tech_no_hash.setValue(2843000)
            self.kai_prof_gov.setValue(302000)
            self.kai_tech_gov.setValue(428000)
    
    def load_colors(self):
        """بارگذاری رنگها"""
        try:
            if os.path.exists('color_settings.json'):
                with open('color_settings.json', 'r') as f:
                    colors = json.load(f)
            else:
                colors = {
                    'background': '#f5f7fa',
                    'text': '#2c3e50',
                    'button': '#00b4d8',
                    'table_header': '#0077b6'
                }
            
            self.color_background.setText(colors.get('background', '#f5f7fa'))
            self.color_text.setText(colors.get('text', '#2c3e50'))
            self.color_button.setText(colors.get('button', '#00b4d8'))
            self.color_table_header.setText(colors.get('table_header', '#0077b6'))
            
            # تنظیم رنگ پس‌زمینه فیلدها
            for key in ['background', 'text', 'button', 'table_header']:
                input_field = getattr(self, f"color_{key}")
                input_field.setStyleSheet(f"background-color: {input_field.text()}; color: white;")
                
        except Exception as e:
            print(f"خطا در بارگذاری رنگها: {e}")
    
    def select_excel(self):
        """انتخاب فایل اکسل"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "انتخاب فایل اکسل", "", "Excel Files (*.xlsx *.xls)"
        )
        if filename:
            self.excel_input.setText(filename)
    
    def select_logo(self):
        """انتخاب لوگو"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "انتخاب لوگو", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if filename:
            self.logo_input.setText(filename)
    
    def select_color(self, key):
        """انتخاب رنگ"""
        current_color = getattr(self, f"color_{key}").text() or "#000000"
        color = QColorDialog.getColor(QColor(current_color), self, "انتخاب رنگ")
        
        if color.isValid():
            color_hex = color.name()
            input_field = getattr(self, f"color_{key}")
            input_field.setText(color_hex)
            input_field.setStyleSheet(f"background-color: {color_hex}; color: white;")
    
    def reset_coefficients_to_default(self):
        """بازنشانی ضرایب به پیشفرض - نسخه جدید"""
        reply = QMessageBox.question(
            self, "تایید",
            "آیا می‌خواهید ضرایب کای را به مقادیر پیشفرض بازنشانی کنید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # مقادیر پیشفرض جدید
            self.kai_prof_hash.setValue(568000)
            self.kai_tech_hash.setValue(1777000)
            self.kai_prof_no_hash.setValue(1011000)
            self.kai_tech_no_hash.setValue(2843000)
            self.kai_prof_gov.setValue(302000)
            self.kai_tech_gov.setValue(428000)
    
    def reset_colors_to_default(self):
        """بازنشانی رنگها به پیشفرض"""
        reply = QMessageBox.question(
            self, "تایید",
            "آیا می‌خواهید رنگها را به حالت پیشفرض بازنشانی کنید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.color_background.setText('#f5f7fa')
            self.color_text.setText('#2c3e50')
            self.color_button.setText('#00b4d8')
            self.color_table_header.setText('#0077b6')
            self.load_colors()
    
    def save_all_settings(self):
        """ذخیره تمام تنظیمات - نسخه جدید"""
        try:
            # ذخیره اطلاعات موسسه
            self.parent.apply_settings(
                excel_path=self.excel_input.text() or None,
                logo=self.logo_input.text() or None,
                company=self.company_input.text() or None,
                address=self.address_input.text() or None,
                phone=self.phone_input.text() or None,
                doctor=self.doctor_input.text() or None,
                font_size=self.font_spin.value()
            )
            
            # ذخیره ضرایب کای جدید (6 ضریب)
            coefficients = {
                'کای حرفه‌ای # دار': self.kai_prof_hash.value(),
                'کای فنی # دار': self.kai_tech_hash.value(),
                'کای حرفه‌ای بدون #': self.kai_prof_no_hash.value(),
                'کای فنی بدون #': self.kai_tech_no_hash.value(),
                'کای حرفه‌ای دولتی': self.kai_prof_gov.value(),
                'کای فنی دولتی': self.kai_tech_gov.value()
            }
            
            with open('coefficients.json', 'w', encoding='utf-8') as f:
                json.dump(coefficients, f, ensure_ascii=False, indent=2)
            
            # بارگذاری مجدد ماژول محاسبه
            from calculator import PriceCalculator
            self.parent.calculator = PriceCalculator(coefficients)
            
            # ذخیره رنگها
            colors = {
                'background': self.color_background.text(),
                'text': self.color_text.text(),
                'button': self.color_button.text(),
                'table_header': self.color_table_header.text()
            }
            
            with open('color_settings.json', 'w', encoding='utf-8') as f:
                json.dump(colors, f, ensure_ascii=False, indent=2)
            
            # اعمال رنگها
            self.parent.apply_colors()
            
            QMessageBox.information(self, "موفق", "✅ تمام تنظیمات با موفقیت ذخیره شد")
            self.close()
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"❌ خطا در ذخیره تنظیمات:\n{str(e)}")
