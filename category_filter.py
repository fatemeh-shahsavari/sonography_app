"""
ماژول دسته بندی خدمات - با دسته سونوگرافی و تصویربرداری
"""


class CategoryFilter:
    """فیلتر و دسته بندی خدمات"""
    
    def __init__(self):
        # محدوده کدهای سونوگرافی: از 701500 تا 701892
        self.sonography_range = (701500, 701892)
        
        self.categories = {
            "همه": lambda x: True,
            "🩻 سونوگرافی": self._is_sonography,
            "🏥 تصویربرداری": self._is_imaging,
            "💉 آزمایش": self._is_lab,
            "🦷 دندان": self._is_dental,
            "👁️ چشم": self._is_eye,
            "💊 دارو": self._is_medicine,
        }
    
    def _extract_code(self, text):
        """استخراج کد از متن"""
        # اگر فرمت "کد - شرح" باشد
        if " - " in text:
            code = text.split(" - ")[0].strip()
            return code
        # اگر فقط کد باشد
        return text.strip()
    
    def _is_sonography(self, text):
        """بررسی سونوگرافی - فقط براساس محدوده کد"""
        code = self._extract_code(text)
        try:
            code_num = int(code)
            if self.sonography_range[0] <= code_num <= self.sonography_range[1]:
                return True
        except ValueError:
            pass
        return False
    
    def _is_imaging(self, text):
         """تصویربرداری - فقط کدهایی که با 70 شروع می‌شوند (حتی سونوگرافی)"""
         code = self._extract_code(text)
         return code.startswith('70')

    
    
    def _is_lab(self, text):
        """آزمایش"""
        keywords = ["آزمایش", "تست", "سرم", "کشت", "نمونه"]
        return any(k in text for k in keywords)
    
    def _is_dental(self, text):
        """دندان"""
        keywords = ["دندان", "دهان", "فک", "لثه"]
        return any(k in text for k in keywords)
    
    def _is_eye(self, text):
        """چشم"""
        keywords = ["چشم", "بینایی", "عینک"]
        return any(k in text for k in keywords)
    
    def _is_medicine(self, text):
        """دارو"""
        keywords = ["دارو", "قرص", "شربت", "کپسول"]
        return any(k in text for k in keywords)
    
    def categorize_service(self, service_text):
        """تعیین دسته یک خدمت"""
        # سونوگرافی اولویت دارد (قبل از تصویربرداری)
        if self._is_sonography(service_text):
            return "🩻 سونوگرافی"
        
        # تصویربرداری (کدهای 70...)
        if self._is_imaging(service_text):
            return "🏥 تصویربرداری"
        
        # بقیه دسته‌ها
        for category, check_func in self.categories.items():
            if category in ["همه", "🩻 سونوگرافی", "🏥 تصویربرداری"]:
                continue
            if check_func(service_text):
                return category
        
        return "همه"
    
    def get_all_categories(self):
        """دریافت لیست تمام دسته ها"""
        return list(self.categories.keys())
