"""
سیستم مدیریت سوابق بیماران
ذخیره و بازیابی خودکار سوابق بر اساس کدملی + جستجوی نام
"""

import json
import os
from datetime import datetime
import jdatetime


class PatientRecordsManager:
    """مدیریت سوابق بیماران"""
    
    def __init__(self, records_file="patient_records.json"):
        self.records_file = records_file
        self.records = self.load_records()
    
    def load_records(self):
        """بارگذاری سوابق از فایل"""
        try:
            if os.path.exists(self.records_file):
                with open(self.records_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری سوابق: {e}")
            return {}
    
    def save_records(self):
        """ذخیره سوابق در فایل"""
        try:
            with open(self.records_file, 'w', encoding='utf-8') as f:
                json.dump(self.records, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"⚠️ خطا در ذخیره سوابق: {e}")
            return False
    
    def add_record(self, national_code, patient_data):
        """
        افزودن رکورد جدید برای بیمار
        
        Args:
            national_code: کدملی بیمار
            patient_data: دیکشنری حاوی اطلاعات بیمار و فاکتور
        """
        if not national_code or national_code.strip() == "":
            return False
        
        national_code = national_code.strip()
        
        # اگر بیمار وجود نداشت، ایجاد کن
        if national_code not in self.records:
            self.records[national_code] = {
                'name': patient_data.get('name', ''),
                'insurance': patient_data.get('insurance', ''),
                'invoices': []
            }
        
        # آپدیت نام و بیمه (در صورت تغییر)
        if patient_data.get('name'):
            self.records[national_code]['name'] = patient_data['name']
        if patient_data.get('insurance'):
            self.records[national_code]['insurance'] = patient_data['insurance']
        
        # افزودن فاکتور جدید
        invoice_record = {
            'date': jdatetime.date.today().strftime("%Y/%m/%d"),
            'datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'tracking_code': patient_data.get('tracking_code', ''),
            'services': patient_data.get('services', []),
            'total': patient_data.get('total', 0),
            'organization': patient_data.get('organization', 0),
            'patient_pay': patient_data.get('patient_pay', 0),
            'discount': patient_data.get('discount', 0),
            'tariff_type': patient_data.get('tariff_type', 'بیمه‌شده'),
            'pdf_path': patient_data.get('pdf_path', '')
        }
        
        self.records[national_code]['invoices'].append(invoice_record)
        
        return self.save_records()
    
    def get_patient_records(self, national_code):
        """دریافت سوابق بیمار بر اساس کدملی"""
        if not national_code:
            return None
        
        national_code = national_code.strip()
        return self.records.get(national_code, None)
    
    def get_patient_summary(self, national_code):
        """دریافت خلاصه سوابق بیمار"""
        records = self.get_patient_records(national_code)
        if not records:
            return None
        
        total_invoices = len(records['invoices'])
        total_amount = sum(inv['total'] for inv in records['invoices'])
        last_visit = records['invoices'][-1]['date'] if records['invoices'] else 'نامشخص'
        
        return {
            'national_code': national_code,
            'name': records['name'],
            'insurance': records['insurance'],
            'total_invoices': total_invoices,
            'total_amount': total_amount,
            'last_visit': last_visit,
            'invoices': records['invoices']
        }
    
    def search_by_name(self, name_query):
        """
        جستجو بیمار بر اساس نام یا نام خانوادگی
        
        Returns:
            لیستی از بیماران مطابق با جستجو
        """
        name_query = name_query.strip().lower()
        
        if not name_query or len(name_query) < 2:
            return []
        
        results = []
        
        for national_code, data in self.records.items():
            patient_name = data['name'].lower()
            
            # جستجو در نام کامل یا بخش‌های آن
            if name_query in patient_name or any(name_query in part for part in patient_name.split()):
                summary = self.get_patient_summary(national_code)
                if summary:
                    results.append(summary)
        
        # مرتب‌سازی بر اساس آخرین مراجعه
        results.sort(key=lambda x: x['last_visit'], reverse=True)
        
        return results
    
    def get_all_patients(self, limit=100):
        """دریافت لیست همه بیماران"""
        patients = []
        
        for national_code in list(self.records.keys())[:limit]:
            summary = self.get_patient_summary(national_code)
            if summary:
                patients.append(summary)
        
        # مرتب‌سازی بر اساس آخرین مراجعه
        patients.sort(key=lambda x: x['last_visit'], reverse=True)
        
        return patients
