"""
رابط گرافیکی دریافت نسخه الکترونیک تامین اجتماعی
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTextEdit, QMessageBox,
    QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from tamin_scraper import TaminScraper

class PrescriptionWorker(QThread):
    """Worker thread برای عملیات طولانی"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, scraper, national_code, tracking_code):
        super().__init__()
        self.scraper = scraper
        self.national_code = national_code
        self.tracking_code = tracking_code
    
    def run(self):
        try:
            self.progress.emit("در حال جستجوی نسخه...")
            result = self.scraper.search_prescription(
                self.national_code, 
                self.tracking_code
            )
            
            if result:
                self.progress.emit("در حال ذخیره اسکرین‌شات...")
                screenshot = self.scraper.save_prescription_screenshot(
                    self.national_code,
                    self.tracking_code
                )
                result['screenshot'] = screenshot
                
                self.finished.emit(result)
            else:
                self.error.emit("نسخه‌ای یافت نشد!")
                
        except Exception as e:
            self.error.emit(str(e))

class PrescriptionDialog(QDialog):
    """پنجره دریافت نسخه الکترونیک"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("📋 دریافت نسخه الکترونیک تامین اجتماعی")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.resize(600, 500)
        
        self.scraper = TaminScraper(browser_type="chrome")
        self.worker = None
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # راهنما
        guide = QLabel(
            "🔐 برای دریافت نسخه الکترونیک، ابتدا وارد حساب کاربری خود در سایت تامین شوید.\n"
            "سپس کد ملی و کد پیگیری بیمار را وارد کنید."
        )
        guide.setWordWrap(True)
        guide.setStyleSheet("background-color: #e3f2fd; padding: 10px; border-radius: 5px;")
        layout.addWidget(guide)
        
        # دکمه ورود
        self.btn_login = QPushButton("🔐 ورود به سایت تامین اجتماعی")
        self.btn_login.clicked.connect(self.login_to_tamin)
        self.btn_login.setMinimumHeight(40)
        layout.addWidget(self.btn_login)
        
        # فیلدهای ورودی
        form_layout = QVBoxLayout()
        
        # کد ملی
        national_layout = QHBoxLayout()
        national_layout.addWidget(QLabel("🆔 کد ملی بیمار:"))
        self.national_code_input = QLineEdit()
        self.national_code_input.setPlaceholderText("مثال: 0123456789")
        self.national_code_input.setMaxLength(10)
        national_layout.addWidget(self.national_code_input)
        form_layout.addLayout(national_layout)
        
        # کد پیگیری
        tracking_layout = QHBoxLayout()
        tracking_layout.addWidget(QLabel("📝 کد پیگیری:"))
        self.tracking_code_input = QLineEdit()
        self.tracking_code_input.setPlaceholderText("مثال: 123456")
        tracking_layout.addWidget(self.tracking_code_input)
        form_layout.addLayout(tracking_layout)
        
        layout.addLayout(form_layout)
        
        # دکمه جستجو
        self.btn_search = QPushButton("🔍 دریافت نسخه")
        self.btn_search.clicked.connect(self.search_prescription)
        self.btn_search.setEnabled(False)
        self.btn_search.setMinimumHeight(40)
        layout.addWidget(self.btn_search)
        
        # نوار پیشرفت
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximum(0)  # Indeterminate
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # وضعیت
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #0077b6; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # نمایش نتایج
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("نتایج اینجا نمایش داده می‌شود...")
        layout.addWidget(self.result_text)
        
        # دکمه‌های پایین
        button_layout = QHBoxLayout()
        
        btn_close = QPushButton("❌ بستن")
        btn_close.clicked.connect(self.close_dialog)
        button_layout.addWidget(btn_close)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def login_to_tamin(self):
        """ورود به سایت تامین"""
        self.btn_login.setEnabled(False)
        self.status_label.setText("⏳ در حال باز کردن مرورگر...")
        
        try:
            if self.scraper.login_manual():
                self.btn_search.setEnabled(True)
                self.btn_login.setText("✅ وارد شده‌اید")
                self.status_label.setText("✅ ورود موفقیت‌آمیز! حالا می‌توانید نسخه را جستجو کنید.")
                self.status_label.setStyleSheet("color: green; font-weight: bold;")
            else:
                self.btn_login.setEnabled(True)
                self.status_label.setText("❌ ورود ناموفق بود")
                self.status_label.setStyleSheet("color: red; font-weight: bold;")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ورود:\n{str(e)}")
            self.btn_login.setEnabled(True)
    
    def search_prescription(self):
        """جستجوی نسخه"""
        national_code = self.national_code_input.text().strip()
        tracking_code = self.tracking_code_input.text().strip()
        
        if not national_code or not tracking_code:
            QMessageBox.warning(self, "هشدار", "لطفا کد ملی و کد پیگیری را وارد کنید")
            return
        
        # شروع worker
        self.btn_search.setEnabled(False)
        self.progress_bar.show()
        self.result_text.clear()
        
        self.worker = PrescriptionWorker(self.scraper, national_code, tracking_code)
        self.worker.finished.connect(self.on_search_finished)
        self.worker.error.connect(self.on_search_error)
        self.worker.progress.connect(self.on_progress)
        self.worker.start()
    
    def on_search_finished(self, result):
        """نمایش نتایج"""
        self.progress_bar.hide()
        self.btn_search.setEnabled(True)
        self.status_label.setText("✅ نسخه دریافت شد!")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        
        # نمایش اطلاعات
        text = f"""
📋 اطلاعات نسخه الکترونیک:

👤 بیمار: {result.get('patient_name', 'نامشخص')}
🆔 کد ملی: {result.get('national_code', 'نامشخص')}
📅 تاریخ: {result.get('date', 'نامشخص')}
👨‍⚕️ پزشک: {result.get('doctor_name', 'نامشخص')}

💊 داروها:
{chr(10).join(['- ' + med for med in result.get('medicines', ['هیچ دارویی ثبت نشده'])])}

🔬 خدمات:
{chr(10).join(['- ' + srv for srv in result.get('services', ['هیچ خدمتی ثبت نشده'])])}

📸 اسکرین‌شات ذخیره شد: {result.get('screenshot', 'ذخیره نشد')}
        """
        
        self.result_text.setText(text)
    
    def on_search_error(self, error_msg):
        """نمایش خطا"""
        self.progress_bar.hide()
        self.btn_search.setEnabled(True)
        self.status_label.setText(f"❌ خطا: {error_msg}")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        QMessageBox.critical(self, "خطا", error_msg)
    
    def on_progress(self, message):
        """به‌روزرسانی وضعیت"""
        self.status_label.setText(message)
    
    def close_dialog(self):
        """بستن پنجره"""
        self.scraper.close()
        self.close()
