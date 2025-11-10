"""
اسکریپت تبدیل داده‌های ghardash.xlsx به all.xlsx
برای مهاجرت داده‌ها
"""
import pandas as pd
from calculator import PriceCalculator

def migrate_to_all_excel():
    """مهاجرت از ghardash به all"""
    
    # بارگذاری فایل all
    df = pd.read_excel('all.xlsx')
    
    # تنظیم هدرها
    df.columns = ['کدملی', 'ویژگی کد', 'شرح کد', 'توضیحات', 'کل', 'حرفه‌ای', 'فنی', 'ارزش پایه بیهوشی']
    df = df.iloc[2:].reset_index(drop=True)
    df = df.dropna(subset=['کدملی'])
    
    # بارگذاری ضرایب
    coefficients = PriceCalculator.load_coefficients_from_file()
    calculator = PriceCalculator(coefficients)
    
    # محاسبه قیمت‌ها برای هر خدمت
    prices_data = []
    
    for idx, row in df.iterrows():
        code = str(row['کدملی']).strip()
        service_type = str(row['ویژگی کد']) if pd.notna(row['ویژگی کد']) else ''
        professional = float(row['حرفه‌ای']) if pd.notna(row['حرفه‌ای']) else 0
        technical = float(row['فنی']) if pd.notna(row['فنی']) else 0
        
        if professional > 0 or technical > 0:
            prices = calculator.calculate_service_price(service_type, professional, technical)
            
            prices_data.append({
                'کدملی': code,
                'ویژگی کد': service_type,
                'شرح کد': row['شرح کد'],
                'کل': row['کل'],
                'حرفه‌ای': professional,
                'فنی': technical,
                'خصوصی آزاد': prices['private'],
                'بیمه شده': prices['insurance'],
                'سهم سازمان': prices['organization'],
                'دولتی': prices['government'],
                '70 درصد دولتی': prices['government_70']
            })
    
    # ذخیره در فایل جدید
    output_df = pd.DataFrame(prices_data)
    output_df.to_excel('calculated_prices.xlsx', index=False)
    print(f"محاسبات برای {len(prices_data)} خدمت انجام شد و در calculated_prices.xlsx ذخیره گردید")

if __name__ == '__main__':
    migrate_to_all_excel()
