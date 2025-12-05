"""
پنجره اصلی برنامه - نسخه جدید برای all.xlsx
با قابلیت ذخیره و بارگذاری مسیر فایل اکسل + بیحسی موضعی + هزینه متفرقه + سوابق بیماران + جستجوی نام
"""

import os
import pandas as pd
import jdatetime
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton,
    QMessageBox, QListWidgetItem, QComboBox, QLineEdit, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QSpinBox, QScrollArea, QFrame,
    QCheckBox
)
from PyQt6.QtGui import QFont, QColor, QShortcut, QKeySequence
from PyQt6.QtCore import Qt

from ui_settings import SettingsDialog
from utils import resource_path
from invoice import generate_invoice, direct_print
from utils import int_from_string
from features import FeatureManager
from history import HistoryDialog
from shortcuts import ShortcutManager
from category_filter import CategoryFilter
from calculator import PriceCalculator

# ⭐ Import ماژولهای سوابق بیمار + جستجو
try:
    from patient_records import PatientRecordsManager
    from ui_patient_history import PatientHistoryDialog
    from ui_patient_search import PatientSearchDialog
    PATIENT_RECORDS_AVAILABLE = True
except ImportError:
    PATIENT_RECORDS_AVAILABLE = False
    print("⚠️ ماژول سوابق بیماران یافت نشد. لطفاً patient_records.py، ui_patient_history.py و ui_patient_search.py را ایجاد کنید.")


def normalize_text(txt):
    """نرمالسازی متن فارسی"""
    return txt.replace("ي", "ی").replace("ك", "ک").strip().lower()


class InsuranceApp(QWidget):
    """برنامه اصلی تعرفه و فاکتور"""

    def __init__(self, excel_path="all.xlsx"):
        super().__init__()
        self.setWindowTitle("💊 نرمافزار تعرفه و فاکتور درمانی Pro")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.resize(1100, 800)

        # مسیر فایل اکسل
        self.excel_path = excel_path
        self.logo_path = ""

        # تنظیمات پیشفرض
        self.company_name = "سونوگرافی تابش"
        self.address = "شیراز، خیابان مدرس، بالاتر از چهارراه پلنگی"
        self.phone = "07132655"
        self.doctor_name = "شهرسواری رضا"
        self.font_size = 10
        self.setFont(QFont("Vazirmatn", self.font_size))

        # بارگذاری تنظیمات از فایل
        self.load_settings()

        # ماژولها
        self.features = FeatureManager(self)
        self.category_filter = CategoryFilter()
        self.current_category = "همه"
        self.category_buttons = {}

        # ماژول محاسبه با ضرایب جدید
        coefficients = PriceCalculator.load_coefficients_from_file()
        self.calculator = PriceCalculator(coefficients)

        # دیکشنری نگهداری کد -> خدمت
        self.service_codes = {}

        # بارگذاری داده
        self.load_excel()

        # ساخت رابط
        self.init_ui()

        # میانبرها
        self.shortcuts = ShortcutManager(self)

        # ⭐ مدیریت سوابق بیماران
        if PATIENT_RECORDS_AVAILABLE:
            self.patient_records = PatientRecordsManager()
            # میانبر Ctrl+F برای جستجو
            QShortcut(QKeySequence("Ctrl+F"), self, self.open_patient_search)
        else:
            self.patient_records = None

        # تم
        self.apply_colors()

    def load_settings(self):
        """بارگذاری تنظیمات از فایل JSON"""
        try:
            if os.path.exists('app_settings.json'):
                with open('app_settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.company_name = settings.get('company_name', self.company_name)
                    self.address = settings.get('address', self.address)
                    self.phone = settings.get('phone', self.phone)
                    self.doctor_name = settings.get('doctor_name', self.doctor_name)
                    self.logo_path = settings.get('logo_path', self.logo_path)
                    self.font_size = settings.get('font_size', self.font_size)
                    self.excel_path = settings.get('excel_path', self.excel_path)
        except Exception as e:
            print(f"خطا در بارگذاری تنظیمات: {e}")

    def save_settings(self):
        """ذخیره تنظیمات در فایل JSON"""
        try:
            settings = {
                'company_name': self.company_name,
                'address': self.address,
                'phone': self.phone,
                'doctor_name': self.doctor_name,
                'logo_path': self.logo_path,
                'font_size': self.font_size,
                'excel_path': self.excel_path
            }
            with open('app_settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"خطا در ذخیره تنظیمات: {e}")

    def init_ui(self):
        """ساخت رابط کاربری"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # نوار بالا
        top = self.create_toolbar()
        layout.addLayout(top)

        # فیلتر دستهبندی
        category_section = self.create_category_filter()
        layout.addWidget(category_section)

        # لیست خدمات
        self.service_list = self.create_service_list()
        layout.addWidget(self.service_list)

        # نوع تعرفه + بیحسی موضعی
        tariff_row = self.create_tariff_row()
        layout.addLayout(tariff_row)

        # هزینه متفرقه
        misc_row = self.create_misc_row()
        layout.addLayout(misc_row)

        # جدول خدمات
        self.table = self.create_table()
        layout.addWidget(self.table)

        # دکمه حذف
        btn_del = QPushButton("❌ حذف خدمت (Delete)")
        btn_del.clicked.connect(self.remove_selected)
        layout.addWidget(btn_del)

        # تخفیف
        discount_row = self.create_discount_row()
        layout.addLayout(discount_row)

        # اطلاعات بیمار
        info_row = self.create_info_row()
        layout.addLayout(info_row)

        # دکمههای اصلی
        buttons_row = self.create_main_buttons()
        layout.addLayout(buttons_row)

        # نتیجه
        self.result = QLabel("")
        self.result.setStyleSheet(
            "font-size: 12px; font-weight: bold; padding: 8px; "
            "background-color: #e8f4f8; border-radius: 6px;"
        )
        layout.addWidget(self.result)

        self.setLayout(layout)

    def create_toolbar(self):
        """ساخت نوار ابزار"""
        top = QHBoxLayout()
        top.setContentsMargins(10, 10, 10, 0)

        self.stats_label = QLabel(f"📊 فاکتورهای امروز: {self.features.get_today_stats()}")
        self.stats_label.setStyleSheet("font-weight: bold; color: #0077b6; font-size: 12px;")
        top.addWidget(self.stats_label)

        top.addStretch()

        top.addWidget(QLabel("🔍"))
        self.search = QLineEdit()
        self.search.setPlaceholderText("جستجو با نام یا کد (مثلا: 701500)")
        self.search.textChanged.connect(self.filter_list)
        top.addWidget(self.search)

        # ⭐ دکمه جستجوی بیمار با نام
        if PATIENT_RECORDS_AVAILABLE:
            btn_patient_search = QPushButton("🔍 جستجو بیمار")
            btn_patient_search.setToolTip("جستجوی بیمار با نام یا نام خانوادگی (Ctrl+F)")
            btn_patient_search.clicked.connect(self.open_patient_search)
            btn_patient_search.setStyleSheet("background-color: #ff6b6b; color: white; font-weight: bold;")
            top.addWidget(btn_patient_search)

            btn_patient_history = QPushButton("🩺 سوابق")
            btn_patient_history.setToolTip("مشاهده سوابق بیمار فعلی")
            btn_patient_history.clicked.connect(lambda: self.show_patient_history())
            top.addWidget(btn_patient_history)

        # دکمه نسخه الکترونیک
        btn_prescription = QPushButton("📋 نسخه")
        btn_prescription.setToolTip("دریافت نسخه الکترونیک تامین")
        btn_prescription.clicked.connect(self.open_prescription_dialog)
        top.addWidget(btn_prescription)

        btn_history = QPushButton("📜 تاریخچه")
        btn_history.setToolTip("Ctrl+H")
        btn_history.clicked.connect(self.show_history)
        top.addWidget(btn_history)

        btn_backup = QPushButton("💾 پشتیبان")
        btn_backup.setToolTip("Ctrl+B")
        btn_backup.clicked.connect(self.create_backup)
        top.addWidget(btn_backup)

        btn_help = QPushButton("❓")
        btn_help.setToolTip("راهنما")
        btn_help.clicked.connect(self.show_help)
        top.addWidget(btn_help)

        btn_settings = QPushButton("⚙️")
        btn_settings.setToolTip("تنظیمات")
        btn_settings.clicked.connect(self.open_settings)
        top.addWidget(btn_settings)

        return top

    def create_category_filter(self):
        """ساخت فیلتر دستهبندی سریع"""
        container = QFrame()
        container.setMaximumHeight(85)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(5)

        label = QLabel("🗂️ دستهبندی سریع:")
        label.setStyleSheet("font-weight: bold; color: #0077b6; font-size: 12px;")
        layout.addWidget(label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(50)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scroll_widget = QWidget()
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(8)

        categories = self.category_filter.get_all_categories()
        for cat in categories:
            btn = QPushButton(cat)
            btn.setCheckable(True)
            btn.setMinimumWidth(120)
            btn.setMinimumHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 11px;
                    font-weight: 600;
                    padding: 8px 12px;
                    border-radius: 8px;
                }
            """)
            if cat == "همه":
                btn.setChecked(True)

            btn.clicked.connect(lambda checked, c=cat: self.filter_by_category(c))
            self.category_buttons[cat] = btn
            btn_layout.addWidget(btn)

        btn_layout.addStretch()
        scroll_widget.setLayout(btn_layout)
        scroll.setWidget(scroll_widget)

        layout.addWidget(scroll)
        container.setLayout(layout)
        return container

    def filter_by_category(self, category):
        """فیلتر کردن بر اساس دسته"""
        self.current_category = category
        for cat, btn in self.category_buttons.items():
            btn.setChecked(cat == category)
        self.apply_filters()

    def apply_filters(self):
        """اعمال فیلتر دستهبندی + جستجو با کد"""
        search_text = normalize_text(self.search.text())

        for i in range(1, self.service_list.count()):
            item = self.service_list.item(i)
            full_text = item.text()

            if " - " in full_text:
                service_name = full_text.split(" - ", 1)[1]
                service_code = full_text.split(" - ", 1)[0]
            else:
                service_name = full_text
                service_code = ""

            item_category = self.category_filter.categorize_service(full_text)
            category_match = (self.current_category == "همه" or item_category == self.current_category)

            search_match = (
                not search_text or
                search_text in normalize_text(service_name) or
                search_text in normalize_text(service_code)
            )

            item.setHidden(not (category_match and search_match))

    def filter_list(self, text):
        """جستجو با در نظر گرفتن دستهبندی"""
        self.apply_filters()

    def create_service_list(self):
        """ساخت لیست خدمات با کد"""
        service_list = QListWidget()
        service_list.setFont(QFont("Vazirmatn", self.font_size))
        service_list.setSpacing(0)
        service_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)

        self.header_item = QListWidgetItem("📋 لیست خدمات (Shift+Click = چندتایی)")
        self.header_item.setFlags(
            self.header_item.flags() & ~Qt.ItemFlag.ItemIsSelectable & ~Qt.ItemFlag.ItemIsEnabled
        )
        header_font = QFont("Vazirmatn", self.font_size + 2, QFont.Weight.Bold)
        self.header_item.setFont(header_font)
        service_list.addItem(self.header_item)

        for idx, row in self.df.iterrows():
            service_name = str(row[self.name_col])
            if not service_name or service_name == 'nan':
                continue

            service_code = str(row.get('کدملی', ''))
            if service_code and service_code != 'nan' and service_code != '':
                service_code = service_code.replace('.0', '').strip()
                display_text = f"{service_code} - {service_name}"
                self.service_codes[service_code] = service_name
            else:
                display_text = service_name

            service_list.addItem(QListWidgetItem(display_text))

        return service_list

    def create_tariff_row(self):
        """ساخت ردیف نوع تعرفه + بیحسی موضعی"""
        row = QHBoxLayout()
        row.setContentsMargins(10, 0, 10, 0)

        row.addWidget(QLabel("👤 نوع تعرفه:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["بیمهشده", "خصوصی آزاد", "دولتی"])
        row.addWidget(self.type_combo)

        # چکباکس بیحسی موضعی
        self.anesthesia_checkbox = QCheckBox("💉 بیحسی موضعی (+20%)")
        self.anesthesia_checkbox.setStyleSheet("font-weight: bold; color: #d32f2f;")
        self.anesthesia_checkbox.stateChanged.connect(self.calculate)
        row.addWidget(self.anesthesia_checkbox)

        btn_add = QPushButton("➕ افزودن")
        btn_add.clicked.connect(self.add_service)
        row.addWidget(btn_add)

        return row

    def create_misc_row(self):
        """ساخت ردیف هزینه متفرقه"""
        row = QHBoxLayout()
        row.setContentsMargins(10, 0, 10, 0)

        row.addWidget(QLabel("💰 هزینه متفرقه:"))

        # عنوان هزینه
        self.misc_title_input = QLineEdit()
        self.misc_title_input.setPlaceholderText("عنوان (مثلاً: هزینه اتاق)")
        self.misc_title_input.setMinimumWidth(200)
        row.addWidget(self.misc_title_input)

        row.addWidget(QLabel("مبلغ:"))

        # مبلغ هزینه
        self.misc_amount_spin = QSpinBox()
        self.misc_amount_spin.setRange(0, 100000000)
        self.misc_amount_spin.setSingleStep(10000)
        self.misc_amount_spin.setSuffix(" ریال")
        self.misc_amount_spin.setMinimumWidth(150)
        row.addWidget(self.misc_amount_spin)

        # دکمه افزودن
        btn_add_misc = QPushButton("➕ افزودن هزینه")
        btn_add_misc.clicked.connect(self.add_misc_cost)
        btn_add_misc.setStyleSheet("background-color: #ff9800;")
        row.addWidget(btn_add_misc)

        row.addStretch()
        return row

    def create_table(self):
        """ساخت جدول خدمات"""
        table = QTableWidget(0, 6)
        table.setHorizontalHeaderLabels(["شرح", "تعرفه", "کل", "سازمان", "بیمار", "توضیح"])
        table.setFont(QFont("Vazirmatn", self.font_size))
        table.setColumnWidth(0, 340)
        return table

    def create_discount_row(self):
        """ساخت ردیف تخفیف"""
        row = QHBoxLayout()
        row.setContentsMargins(10, 0, 10, 0)

        row.addWidget(QLabel("🏷️ تخفیف:"))

        self.discount_type = QComboBox()
        self.discount_type.addItems(["ریالی", "درصدی"])
        self.discount_type.currentTextChanged.connect(self.change_discount_type)
        self.discount_type.setMinimumWidth(100)
        row.addWidget(self.discount_type)

        self.discount_spin = QSpinBox()
        self.discount_spin.setRange(0, 100000000)
        self.discount_spin.setSingleStep(10000)
        self.discount_spin.setSuffix(" ریال")
        self.discount_spin.setMinimumWidth(180)
        self.discount_spin.valueChanged.connect(self.calculate)
        row.addWidget(self.discount_spin)

        row.addStretch()
        return row

    def change_discount_type(self, dtype):
        """تغییر نوع تخفیف"""
        if dtype == "درصدی":
            self.discount_spin.setRange(0, 100)
            self.discount_spin.setSingleStep(5)
            self.discount_spin.setSuffix(" %")
            self.discount_spin.setValue(0)
        else:
            self.discount_spin.setRange(0, 100000000)
            self.discount_spin.setSingleStep(10000)
            self.discount_spin.setSuffix(" ریال")
            self.discount_spin.setValue(0)
        self.calculate()

    def create_info_row(self):
        """ساخت ردیف اطلاعات بیمار"""
        row = QHBoxLayout()
        row.setContentsMargins(10, 0, 10, 0)

        # نام بیمار
        self.name_in = QLineEdit()
        self.name_in.setPlaceholderText("نام بیمار")
        
        # ⭐ اتصال به پیشنهاد بیمار با نام
        if PATIENT_RECORDS_AVAILABLE:
            self.name_in.textChanged.connect(self.suggest_patients_by_name)

        # کد ملی
        self.national_code_in = QLineEdit()
        self.national_code_in.setPlaceholderText("کد ملی")
        self.national_code_in.setMaxLength(10)
        self.national_code_in.setFixedWidth(120)

        # ⭐ اتصال به سیستم بررسی سوابق
        if PATIENT_RECORDS_AVAILABLE:
            self.national_code_in.textChanged.connect(self.check_patient_history)

        # کد پیگیری
        self.tracking_code_in = QLineEdit()
        self.tracking_code_in.setPlaceholderText("کد پیگیری نسخه")
        self.tracking_code_in.setMaxLength(20)
        self.tracking_code_in.setFixedWidth(150)

        # بیمه
        self.ins_in = QLineEdit("تامین اجتماعی")
        self.ins_in.setPlaceholderText("بیمه")

        # تاریخ
        self.date_in = QLineEdit(jdatetime.date.today().strftime("%Y/%m/%d"))

        # افزودن به ردیف
        row.addWidget(QLabel("👤"))
        row.addWidget(self.name_in)
        row.addWidget(QLabel("🆔"))
        row.addWidget(self.national_code_in)
        row.addWidget(QLabel("🔢"))
        row.addWidget(self.tracking_code_in)
        row.addWidget(QLabel("🏥"))
        row.addWidget(self.ins_in)
        row.addWidget(QLabel("📅"))
        row.addWidget(self.date_in)

        return row

    def create_main_buttons(self):
        """ساخت دکمههای اصلی"""
        row = QHBoxLayout()
        row.setContentsMargins(10, 0, 10, 10)

        btn_calc = QPushButton("🧮 محاسبه (F5)")
        btn_calc.clicked.connect(self.calculate)
        row.addWidget(btn_calc)

        btn_save = QPushButton("📄 ذخیره PDF (Ctrl+S)")
        btn_save.clicked.connect(self.save_invoice)
        row.addWidget(btn_save)

        btn_print = QPushButton("🖨️ چاپ (Ctrl+P)")
        btn_print.clicked.connect(self.print_invoice)
        row.addWidget(btn_print)

        btn_clear = QPushButton("🔄 پاک (Ctrl+N)")
        btn_clear.clicked.connect(self.clear_all)
        row.addWidget(btn_clear)

        return row

    # ============ متدهای عملیاتی ============

    def load_excel(self):
        """بارگذاری اکسل - نسخه جدید برای all.xlsx"""
        try:
            if not os.path.exists(self.excel_path):
                QMessageBox.critical(self, "خطا", f"فایل اکسل یافت نشد:\n{self.excel_path}")
                return

            df = pd.read_excel(self.excel_path)

            # تشخیص اینکه آیا فایل all.xlsx است یا ghardash.xlsx
            if 'Unnamed: 0' in df.columns:
                # فایل all.xlsx - نیاز به تنظیم هدرها
                df.columns = ['کدملی', 'ویژگی کد', 'شرح کد', 'توضیحات', 'کل', 'حرفهای', 'فنی', 'ارزش پایه بیهوشی']
                df = df.iloc[2:].reset_index(drop=True)  # حذف دو سطر اول
                df = df.dropna(subset=['کدملی'])
                self.name_col = 'شرح کد'
            else:
                # فایل ghardash.xlsx - ساختار قدیمی
                self.name_col = [c for c in df.columns if "شرح" in str(c)][0]

            self.df = df.fillna("")

        except Exception as e:
            QMessageBox.critical(self, "خطا در بارگذاری اکسل", f"❌ خطا:\n{str(e)}")

    def add_service(self):
        """افزودن خدمت - با احتساب بیحسی موضعی"""
        selected = self.service_list.selectedItems()
        if not selected:
            return

        for s in selected:
            full_text = s.text()
            if " - " in full_text:
                name = full_text.split(" - ", 1)[1]
            else:
                name = full_text

            row = self.df[self.df[self.name_col].astype(str) == name]
            if row.empty:
                continue

            # دریافت نوع خدمت و ضرایب
            service_type = str(row.iloc[0].get('ویژگی کد', ''))

            # تلاش برای دریافت مقادیر حرفهای و فنی
            prof_value = 0
            tech_value = 0
            try:
                prof_value = float(row.iloc[0].get('حرفهای', 0))
            except:
                pass
            try:
                tech_value = float(row.iloc[0].get('فنی', 0))
            except:
                pass

            # محاسبه قیمتها با calculator
            prices = self.calculator.calculate_service_price(service_type, prof_value, tech_value)

            # ⭐ اعمال بیحسی موضعی
            if self.anesthesia_checkbox.isChecked():
                # خصوصی آزاد جدید = خصوصی قدیمی × 1.20
                prices['private'] = int(prices['private'] * 1.20)
                # بیمه شده جدید = خصوصی جدید - سهم سازمان (سازمان ثابت)
                prices['insurance'] = prices['private'] - prices['organization']

            ttype = self.type_combo.currentText()
            if ttype == "خصوصی آزاد":
                total = prices['private']
                org = 0
                patient = total
            elif ttype == "دولتی":
                total = prices['government']
                org = 0
                patient = total
            else:  # بیمهشده
                total = prices['private']
                org = prices['organization']
                patient = prices['insurance']

            # افزودن به جدول
            r = self.table.rowCount()
            self.table.insertRow(r)
            for j, val in enumerate([name, ttype, str(int(total)), str(int(org)), str(int(patient)), ""]):
                self.table.setItem(r, j, QTableWidgetItem(val))

        self.calculate()

    def add_misc_cost(self):
        """افزودن هزینه متفرقه به جدول"""
        title = self.misc_title_input.text().strip()
        amount = self.misc_amount_spin.value()

        if not title:
            QMessageBox.warning(self, "خطا", "⚠️ لطفاً عنوان هزینه را وارد کنید!")
            return

        if amount <= 0:
            QMessageBox.warning(self, "خطا", "⚠️ لطفاً مبلغ را وارد کنید!")
            return

        # افزودن به جدول
        r = self.table.rowCount()
        self.table.insertRow(r)

        # شرح، تعرفه، کل، سازمان، بیمار، توضیح
        self.table.setItem(r, 0, QTableWidgetItem(f"💰 {title}"))
        self.table.setItem(r, 1, QTableWidgetItem("متفرقه"))
        self.table.setItem(r, 2, QTableWidgetItem(str(amount)))
        self.table.setItem(r, 3, QTableWidgetItem("0"))
        self.table.setItem(r, 4, QTableWidgetItem(str(amount)))
        self.table.setItem(r, 5, QTableWidgetItem(""))

        # پاک کردن فیلدها
        self.misc_title_input.clear()
        self.misc_amount_spin.setValue(0)

        # محاسبه مجدد
        self.calculate()

    def remove_selected(self):
        """حذف خدمت انتخاب شده"""
        r = self.table.currentRow()
        if r >= 0:
            self.table.removeRow(r)
            self.calculate()

    def calculate(self):
        """محاسبه مجموع - بیحسی در add_service اعمال شده"""
        total = org = patient = 0

        # جمع کل از جدول
        for i in range(self.table.rowCount()):
            total += int_from_string(self.table.item(i, 2).text())
            org += int_from_string(self.table.item(i, 3).text())
            patient += int_from_string(self.table.item(i, 4).text())

        # اعمال تخفیف
        discount_value = self.discount_spin.value()
        discount_type = self.discount_type.currentText()

        if discount_value > 0:
            final_total, discount_amount = self.features.calculate_discount(
                total, discount_value, discount_type
            )
            patient_after = max(0, patient - discount_amount)

            discount_text = f"{discount_value}%" if discount_type == "درصدی" else f"{discount_value:,} ریال"

            # نمایش
            anesthesia_status = " (+ بیحسی 20%)" if self.anesthesia_checkbox.isChecked() else ""
            self.result.setText(
                f"💰 جمع{anesthesia_status}: {total:,} | 🏷️ تخفیف ({discount_text}): -{discount_amount:,} | "
                f"✅ جمع نهایی: {final_total:,} | سازمان: {org:,} | بیمار: {patient_after:,} ریال"
            )
        else:
            # نمایش بدون تخفیف
            anesthesia_status = " (+ بیحسی 20%)" if self.anesthesia_checkbox.isChecked() else ""
            self.result.setText(f"💰 جمع کل{anesthesia_status}: {total:,} | سازمان: {org:,} | بیمار: {patient:,} ریال")

    # ⭐ ============ متدهای سوابق بیماران + جستجوی نام ============

    def suggest_patients_by_name(self):
        """نمایش پیام اگر بیماری با نام مشابه وجود دارد"""
        if not PATIENT_RECORDS_AVAILABLE or not self.patient_records:
            return
        
        name_text = self.name_in.text().strip()
        
        # فقط اگر بیشتر از 3 حرف تایپ شده و کدملی خالی است
        if len(name_text) >= 3 and not self.national_code_in.text().strip():
            results = self.patient_records.search_by_name(name_text)
            
            if results and len(results) > 0:
                # تغییر رنگ فیلد نام به نارنجی (هشدار)
                self.name_in.setStyleSheet("""
                    background-color: #fff3e0; 
                    border: 2px solid #ff9800; 
                    padding: 10px; 
                    border-radius: 8px;
                """)
            else:
                # بازگشت به حالت عادی
                self.name_in.setStyleSheet("")
        else:
            self.name_in.setStyleSheet("")

    def open_patient_search(self):
        """باز کردن پنجره جستجوی بیمار"""
        if not PATIENT_RECORDS_AVAILABLE or not self.patient_records:
            QMessageBox.warning(
                self,
                "خطا",
                "⚠️ ماژول سوابق بیماران یافت نشد!\n"
                "لطفاً فایلهای patient_records.py، ui_patient_history.py و ui_patient_search.py را ایجاد کنید."
            )
            return
        
        dialog = PatientSearchDialog(self, self.patient_records)
        dialog.patient_selected.connect(self.load_patient_data)
        dialog.exec()

    def load_patient_data(self, patient):
        """بارگذاری خودکار اطلاعات بیمار در فرم"""
        try:
            # پر کردن فیلدها
            self.name_in.setText(patient['name'])
            self.national_code_in.setText(patient['national_code'])
            self.ins_in.setText(patient['insurance'])
            
            # نمایش پیام موفقیت
            QMessageBox.information(
                self,
                "✅ بیمار بارگذاری شد",
                f"اطلاعات بیمار با موفقیت بارگذاری شد:\n\n"
                f"👤 نام: {patient['name']}\n"
                f"🆔 کد ملی: {patient['national_code']}\n"
                f"📊 تعداد مراجعات قبلی: {patient['total_invoices']}\n"
                f"📅 آخرین مراجعه: {patient['last_visit']}"
            )
            
        except Exception as e:
            QMessageBox.warning(self, "خطا", f"❌ خطا در بارگذاری اطلاعات:\n{str(e)}")

    def check_patient_history(self):
        """بررسی و نمایش خودکار سوابق بیمار هنگام وارد کردن کدملی"""
        if not PATIENT_RECORDS_AVAILABLE or not self.patient_records:
            return

        national_code = self.national_code_in.text().strip()

        # فقط وقتی کدملی 10 رقمی کامل شد
        if len(national_code) == 10 and national_code.isdigit():
            summary = self.patient_records.get_patient_summary(national_code)

            if summary:
                # پر کردن خودکار نام و بیمه
                if summary['name']:
                    self.name_in.setText(summary['name'])
                if summary['insurance']:
                    self.ins_in.setText(summary['insurance'])

                # نمایش پیام سوابق
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setWindowTitle("📋 سوابق بیمار")
                msg.setText(
                    f"✅ بیمار قبلاً مراجعه کرده است!\n\n"
                    f"👤 نام: {summary['name']}\n"
                    f"📊 تعداد مراجعات: {summary['total_invoices']}\n"
                    f"📅 آخرین مراجعه: {summary['last_visit']}\n"
                    f"💰 جمع پرداختی: {summary['total_amount']:,} ریال"
                )
                msg.setStandardButtons(
                    QMessageBox.StandardButton.Ok |
                    QMessageBox.StandardButton.Open
                )

                btn_ok = msg.button(QMessageBox.StandardButton.Ok)
                btn_ok.setText("✅ متوجه شدم")

                btn_open = msg.button(QMessageBox.StandardButton.Open)
                btn_open.setText("📋 مشاهده سوابق کامل")

                result = msg.exec()

                # اگر دکمه مشاهده سوابق زده شد
                if result == QMessageBox.StandardButton.Open:
                    self.show_patient_history(national_code)

    def show_patient_history(self, national_code=None):
        """نمایش سوابق کامل بیمار"""
        if not PATIENT_RECORDS_AVAILABLE or not self.patient_records:
            QMessageBox.warning(
                self,
                "خطا",
                "⚠️ ماژول سوابق بیماران یافت نشد!\n"
                "لطفاً فایلهای patient_records.py و ui_patient_history.py را ایجاد کنید."
            )
            return

        if not national_code:
            national_code = self.national_code_in.text().strip()

        if not national_code:
            QMessageBox.warning(self, "خطا", "⚠️ لطفاً کدملی را وارد کنید!")
            return

        summary = self.patient_records.get_patient_summary(national_code)

        if not summary:
            QMessageBox.information(
                self,
                "سوابق",
                "📋 این بیمار سابقه مراجعه ندارد."
            )
            return

        dialog = PatientHistoryDialog(self, summary)
        dialog.exec()

    # ⭐ ============ ذخیره فاکتور با ثبت سوابق ============

    def save_invoice(self):
        """ذخیره فاکتور + ثبت در سوابق بیمار"""
        path = generate_invoice(self)

        if path:
            # محاسبه مقادیر
            total = org = patient = 0
            services_list = []

            for i in range(self.table.rowCount()):
                service_name = self.table.item(i, 0).text()
                tariff_type = self.table.item(i, 1).text()
                cost = int(self.table.item(i, 2).text().replace(',', ''))

                total += cost
                org += int(self.table.item(i, 3).text().replace(',', ''))
                patient += int(self.table.item(i, 4).text().replace(',', ''))

                services_list.append({
                    'name': service_name,
                    'tariff': tariff_type,
                    'cost': cost
                })

            # اعمال تخفیف
            discount_value = self.discount_spin.value()
            discount_type = self.discount_type.currentText()
            discount_amount = 0

            if discount_value > 0:
                if discount_type == "درصدی":
                    discount_amount = int(total * discount_value / 100)
                else:
                    discount_amount = discount_value

                patient = max(0, patient - discount_amount)
                total = max(0, total - discount_amount)

            # ⭐ ثبت در سوابق بیمار
            national_code = self.national_code_in.text().strip()

            if national_code and PATIENT_RECORDS_AVAILABLE and self.patient_records:
                patient_data = {
                    'name': self.name_in.text().strip(),
                    'insurance': self.ins_in.text().strip(),
                    'tracking_code': self.tracking_code_in.text().strip(),
                    'services': services_list,
                    'total': total,
                    'organization': org,
                    'patient_pay': patient,
                    'discount': discount_amount,
                    'tariff_type': self.type_combo.currentText(),
                    'pdf_path': path
                }

                if self.patient_records.add_record(national_code, patient_data):
                    print(f"✅ سوابق بیمار {national_code} ذخیره شد")

            # ذخیره در تاریخچه (کد قبلی)
            name_part = self.name_in.text().strip() or "بیمار"
            national_part = national_code or ""
            tracking_part = self.tracking_code_in.text().strip() or ""

            filename_parts = [name_part]
            if national_part:
                filename_parts.append(national_part)
            if tracking_part:
                filename_parts.append(tracking_part)

            filename = "_".join(filename_parts)
            self.features.save_to_history(path, filename)
            self.stats_label.setText(f"📊 فاکتورهای امروز: {self.features.get_today_stats()}")

    def print_invoice(self):
        """چاپ فاکتور + ذخیره سوابق"""
        # ابتدا ذخیره کن (که سوابق هم ثبت بشه)
        self.save_invoice()
        # بعد چاپ کن
        direct_print(self)

    def clear_all(self):
        """پاک کردن همه"""
        self.table.setRowCount(0)
        self.result.clear()
        self.search.clear()
        self.discount_spin.setValue(0)
        self.discount_type.setCurrentText("ریالی")
        self.anesthesia_checkbox.setChecked(False)
        self.misc_title_input.clear()
        self.misc_amount_spin.setValue(0)
        
        # بازگردانی استایل نرمال به فیلد نام
        self.name_in.setStyleSheet("")

    def show_history(self):
        """نمایش تاریخچه"""
        HistoryDialog(self).exec()

    def create_backup(self):
        """ایجاد پشتیبان"""
        self.features.create_backup()

    def open_prescription_dialog(self):
        """باز کردن پنجره نسخه الکترونیک"""
        try:
            import selenium
            import webdriver_manager
            from ui_prescription import PrescriptionDialog

            dialog = PrescriptionDialog(self)
            dialog.exec()

        except ImportError as e:
            QMessageBox.warning(
                self,
                "ماژول نسخه الکترونیک یافت نشد",
                "⚠️ برای استفاده از قابلیت دریافت نسخه الکترونیک، "
                "ابتدا باید کتابخانههای زیر را نصب کنید:\n\n"
                "در ترمینال اجرا کنید:\n"
                "pip install selenium webdriver-manager\n\n"
                f"خطا: {str(e)}"
            )
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"❌ خطا در باز کردن پنجره:\n{str(e)}")

    def show_help(self):
        """نمایش راهنما"""
        help_text = ShortcutManager.get_shortcuts_help()
        help_text += "\n\n💡 نکته: میتوانید با کد خدمت جستجو کنید"
        help_text += "\n\n💉 بیحسی موضعی: 20% به خصوصی آزاد اضافه میشود"
        help_text += "\n\n💰 هزینه متفرقه: برای افزودن هزینههای اضافی مانند اتاق، ویزیت و..."
        help_text += "\n\n📋 نسخه الکترونیک: برای دریافت نسخه از سایت تامین، روی 'نسخه' کلیک کنید"
        help_text += "\n\n🔍 جستجوی بیمار: با Ctrl+F یا دکمه 'جستجو بیمار'"
        help_text += "\n\n🩺 سوابق بیماران: با وارد کردن کدملی یا نام، سوابق خودکار نمایش داده می‌شود"
        help_text += "\n\n⚠️ هشدار نام مشابه: اگر نامی مشابه باشد، فیلد نام نارنجی می‌شود"

        QMessageBox.information(self, "راهنما", help_text)

    def open_settings(self):
        """باز کردن تنظیمات"""
        SettingsDialog(self).exec()

    def apply_settings(self, excel_path=None, logo=None, company=None, address=None, phone=None, doctor=None, font_size=None):
        """اعمال تنظیمات"""
        try:
            if excel_path and os.path.exists(excel_path):
                self.excel_path = excel_path
                self.load_excel()

                # بازسازی لیست خدمات
                self.service_list.clear()
                self.header_item = QListWidgetItem("📋 لیست خدمات (Shift+Click = چندتایی)")
                self.header_item.setFlags(
                    self.header_item.flags() & ~Qt.ItemFlag.ItemIsSelectable & ~Qt.ItemFlag.ItemIsEnabled
                )
                header_font = QFont("Vazirmatn", self.font_size + 2, QFont.Weight.Bold)
                self.header_item.setFont(header_font)
                self.service_list.addItem(self.header_item)

                self.service_codes.clear()
                for idx, row in self.df.iterrows():
                    service_name = str(row[self.name_col])
                    if not service_name or service_name == 'nan':
                        continue

                    service_code = str(row.get('کدملی', ''))
                    if service_code and service_code != 'nan' and service_code != '':
                        service_code = service_code.replace('.0', '').strip()
                        display_text = f"{service_code} - {service_name}"
                        self.service_codes[service_code] = service_name
                    else:
                        display_text = service_name

                    self.service_list.addItem(QListWidgetItem(display_text))

                self.apply_colors()

            if logo:
                self.logo_path = logo
            if company:
                self.company_name = company
            if address:
                self.address = address
            if phone:
                self.phone = phone
            if doctor:
                self.doctor_name = doctor

            if font_size:
                self.font_size = font_size
                self.setFont(QFont("Vazirmatn", font_size))
                self.table.setFont(QFont("Vazirmatn", font_size))
                self.service_list.setFont(QFont("Vazirmatn", font_size))

            # ذخیره تنظیمات بعد از تغییرات
            self.save_settings()

            # بارگذاری مجدد calculator
            coefficients = PriceCalculator.load_coefficients_from_file()
            self.calculator = PriceCalculator(coefficients)

        except Exception as e:
            QMessageBox.critical(self, "خطا", f"❌ خطا در اعمال تنظیمات:\n{str(e)}")

    def apply_colors(self):
        """اعمال رنگها"""
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

            self.header_item.setBackground(QColor(colors['table_header']))
            self.header_item.setForeground(QColor("#ffffff"))

            self.setStyleSheet(f"""
                QWidget {{background-color: {colors['background']}; color: {colors['text']};}}
                QLineEdit {{background-color: #fff; border: 2px solid #e0e6ed; padding: 10px; border-radius: 8px;}}
                QLineEdit:focus {{border: 2px solid {colors['button']};}}
                QPushButton {{
                    background-color: {colors['button']};
                    color: white;
                    padding: 11px 20px;
                    border-radius: 8px;
                    font-weight: 600;
                    font-size: 11px;
                }}
                QPushButton:hover {{background-color: #48cae4;}}
                QPushButton:checked {{
                    background-color: #0096c7;
                    font-weight: bold;
                    border: 3px solid #023e8a;
                }}
                QComboBox, QSpinBox {{background-color: #fff; border: 2px solid #e0e6ed; padding: 8px; border-radius: 8px;}}
                QCheckBox {{font-size: 11px; padding: 8px;}}
                QListWidget {{background-color: #fff; border: 2px solid #e0e6ed; border-radius: 10px; padding: 0;}}
                QListWidget::item {{padding: 12px;}}
                QListWidget::item:selected {{background-color: {colors['button']}; color: white; border-radius: 6px;}}
                QTableWidget {{background-color: #fff; border: 2px solid #e0e6ed; border-radius: 10px;}}
                QTableWidget QHeaderView::section {{background-color: {colors['table_header']}; color: white; padding: 12px; font-weight: 700;}}
            """)

        except Exception as e:
            print(f"خطا در رنگها: {e}")
