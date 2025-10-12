# راهنمای سریع: سیستم جلوگیری از ثبت‌نام تکراری

## مراحل راه‌اندازی (5 دقیقه)

### گام 1: اجرای Migration 

```bash
cd truckmaintenance
alembic upgrade head
```

✅ این دستور تمام تغییرات دیتابیس را اعمال می‌کند.

### گام 2: راه‌اندازی Backend

```bash
python scripts/run_backend.py
```

✅ Backend روی پورت 5000 اجرا می‌شود.

### گام 3: راه‌اندازی Frontend (در ترمینال جدید)

```bash
npm run dev
```

✅ Frontend روی پورت 5173 اجرا می‌شود.

### گام 4: تست عملکرد

#### تست 1: ثبت‌نام موفق

1. به `http://localhost:5173/signup` بروید
2. اطلاعات زیر را وارد کنید:
   - نام شرکت: شرکت تست من
   - نماینده: علی احمدی
   - موبایل: 09123456789
   - دسته‌ها: تعمیرات موتور
3. کلیک "ارسال درخواست"

**نتیجه مورد انتظار:** ✅ "درخواست شما با موفقیت ثبت شد"

#### تست 2: شماره تکراری

1. دوباره همان فرم را پر کنید
2. از همان شماره موبایل استفاده کنید

**نتیجه مورد انتظار:** ❌ "این شماره موبایل قبلاً در سیستم ثبت شده است"

#### تست 3: Rate Limit

1. سه بار پشت سر هم درخواست ثبت کنید (با شماره‌های متفاوت)
2. بار چهارم را امتحان کنید

**نتیجه مورد انتظار:** ⏱️ "تعداد درخواست‌های شما از حد مجاز گذشته است"

#### تست 4: نام مشابه

1. ثبت اول: "شرکت خدمات خودرو" با موبایل 09121111111
2. ثبت دوم: "شرکت خدمات خودرویی" با موبایل 09122222222

**نتیجه مورد انتظار:** ✅ ثبت موفق + ⚠️ هشدار شباهت نام

### گام 5: بررسی در Business Expert Dashboard

1. Login به `/business-expert/login`
2. رفتن به "درخواست‌ها"
3. مشاهده Badge های هشدار

## فایل‌های کلیدی

| فایل | توضیح |
|------|-------|
| `backend/routes/provider_applications.py` | Logic اصلی Duplicate Prevention |
| `backend/middleware/security.py` | Validation Functions |
| `backend/middleware/rate_limiting.py` | Rate Limiting |
| `backend/utils/fuzzy_match.py` | Fuzzy Matching |
| `src/pages/ProviderSignup.tsx` | Frontend Form |
| `src/pages/business-expert/ApplicationReview.tsx` | Dashboard |

## تنظیمات مهم

### بک‌اند (`backend/config.py`)

```python
RATE_LIMIT_APPLICATIONS_PER_HOUR = 3     # تعداد درخواست مجاز در ساعت
FUZZY_MATCH_THRESHOLD = 0.8              # حد شباهت (0-1)
DUPLICATE_CHECK_ENABLED = True            # فعال/غیرفعال duplicate check
RATE_LIMIT_ENABLED = True                 # فعال/غیرفعال rate limit
SUPPORT_PHONE = "021-12345678"            # شماره پشتیبانی
```

## دستورات مفید

### اجرای تست‌ها
```bash
pytest tests/test_duplicate_prevention.py -v
```

### بررسی لاگ‌ها
```bash
tail -f backend/security.log
```

### Reset دیتابیس (فقط Development)
```bash
alembic downgrade -1
alembic upgrade head
```

### مشاهده migration های اجرا شده
```bash
alembic history
alembic current
```

## Error Codes

| کد | معنی | وضعیت HTTP |
|----|------|-----------|
| `DUPLICATE_PHONE` | شماره تکراری | 409 |
| `RATE_LIMIT_EXCEEDED` | بیش از حد درخواست | 429 |
| `INVALID_PHONE` | شماره نامعتبر | 400 |
| `INVALID_COMPANY_NAME` | نام شرکت نامعتبر | 400 |
| `SIMILAR_COMPANY_NAME` | هشدار شباهت نام | 201 (با warning) |

## نکات مهم

1. ⚠️ **در محیط Development**: اگر Rate Limit مزاحم است، `TESTING=True` قرار دهید.

2. 📊 **Monitoring**: لاگ‌ها در `backend/security.log` ذخیره می‌شوند.

3. 🔒 **امنیت**: شماره تلفن‌ها در لاگ Hash می‌شوند.

4. 🔄 **Fuzzy Match**: غیرمسدودکننده است - فقط هشدار می‌دهد.

5. ✅ **Production Ready**: تمام استانداردها رعایت شده است.

## پشتیبانی و سوالات

اگر مشکلی پیش آمد:
1. لاگ‌ها را بررسی کنید
2. فایل `DUPLICATE_PREVENTION_IMPLEMENTATION.md` را مطالعه کنید
3. تست‌ها را اجرا کنید تا ببینید کدام قسمت مشکل دارد

---

**موفق باشید! 🚀**

