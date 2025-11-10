"""
ماژول محاسبه هزینه خدمات بر اساس کایها - نسخه جدید برای all.xlsx
"""

class PriceCalculator:
    """محاسبه قیمت خدمات براساس ضرایب کای"""
    
    def __init__(self, coefficients):
        """
        coefficients: دیکشنری شامل 6 ضریب:
        - کای حرفه‌ای # دار
        - کای فنی # دار  
        - کای حرفه‌ای بدون #
        - کای فنی بدون #
        - کای حرفه‌ای دولتی
        - کای فنی دولتی
        """
        self.coef = coefficients
    
    def calculate_service_price(self, service_type, professional_value, technical_value):
        """
        محاسبه قیمت خدمت
        
        Args:
            service_type: نوع خدمت (شامل '#' یا بدون '#')
            professional_value: ضریب حرفهای
            technical_value: ضریب فنی
            
        Returns:
            dict: قیمتها و اطلاعات
        """
        # اگر مقادیر صفر باشند، فقط صفر برمی‌گردانیم
        if professional_value == 0 and technical_value == 0:
            return {
                'private': 0,
                'insurance': 0,
                'organization': 0,
                'government': 0,
                'government_70': 0,
                'has_insurance': True
            }
        
        # تشخیص نوع کای براساس وجود یا عدم وجود #
        has_hash = service_type and '#' in str(service_type)
        
        if has_hash:
            # خدمات # دار
            kai_prof = self.coef.get('کای حرفه‌ای # دار', 568000)
            kai_tech = self.coef.get('کای فنی # دار', 1777000)
        else:
            # خدمات بدون # (جراحی)
            kai_prof = self.coef.get('کای حرفه‌ای بدون #', 1011000)
            kai_tech = self.coef.get('کای فنی بدون #', 2843000)
        
        # کای دولتی (برای هر دو نوع یکسان است)
        kai_prof_gov = self.coef.get('کای حرفه‌ای دولتی', 302000)
        kai_tech_gov = self.coef.get('کای فنی دولتی', 428000)
        
        # فرمول‌های محاسبه:
        # خصوصی آزاد = (کای حرفه‌ای × ضریب حرفه‌ای) + (کای فنی × ضریب فنی)
        private_price = (professional_value * kai_prof) + (technical_value * kai_tech)
        
        # دولتی = (کای حرفه‌ای دولتی × ضریب حرفه‌ای) + (کای فنی دولتی × ضریب فنی)
        government_price = (professional_value * kai_prof_gov) + (technical_value * kai_tech_gov)
        
        # ⭐ فرمول اصلاح شده:
        # سهم سازمان = 70% دولتی
        organization_share = government_price * 0.7
        
        # بیمه شده = خصوصی آزاد - سهم سازمان
        insurance_price = private_price - organization_share
        
        return {
            'private': round(private_price),
            'insurance': round(insurance_price),
            'organization': round(organization_share),
            'government': round(government_price),
            'government_70': round(organization_share),  # همان سهم سازمان است
            'has_insurance': True
        }
    
    @staticmethod
    def load_coefficients_from_file(file_path='coefficients.json'):
        """بارگذاری ضرایب از فایل"""
        import json
        import os
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # مقادیر پیشفرض
        return {
            'کای حرفه‌ای # دار': 568000,
            'کای فنی # دار': 1777000,
            'کای حرفه‌ای بدون #': 1011000,
            'کای فنی بدون #': 2843000,
            'کای حرفه‌ای دولتی': 302000,
            'کای فنی دولتی': 428000
        }
    
    @staticmethod
    def save_coefficients_to_file(coefficients, file_path='coefficients.json'):
        """ذخیره ضرایب در فایل"""
        import json
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(coefficients, f, ensure_ascii=False, indent=2)
