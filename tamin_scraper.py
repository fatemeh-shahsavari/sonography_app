"""
ماژول دریافت خودکار نسخه الکترونیک از سایت تامین اجتماعی
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from datetime import datetime

class TaminScraper:
    """دریافت خودکار نسخه الکترونیک از ep.tamin.ir"""
    
    def __init__(self, browser_type="chrome"):
        """
        Args:
            browser_type: نوع مرورگر ("chrome" یا "firefox")
        """
        self.browser_type = browser_type
        self.driver = None
        self.is_logged_in = False
        
        # ایجاد پوشه برای ذخیره نسخه‌ها
        os.makedirs("prescriptions", exist_ok=True)
    
    def start_browser(self, headless=False):
        """راه‌اندازی مرورگر"""
        try:
            if self.browser_type == "firefox":
                options = webdriver.FirefoxOptions()
                if headless:
                    options.add_argument('--headless')
                self.driver = webdriver.Firefox(
                    service=FirefoxService(GeckoDriverManager().install()),
                    options=options
                )
            else:  # chrome
                options = webdriver.ChromeOptions()
                if headless:
                    options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                self.driver = webdriver.Chrome(
                    service=ChromeService(ChromeDriverManager().install()),
                    options=options
                )
            
            self.driver.maximize_window()
            return True
        except Exception as e:
            print(f"خطا در راه‌اندازی مرورگر: {e}")
            return False
    
    def login_manual(self):
        """ورود دستی توسط کاربر"""
        try:
            if not self.driver:
                if not self.start_browser():
                    return False
            
            # رفتن به صفحه ورود
            self.driver.get("https://ep.tamin.ir")
            
            print("🔐 لطفا در مرورگر وارد حساب کاربری خود شوید...")
            print("⏳ بعد از ورود موفقیت‌آمیز، این پنجره به‌طور خودکار ادامه می‌دهد...")
            
            # صبر کردن تا کاربر وارد شود (چک URL)
            WebDriverWait(self.driver, 300).until(
                lambda driver: "dashboard" in driver.current_url.lower() or 
                               "panel" in driver.current_url.lower() or
                               driver.current_url != "https://ep.tamin.ir"
            )
            
            self.is_logged_in = True
            print("✅ ورود موفقیت‌آمیز!")
            return True
            
        except Exception as e:
            print(f"❌ خطا در ورود: {e}")
            return False
    
    def search_prescription(self, national_code, tracking_code):
        """
        جستجوی نسخه با کدملی و کد پیگیری
        
        Args:
            national_code: کد ملی بیمار
            tracking_code: کد پیگیری نسخه
        
        Returns:
            dict: اطلاعات نسخه
        """
        try:
            if not self.is_logged_in:
                print("❌ ابتدا باید وارد سایت شوید!")
                return None
            
            # رفتن به صفحه جستجوی نسخه (ممکن است URL متفاوت باشد)
            # این بخش باید بر اساس ساختار واقعی سایت تنظیم شود
            
            # پیدا کردن فیلد کد ملی
            national_code_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "nationalCode"))
            )
            national_code_field.clear()
            national_code_field.send_keys(national_code)
            
            # پیدا کردن فیلد کد پیگیری
            tracking_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "trackingCode"))
            )
            tracking_field.clear()
            tracking_field.send_keys(tracking_code)
            
            # کلیک روی دکمه جستجو
            search_button = self.driver.find_element(By.ID, "searchButton")
            search_button.click()
            
            # صبر برای بارگذاری نتایج
            time.sleep(3)
            
            # استخراج اطلاعات نسخه
            prescription_info = self.extract_prescription_data()
            
            return prescription_info
            
        except Exception as e:
            print(f"❌ خطا در جستجوی نسخه: {e}")
            return None
    
    def extract_prescription_data(self):
        """استخراج اطلاعات نسخه از صفحه"""
        try:
            # این بخش باید بر اساس ساختار HTML واقعی سایت نوشته شود
            prescription = {
                'patient_name': '',
                'national_code': '',
                'date': '',
                'doctor_name': '',
                'medicines': [],
                'services': []
            }
            
            # مثال استخراج داده
            # prescription['patient_name'] = self.driver.find_element(By.CLASS_NAME, "patient-name").text
            
            return prescription
            
        except Exception as e:
            print(f"خطا در استخراج داده: {e}")
            return None
    
    def save_prescription_screenshot(self, national_code, tracking_code):
        """ذخیره اسکرین‌شات نسخه"""
        try:
            filename = f"prescriptions/{national_code}_{tracking_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.driver.save_screenshot(filename)
            print(f"✅ اسکرین‌شات ذخیره شد: {filename}")
            return filename
        except Exception as e:
            print(f"❌ خطا در ذخیره اسکرین‌شات: {e}")
            return None
    
    def save_prescription_pdf(self, national_code, tracking_code):
        """ذخیره PDF نسخه"""
        try:
            # این متد باید بر اساس امکانات سایت پیاده شود
            # معمولا یک دکمه PDF در سایت وجود دارد
            
            pdf_button = self.driver.find_element(By.CLASS_NAME, "download-pdf")
            pdf_button.click()
            
            time.sleep(2)
            
            return True
        except Exception as e:
            print(f"❌ خطا در دانلود PDF: {e}")
            return False
    
    def close(self):
        """بستن مرورگر"""
        if self.driver:
            self.driver.quit()
            self.is_logged_in = False
