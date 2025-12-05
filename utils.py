import sys
import os
import pandas as pd
import arabic_reshaper
from bidi.algorithm import get_display


def resource_path(relative_path):
    """
    آدرس فایل‌ها را هم در حالت عادی و هم در حالت exe پیدا می‌کند
    این تابع برای بسته‌بندی PyInstaller ضروری است
    """
    try:
        # وقتی برنامه exe شده است، فایل‌ها در این مسیر موقت هستند
        base_path = sys._MEIPASS
    except Exception:
        # در حالت عادی (توسعه)
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


def int_from_string(s):
    """تبدیل رشته به عدد صحیح"""
    if pd.isna(s):
        return 0
    if isinstance(s, (int, float)):
        return int(s)
    try:
        return int(str(s).replace(",", "").strip())
    except:
        return 0


def rtl(text):
    """تبدیل متن فارسی به جهت صحیح نمایش در PDF"""
    try:
        reshaped_text = arabic_reshaper.reshape(str(text))
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except Exception:
        return str(text)


def rtl_no_reshape(text):
    """تبدیل متن فارسی بدون reshape - برای متن‌های ترکیبی با اعداد"""
    try:
        # فقط از bidi استفاده می‌کنیم بدون reshape
        return get_display(str(text))
    except Exception:
        return str(text)


def wrap_text(text, max_chars=35):
    """شکستن متن‌های طولانی برای جدول فاکتور"""
    words = text.split()
    lines, current = [], ""
    for w in words:
        if len(current) + len(w) + 1 <= max_chars:
            current += (" " if current else "") + w
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)
    return "\n".join(lines)

