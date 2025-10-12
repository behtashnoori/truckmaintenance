# سیستم جلوگیری از ثبت‌نام‌های تکراری و نامعتبر

## خلاصه پیاده‌سازی

این سند جزئیات کامل پیاده‌سازی سیستم جامع جلوگیری از ثبت‌نام‌های تکراری و نامعتبر ارائه‌دهندگان سرویس را شرح می‌دهد.

## تغییرات انجام شده

### 1. لایه دیتابیس

#### فایل: `backend/models/provider_application.py`
**تغییرات:**
- افزودن `unique=True` به فیلد `phone_mobile`
- افزودن `index=True` به فیلدهای `phone_mobile`, `company_name`, `created_at`
- افزودن فیلدهای جدید:
  - `reapplication_count`: تعداد دفعات ثبت‌نام مجدد
  - `last_submitted_at`: زمان آخرین ثبت‌نام
  - `fuzzy_match_warning`: آیا هشدار شباهت نام وجود دارد
  - `similar_company_names`: لیست شرکت‌های مشابه

#### فایل: `migrations/versions/add_duplicate_prevention_fields.py`
**ویژگی‌ها:**
- افزودن Unique Constraint روی `phone_mobile`
- افزودن Indexes برای بهبود کارایی جستجو
- مدیریت هوشمند داده‌های تکراری موجود
- Rollback امن در صورت نیاز

### 2. تنظیمات سیستم

#### فایل: `backend/config.py`
**تنظیمات جدید:**
```python
RATE_LIMIT_APPLICATIONS_PER_HOUR = 3  # حداکثر 3 درخواست در ساعت
RATE_LIMIT_ENABLED = True
FUZZY_MATCH_THRESHOLD = 0.8  # حد آستانه شباهت (80%)
DUPLICATE_CHECK_ENABLED = True
PHONE_PATTERN = r'^09\d{9}$'  # فرمت شماره موبایل ایران
SUPPORT_PHONE = '021-12345678'  # شماره تماس پشتیبانی
```

### 3. Validation و Security

#### فایل: `backend/middleware/security.py`
**توابع جدید:**

1. **`sanitize_phone(phone)`**: پاکسازی شماره تلفن
   - حذف فاصله، خط تیره و کاراکترهای غیرضروری
   - تبدیل پیش‌شماره بین‌المللی (+98) به 0

2. **`validate_phone(phone)`**: اعتبارسنجی شماره تلفن
   - بررسی فرمت ایرانی (09XXXXXXXXX)
   - رد شماره‌های تستی و نامعتبر
   - رد شماره‌هایی که تمام ارقام یکسان هستند

3. **`validate_company_name(company_name)`**: اعتبارسنجی نام شرکت
   - بررسی حداقل و حداکثر طول
   - شناسایی الگوهای SQL Injection
   - رد نام‌های دارای کاراکترهای تکراری بیش از حد
   - رد نام‌های فقط عددی

4. **`check_suspicious_patterns(data)`**: شناسایی الگوهای مشکوک
   - تشخیص داده‌های تستی
   - بررسی نام و نام خانوادگی یکسان
   - شناسایی نام‌های خیلی کوتاه

### 4. Rate Limiting

#### فایل: `backend/middleware/rate_limiting.py`
**تابع جدید:**

**`application_rate_limit`**: محدودسازی درخواست‌ها
- حداکثر 3 درخواست در ساعت به ازای هر IP
- پیام خطای واضح با زمان انتظار
- عدم محدودیت در حالت Testing
- پشتیبانی از Proxy Headers (X-Forwarded-For)

### 5. Fuzzy Matching

#### فایل: `backend/utils/fuzzy_match.py`
**قابلیت‌ها:**
- الگوریتم Levenshtein Distance
- محاسبه میزان شباهت بین نام شرکت‌ها
- نرمال‌سازی رشته‌ها (حذف پسوندهای رایج)
- تشخیص نام‌های مشابه با threshold قابل تنظیم

### 6. Backend Routes

#### فایل: `backend/routes/provider_applications.py`
**بهبودها:**

1. **Duplicate Detection:**
   - بررسی تکراری بودن شماره موبایل قبل از ذخیره
   - پیام خطای جامع با اطلاعات تماس پشتیبانی
   - HTTP Status Code 409 (Conflict)

2. **Fuzzy Matching:**
   - مقایسه نام شرکت با شرکت‌های موجود
   - Warning غیرمسدودکننده در صورت شباهت بالا
   - ذخیره لیست شرکت‌های مشابه

3. **Enhanced Logging:**
   - ثبت تمام تلاش‌های تکراری (با Hash شدن شماره تلفن)
   - ثبت نتایج Fuzzy Matching
   - ثبت نقض محدودیت‌های Rate Limit

4. **Error Handling:**
   - مدیریت IntegrityError در سطح دیتابیس
   - پیام‌های خطای ساختاریافته با کد خطا
   - جزئیات کامل برای کاربر

### 7. Frontend API Layer

#### فایل: `src/lib/api.ts`
**Type Definitions جدید:**
```typescript
interface ApiError {
  code?: string;
  message: string;
  action?: string;
  support_contact?: string;
  details?: string;
  retry_after?: number;
  max_attempts?: number;
}

interface ApiWarning {
  code?: string;
  message: string;
  note?: string;
}
```

**بهبود `submitProviderApplication`:**
- مدیریت Response های مختلف
- پشتیبانی از Warning ها
- Error Handling پیشرفته

### 8. Frontend User Interface

#### فایل: `src/pages/ProviderSignup.tsx`
**قابلیت‌های جدید:**

1. **Error Handling پیشرفته:**
   - مدیریت جداگانه هر نوع خطا
   - نمایش پیام‌های فارسی واضح
   - نمایش اطلاعات تماس پشتیبانی

2. **Error Codes پشتیبانی شده:**
   - `DUPLICATE_PHONE`: شماره تکراری
   - `RATE_LIMIT_EXCEEDED`: بیش از حد درخواست
   - `INVALID_PHONE`: شماره نامعتبر
   - `INVALID_COMPANY_NAME`: نام شرکت نامعتبر
   - `NETWORK_ERROR`: خطای شبکه

3. **Warning Display:**
   - نمایش هشدار Fuzzy Match
   - اطلاع‌رسانی شرکت‌های مشابه

### 9. Business Expert Dashboard

#### فایل: `src/pages/business-expert/ApplicationReview.tsx`
**ویژگی‌های جدید:**

1. **Warning Indicators در لیست:**
   - Badge نام مشابه (زرد)
   - Badge درخواست چندباره (آبی)
   - نمایش خلاصه شرکت‌های مشابه

2. **Detail View Warnings:**
   - هشدار کامل نام مشابه با لیست شرکت‌ها
   - نمایش تعداد دفعات درخواست
   - راهنمایی برای کارشناس

### 10. Test Suite

#### فایل: `tests/test_duplicate_prevention.py`
**Test Classes:**

1. **TestDuplicatePhoneNumber:**
   - تست ثبت اولین درخواست
   - تست رد شماره تکراری
   - تست Sanitization شماره تلفن
   - تست مجوز شماره‌های مختلف

2. **TestPhoneValidation:**
   - تست شماره‌های معتبر
   - تست شماره‌های نامعتبر
   - تست الگوهای مختلف

3. **TestFuzzyMatching:**
   - تست هشدار نام مشابه
   - تست عدم هشدار برای نام‌های متفاوت

4. **TestCompanyNameValidation:**
   - تست نام‌های معتبر
   - تست نام‌های نامعتبر
   - تست SQL Injection

5. **TestRateLimiting:**
   - تست محدودیت 3 درخواست
   - تست مسدود شدن درخواست چهارم

6. **TestDatabaseConstraints:**
   - تست Unique Constraint
   - تست IntegrityError

7. **TestApplicationTracking:**
   - تست فیلدهای جدید

## دستورالعمل نصب و راه‌اندازی

### 1. اجرای Migration

```bash
# از ریشه پروژه
cd truckmaintenance

# اجرای migration
alembic upgrade head
```

### 2. بررسی تنظیمات محیط

فایل `.env` یا `backend/db_credentials.py` را بررسی کنید:

```python
# تنظیمات اختیاری
RATE_LIMIT_APPLICATIONS_PER_HOUR=3
RATE_LIMIT_ENABLED=true
FUZZY_MATCH_THRESHOLD=0.8
DUPLICATE_CHECK_ENABLED=true
SUPPORT_PHONE=021-12345678
```

### 3. نصب Dependencies (در صورت نیاز)

```bash
# برای Python
pip install -r requirements.txt

# برای Frontend
npm install
```

### 4. اجرای تست‌ها

```bash
# اجرای تست‌های duplicate prevention
pytest tests/test_duplicate_prevention.py -v

# اجرای تمام تست‌ها
pytest tests/ -v
```

### 5. راه‌اندازی سرورها

```bash
# Backend
python scripts/run_backend.py

# Frontend (در ترمینال جداگانه)
npm run dev
```

## استانداردها و Best Practices پیاده‌سازی شده

### 1. OWASP API Security
- ✅ Input Validation در چند لایه
- ✅ Rate Limiting برای جلوگیری از سوء استفاده
- ✅ پیام‌های خطا بدون افشای اطلاعات حساس
- ✅ Logging امن (Hash شدن داده‌های حساس)

### 2. RESTful API Best Practices
- ✅ استفاده صحیح از HTTP Status Codes
  - 201: Created
  - 400: Bad Request
  - 409: Conflict (برای Duplicate)
  - 429: Too Many Requests
- ✅ فرمت پاسخ یکپارچه
- ✅ Error Code های واضح

### 3. استانداردهای ایرانی
- ✅ فرمت شماره موبایل ایران (09XXXXXXXXX)
- ✅ پیام‌های خطا به فارسی
- ✅ اطلاعات تماس پشتیبانی

### 4. رعایت حریم خصوصی (GDPR-like)
- ✅ Hash کردن شماره تلفن در لاگ‌ها
- ✅ عدم نمایش اطلاعات سایر متقاضیان
- ✅ Logging محدود و هدفمند

## نمونه‌های استفاده

### Backend - بررسی شماره تکراری

```python
# Automatic در endpoint
# اگر شماره تکراری باشد:
{
  "success": false,
  "error": {
    "code": "DUPLICATE_PHONE",
    "message": "این شماره موبایل قبلاً در سیستم ثبت شده است.",
    "action": "لطفاً با شماره دیگری ثبت‌نام کنید یا با پشتیبانی تماس بگیرید.",
    "support_contact": "021-12345678",
    "details": "اگر قبلاً ثبت‌نام کرده‌اید، لطفاً منتظر تماس کارشناس بازرگانی باشید."
  }
}
```

### Backend - هشدار نام مشابه

```python
# اگر نام شرکت شباهت زیادی داشته باشد:
{
  "success": true,
  "message": "درخواست شما با موفقیت ثبت شد",
  "data": {"id": 123, "status": "pending"},
  "warning": {
    "code": "SIMILAR_COMPANY_NAME",
    "message": "نام شرکت شما شباهت زیادی به شرکت‌های موجود در سیستم دارد: شرکت A, شرکت B",
    "note": "اگر این شرکت شما نیست، درخواست شما در حال بررسی است."
  }
}
```

### Frontend - مدیریت خطا

```typescript
const response = await submitProviderApplication(data);

if (response.success) {
  // موفق
  if (response.warning) {
    // نمایش هشدار
  }
} else {
  const error = response.error as ApiError;
  
  switch (error.code) {
    case 'DUPLICATE_PHONE':
      // نمایش پیام تکراری بودن با اطلاعات تماس
      break;
    case 'RATE_LIMIT_EXCEEDED':
      // نمایش پیام محدودیت با زمان انتظار
      break;
    // ...
  }
}
```

## نکات مهم برای توسعه‌دهندگان

### 1. غیرفعال کردن موقت Duplicate Check
```python
# در config یا environment variable
DUPLICATE_CHECK_ENABLED=false
```

### 2. تنظیم Rate Limit برای محیط Development
```python
# تعداد بیشتر برای تست راحت‌تر
RATE_LIMIT_APPLICATIONS_PER_HOUR=100
```

### 3. کاهش Threshold فازی برای تست
```python
# برای تست بهتر fuzzy matching
FUZZY_MATCH_THRESHOLD=0.6  # Default: 0.8
```

### 4. مشاهده لاگ‌ها
```bash
# لاگ‌های duplicate prevention
tail -f backend/security.log | grep "Duplicate"
tail -f backend/security.log | grep "Fuzzy"
tail -f backend/security.log | grep "Rate limit"
```

## مشکلات محتمل و راه‌حل

### 1. خطای Migration
**مشکل:** Migration با خطا مواجه می‌شود.

**راه‌حل:**
```bash
# بررسی وضعیت
alembic current

# برگشت به نسخه قبل
alembic downgrade -1

# اجرای مجدد
alembic upgrade head
```

### 2. داده‌های تکراری موجود
**مشکل:** در دیتابیس شماره‌های تکراری وجود دارد.

**راه‌حل:** Migration به طور خودکار آن‌ها را مدیریت می‌کند و پسوند `_dup_N` اضافه می‌کند.

### 3. Rate Limit در محیط Development مزاحم است
**راه‌حل:**
```python
# در config.py
TESTING = True  # Rate limit غیرفعال می‌شود
```

### 4. Fuzzy Match بیش از حد حساس است
**راه‌حل:**
```python
# افزایش threshold
FUZZY_MATCH_THRESHOLD=0.9  # بجای 0.8
```

## آمار و گزارش‌گیری

### Query های مفید

```sql
-- تعداد درخواست‌های با هشدار fuzzy match
SELECT COUNT(*) FROM provider_application WHERE fuzzy_match_warning = true;

-- لیست شرکت‌های مشابه
SELECT company_name, similar_company_names 
FROM provider_application 
WHERE fuzzy_match_warning = true;

-- درخواست‌های با تعداد بیشتر از 1
SELECT * FROM provider_application WHERE reapplication_count > 1;

-- آمار درخواست‌ها بر اساس تاریخ
SELECT DATE(created_at), COUNT(*) 
FROM provider_application 
GROUP BY DATE(created_at) 
ORDER BY DATE(created_at) DESC;
```

## نتیجه‌گیری

این سیستم یک راه‌حل جامع برای:
- ✅ جلوگیری از ثبت‌نام‌های تکراری
- ✅ اعتبارسنجی کامل داده‌ها
- ✅ محدودسازی درخواست‌ها
- ✅ هشدار به کارشناسان درباره موارد مشکوک
- ✅ تجربه کاربری مناسب با پیام‌های واضح

تمام استانداردهای بین‌المللی و بهترین روش‌های صنعت رعایت شده است.

---

**تاریخ پیاده‌سازی:** 12 اکتبر 2025  
**نسخه:** 1.0.0  
**وضعیت:** آماده به استفاده در Production

