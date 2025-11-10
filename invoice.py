from reportlab.lib.pagesizes import A6
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from datetime import datetime
import jdatetime, os, platform, subprocess, shutil, json
from textwrap import wrap

# پشتیبانی از فارسی
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False

# ثبت فونت فارسی
try:
    pdfmetrics.registerFont(TTFont("Vazir", "Vazirmatn-Regular.ttf"))
    pdfmetrics.registerFont(TTFont("Vazir-Bold", "Vazirmatn-Bold.ttf"))
    HAS_FONT = True
except:
    HAS_FONT = False
    print("⚠️ فونت Vazirmatn یافت نشد!")

def persian_text(txt):
    """تبدیل متن فارسی برای نمایش صحیح"""
    if ARABIC_SUPPORT:
        return get_display(arabic_reshaper.reshape(str(txt)))
    return str(txt)

def wrap_text(text, limit=32):
    """شکستن متن طولانی شرح خدمت"""
    lines = wrap(str(text), limit)
    return "\n".join(lines)

def generate_invoice(app):
    """تولید فاکتور رسمی با ذخیره خودکار"""
    try:
        # ---------- اطلاعات بیمار ----------
        patient = app.name_in.text().strip()
        national = app.national_code_in.text().strip()
        tracking = app.tracking_code_in.text().strip()
        insurance = app.ins_in.text().strip()
        today = jdatetime.date.today().strftime("%Y/%m/%d")
        
        # نام فایل موقت
        filename = f"invoice_temp_{datetime.now().strftime('%H%M%S')}.pdf"
        c = canvas.Canvas(filename, pagesize=A6)
        w, h = A6
        font, bold = ("Vazir", "Vazir-Bold") if HAS_FONT else ("Helvetica", "Helvetica-Bold")
        margin = 8 * mm
        
        # ---------- سربرگ ----------
        logo_w, logo_h = 24 * mm, 24 * mm
        top_y = h - 6 * mm
        
        # لوگو در وسط یکسوم چپ
        if hasattr(app, "logo_path") and app.logo_path and os.path.exists(app.logo_path):
            try:
                left_third = w / 3
                logo_x = (left_third - logo_w) / 2
                logo_y = top_y - (logo_h / 2) - 10 * mm
                c.drawImage(app.logo_path, logo_x, logo_y, logo_w, logo_h, preserveAspectRatio=True, mask='auto')
            except:
                pass
        
        # اطلاعات مرکز سمت راست
        text_right = w - margin
        c.setFont(bold, 12)
        c.setFillColor(colors.HexColor("#003366"))
        c.drawRightString(text_right, top_y - 5 * mm, persian_text(app.company_name))
        c.setFont(font, 7)
        c.setFillColor(colors.black)
        c.drawRightString(text_right, top_y - 11 * mm, persian_text(app.address))
        c.drawRightString(text_right, top_y - 16 * mm, persian_text(f"تلفن: {app.phone}"))
        
        y = top_y - 22 * mm
        c.line(margin, y, w - margin, y)
        y -= 4 * mm
        
        # ---------- مشخصات بیمار ----------
        c.setFont(font, 8)
        info = [
            f"نام بیمار: {patient or '-'}",
            f"کد ملی: {national or '-'}",
            f"کد پیگیری: {tracking or '-'}",
            f"بیمه: {insurance or '-'}",
            f"تاریخ: {today}"
        ]
        
        for line in info:
            c.drawRightString(w - 10 * mm, y, persian_text(line))
            y -= 5 * mm
        
        c.line(margin, y, w - margin, y)
        y -= 10 * mm
        
        # ---------- جدول خدمات ----------
        data = [[persian_text("مبلغ (ریال)"), persian_text("نوع تعرفه"),
                 persian_text("شرح خدمت"), persian_text("ردیف")]]
        
        total = 0
        for i in range(app.table.rowCount()):
            idx = str(i + 1)
            service = wrap_text(app.table.item(i, 0).text(), 32)
            tariff = app.table.item(i, 1).text()
            cost = app.table.item(i, 4).text().replace(",", "")
            try:
                val = int(cost)
            except:
                val = 0
            total += val
            data.append([
                persian_text(f"{val:,}"),
                persian_text(tariff),
                persian_text(service),
                persian_text(idx)
            ])
        
        disc_val = app.discount_spin.value()
        if disc_val > 0:
            disc_type = app.discount_type.currentText()
            data.append([
                persian_text(f"-{disc_val:,}"),
                persian_text(disc_type),
                persian_text("تخفیف"),
                persian_text("-")
            ])
        
        data.append([
            persian_text(f"{total:,}"),
            "",
            persian_text("جمع کل"),
            ""
        ])
        
        # ---------- ساخت جدول ----------
        table = Table(data, colWidths=[22 * mm, 22 * mm, 39 * mm, 10 * mm])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#002b5c")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
            ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME", (0, 0), (-1, 0), bold),
            ("FONTNAME", (0, 1), (-1, -1), font),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("LEADING", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#004c7d")),
            ("BOX", (0, 0), (-1, -1), 1.2, colors.HexColor("#002b5c")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2),
             [colors.HexColor("#f9fbfd"), colors.HexColor("#eef3f9")]),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e8f4f8")),
        ]))
        
        table.wrapOn(c, w, h)
        table_width = sum([22 * mm, 22 * mm, 39 * mm, 10 * mm])
        x_start = w - table_width - 6 * mm
        tbl_height = len(data) * 6.3 * mm
        table.drawOn(c, x_start, y - tbl_height)
        y -= tbl_height + 12 * mm
        
        # ---------- پایانی ----------
        c.setFont(bold, 8)
        c.drawCentredString(w / 2, 10 * mm, persian_text("با آرزوی سلامتی 🌿"))
        c.save()
        
        # ---------- ذخیره خودکار ----------
        final_path = filename
        try:
            if hasattr(app, "save_dir") and os.path.exists(app.save_dir):
                save_path = app.save_dir
            elif os.path.exists("app_settings.json"):
                with open("app_settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    save_path = settings.get("save_path", os.getcwd())
            else:
                save_path = os.getcwd()
            
            os.makedirs(save_path, exist_ok=True)
            date_tag = jdatetime.date.today().strftime("%Y-%m-%d")
            clean_code = national if national else "بدون-کد"
            final_name = f"فاکتور_{clean_code}_{date_tag}.pdf"
            final_path = os.path.join(save_path, final_name)
            
            # اگر فایل وجود داشت، timestamp اضافه کن
            if os.path.exists(final_path):
                timestamp = datetime.now().strftime("%H%M%S")
                final_name = f"فاکتور_{clean_code}_{date_tag}_{timestamp}.pdf"
                final_path = os.path.join(save_path, final_name)
            
            shutil.move(filename, final_path)
            print(f"✅ فاکتور در پوشه ذخیره شد:\n{final_path}")
        except Exception as e:
            print(f"⚠️ خطا در ذخیره خودکار فاکتور: {e}")
            final_path = filename
        
        return final_path
    
    except Exception as e:
        print(f"⚠️ خطا در اجرای فاکتور: {e}")
        import traceback
        traceback.print_exc()
        return None


def direct_print(app):
    """چاپ حرفه‌ای با استفاده از QPrintDialog و PyMuPDF - سازگار کامل با PyQt6"""
    from PyQt6.QtWidgets import QMessageBox
    from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
    from PyQt6.QtGui import QPainter, QImage, QPageSize, QPageLayout
    from PyQt6.QtCore import QRectF
    
    try:
        # تولید فاکتور
        pdf_path = generate_invoice(app)
        
        if not pdf_path or not os.path.exists(pdf_path):
            QMessageBox.warning(app, "خطا", "⚠️ فایل PDF برای چاپ یافت نشد!")
            return
        
        # بررسی وجود PyMuPDF
        try:
            import fitz  # PyMuPDF
            HAS_PYMUPDF = True
        except ImportError:
            HAS_PYMUPDF = False
            print("⚠️ PyMuPDF یافت نشد. استفاده از روش فالبک...")
        
        if HAS_PYMUPDF:
            # ساخت پرینتر
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            
            # ⭐ تنظیم صفحه A6 با QPageLayout (سازگار با PyQt6)
            page_size = QPageSize(QPageSize.PageSizeId.A6)
            page_layout = QPageLayout(page_size, QPageLayout.Orientation.Portrait, printer.pageLayout().margins())
            printer.setPageLayout(page_layout)
            
            # نمایش دیالوگ چاپ (کاربر می‌تونه چاپگر، تعداد کپی و ... رو انتخاب کنه)
            print_dialog = QPrintDialog(printer, app)
            print_dialog.setWindowTitle("چاپ فاکتور")
            
            if print_dialog.exec() == QPrintDialog.DialogCode.Accepted:
                try:
                    doc = fitz.open(pdf_path)
                    painter = QPainter()
                    
                    if not painter.begin(printer):
                        QMessageBox.warning(app, "خطا", "⚠️ خطا در شروع چاپ!")
                        return
                    
                    for page_num in range(len(doc)):
                        if page_num > 0:
                            printer.newPage()
                        
                        page = doc[page_num]
                        # بزرگ‌نمایی 2x برای کیفیت بالاتر
                        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                        
                        # تبدیل به QImage
                        img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
                        
                        # رسم تصویر روی صفحه چاپ
                        target_rect = QRectF(0, 0, printer.width(), printer.height())
                        painter.drawImage(target_rect, img)
                    
                    painter.end()
                    doc.close()
                    
                    QMessageBox.information(app, "چاپ", "✅ فاکتور با موفقیت چاپ شد!")
                    print(f"✅ چاپ موفق: {pdf_path}")
                    
                except Exception as e:
                    QMessageBox.critical(app, "خطا", f"❌ خطا در چاپ:\n{str(e)}")
                    print(f"⚠️ خطا در چاپ با PyMuPDF: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("❌ چاپ لغو شد توسط کاربر")
        
        else:
            # اگر PyMuPDF نصب نبود، از روش فالبک استفاده کن
            fallback_print(app, pdf_path)
    
    except Exception as e:
        QMessageBox.critical(app, "خطا", f"❌ خطا در چاپ:\n{str(e)}")
        print(f"⚠️ خطا در چاپ: {e}")
        import traceback
        traceback.print_exc()


def fallback_print(app, pdf_path):
    """روش فالبک برای چاپ (باز کردن PDF در نرمافزار پیشفرض)"""
    from PyQt6.QtWidgets import QMessageBox
    from PyQt6.QtGui import QDesktopServices
    from PyQt6.QtCore import QUrl
    
    sys_platform = platform.system().lower()
    
    print(f"🖨️ استفاده از روش فالبک برای چاپ")
    print(f"💻 سیستم عامل: {sys_platform}")
    
    # ویندوز
    if "windows" in sys_platform:
        try:
            os.startfile(pdf_path, "print")
            QMessageBox.information(
                app,
                "چاپ",
                "✅ فایل برای چاپ ارسال شد!\n\nاگر پنجره چاپ باز نشد، دستی فایل را باز کرده و چاپ کنید."
            )
            return
        except Exception as e:
            print(f"⚠️ خطا در چاپ ویندوز: {e}")
    
    # مک
    elif "darwin" in sys_platform:
        try:
            subprocess.run(["lp", pdf_path], check=True)
            QMessageBox.information(app, "چاپ", "✅ فایل برای چاپ ارسال شد!")
            return
        except subprocess.CalledProcessError as e:
            print(f"⚠️ خطا در چاپ مک: {e}")
        except FileNotFoundError:
            print("⚠️ دستور lp یافت نشد")
    
    # لینوکس
    else:
        # تلاش برای چاپ با lpr
        try:
            result = subprocess.run(["lpr", pdf_path], capture_output=True, text=True)
            if result.returncode == 0:
                QMessageBox.information(app, "چاپ", "✅ فایل برای چاپ ارسال شد!")
                return
            else:
                print(f"⚠️ خطای lpr: {result.stderr}")
        except FileNotFoundError:
            print("⚠️ lpr یافت نشد")
        
        # تلاش با lp (جایگزین)
        try:
            result = subprocess.run(["lp", pdf_path], capture_output=True, text=True)
            if result.returncode == 0:
                QMessageBox.information(app, "چاپ", "✅ فایل برای چاپ ارسال شد!")
                return
            else:
                print(f"⚠️ خطای lp: {result.stderr}")
        except FileNotFoundError:
            print("⚠️ lp یافت نشد")
    
    # آخرین راه حل: باز کردن فایل
    try:
        QDesktopServices.openUrl(QUrl.fromLocalFile(pdf_path))
        QMessageBox.information(
            app,
            "فایل باز شد",
            f"✅ فایل PDF باز شد!\n\n"
            f"لطفاً از منوی برنامه PDF گزینه چاپ را انتخاب کنید:\n"
            f"• لینوکس/ویندوز: Ctrl+P\n"
            f"• مک: Cmd+P\n\n"
            f"مسیر فایل:\n{pdf_path}"
        )
    except Exception as e:
        QMessageBox.warning(
            app,
            "خطا",
            f"⚠️ چاپ خودکار امکانپذیر نیست!\n\n"
            f"فایل ذخیره شده است در:\n{pdf_path}\n\n"
            f"لطفاً دستی آن را باز و چاپ کنید."
        )
        print(f"⚠️ خطا در باز کردن فایل: {e}")
