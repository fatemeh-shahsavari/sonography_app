"""
ماژول مدیریت میانبرهای صفحه‌کلید
"""
from PyQt6.QtGui import QShortcut, QKeySequence

class ShortcutManager:
    """مدیریت میانبرهای صفحه‌کلید"""
    
    def __init__(self, parent):
        self.parent = parent
        self.setup_shortcuts()
    
    def setup_shortcuts(self):
        """تنظیم تمام میانبرها"""
        shortcuts = [
            ("Ctrl+S", self.parent.save_invoice),
            ("Ctrl+P", self.parent.print_invoice),
            ("Ctrl+N", self.parent.clear_all),
            ("Ctrl+F", lambda: self.parent.search.setFocus()),
            ("Delete", self.parent.remove_selected),
            ("Ctrl+H", self.parent.show_history),
            ("Ctrl+B", self.parent.create_backup),
            ("F5", self.parent.calculate),
        ]
        
        for key, func in shortcuts:
            QShortcut(QKeySequence(key), self.parent).activated.connect(func)
    
    @staticmethod
    def get_shortcuts_help():
        """دریافت راهنمای میانبرها"""
        return """
        ⌨️ میانبرهای صفحه‌کلید:
        
        Ctrl+S : ذخیره فاکتور PDF
        Ctrl+P : چاپ مستقیم
        Ctrl+N : پاکسازی فرم
        Ctrl+F : جستجو
        Ctrl+H : مشاهده تاریخچه
        Ctrl+B : پشتیبان‌گیری
        Delete : حذف خدمت انتخابی
        F5     : محاسبه مجدد
        """
