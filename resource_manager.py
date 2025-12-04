import os
import sys

def get_resource_path(filename):
    """مسیر صحیح فایل رو برمی‌گردونه (exe یا .py)"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, filename)

# فایل‌های مهم
GHARDASH_FILE = get_resource_path("ghardash.xlsx")
ALL_FILE = get_resource_path("all.xlsx")
COEFFICIENTS_FILE = get_resource_path("coefficients.json")
PATIENT_RECORDS_FILE = get_resource_path("patient_records.json")
COLOR_SETTINGS_FILE = get_resource_path("color_settings.json")
APP_SETTINGS_FILE = get_resource_path("app_settings.json")
