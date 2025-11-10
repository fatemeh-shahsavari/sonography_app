"""
ماژول قابلیت‌های اضافی
شامل: پشتیبان‌گیری، آمار، تخفیف
"""
import os
import shutil
from datetime import datetime
from PyQt6.QtWidgets import QMessageBox


class FeatureManager:
    """مدیریت قابلیت‌های اضافی"""
    
    def __init__(self, parent):
        self.parent = parent
        
        # ایجاد پوشه‌ها
        os.makedirs("invoices_history", exist_ok=True)
        os.makedirs("backups", exist_ok=True)
    
    def create_backup(self):
        """پشتیبان‌گیری از اکسل"""
        try:
            backup_name = f"backups/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            shutil.copy2(self.parent.excel_path, backup_name)
            QMessageBox.information(
                self.parent, 
                "موفق", 
                f"✅ پشتیبان با موفقیت ساخته شد:\n{backup_name}"
            )
            return True
        except Exception as e:
            QMessageBox.warning(
                self.parent, 
                "خطا", 
                f"❌ خطا در ساخت پشتیبان:\n{str(e)}"
            )
            return False
    
    def save_to_history(self, pdf_path, patient_name):
        """ذخیره فاکتور در تاریخچه"""
        try:
            history_name = f"invoices_history/{patient_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            shutil.copy2(pdf_path, history_name)
            return True
        except Exception as e:
            print(f"خطا در ذخیره تاریخچه: {e}")
            return False
    
    def get_today_stats(self):
        """آمار فاکتورهای امروز"""
        try:
            today = datetime.now().strftime('%Y%m%d')
            count = 0
            
            if os.path.exists("invoices_history"):
                for f in os.listdir("invoices_history"):
                    if today in f and f.endswith('.pdf'):
                        count += 1
            
            return count
        except:
            return 0
    
    def calculate_discount(self, total, discount_value, discount_type):
        """
        محاسبه تخفیف
        
        Args:
            total: مبلغ کل
            discount_value: مقدار تخفیف
            discount_type: نوع تخفیف (ریالی یا درصدی)
        
        Returns:
            tuple: (مبلغ نهایی، مقدار تخفیف)
        """
        if discount_type == "درصدی":
            discount_amount = int(total * discount_value / 100)
        else:  # ریالی
            discount_amount = discount_value
        
        final_total = max(0, total - discount_amount)
        
        return final_total, discount_amount
