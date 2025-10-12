# گزارش رفع مشکل Migration و ذخیره‌سازی ثبت نام ارائه‌دهندگان

**تاریخ:** 2025-10-12
**وضعیت:** ✅ حل شده

## شرح مشکل

ثبت نام توسط ارائه‌دهندگان سرویس انجام می‌شد ولی داده‌ها در دیتابیس ذخیره نمی‌شدند.

### علت اصلی

Migration مربوط به تغییر ساختار جدول `provider_application` اجرا نشده بود:
- جدول `category` وجود نداشت
- جدول رابط `provider_application_category` (many-to-many) وجود نداشت
- ستون قدیمی `service_domain` هنوز در جدول باقی بود

## راه‌حل اعمال شده

### 1. اصلاح Migration

فایل: `migrations/versions/add_application_categories.py`

**تغییرات:**
- تغییر `down_revision` از `sync_company_schema` به `create_vehicle_type_table`
- اضافه کردن بررسی وجود جداول قبل از ایجاد (برای جلوگیری از خطای duplicate)
- اضافه کردن بررسی وجود ستون `service_domain` قبل از migration
- اضافه کردن بررسی وجود رکورد قبل از insert در جدول رابط

### 2. اجرای Migration

```bash
alembic upgrade head
```

نتیجه: Migration با موفقیت اجرا شد و ساختار دیتابیس به‌روز شد.

## تست‌های انجام شده

### ✅ Test 1: ساختار دیتابیس
- جدول `provider_application` با ساختار جدید
- جدول `category` ایجاد شده
- جدول رابط `provider_application_category` ایجاد شده
- ستون قدیمی `service_domain` حذف شده

### ✅ Test 2: API Endpoint
- ارسال درخواست POST به `/api/provider-applications`
- دریافت پاسخ 201 Created
- دریافت ID درخواست جدید

### ✅ Test 3: ذخیره‌سازی در دیتابیس
- درخواست با موفقیت در جدول `provider_application` ذخیره شد
- اطلاعات شرکت به درستی ثبت شد
- دسته‌بندی‌های خدماتی به درخواست لینک شدند

### ✅ Test 4: مدیریت Categories
- دسته‌بندی‌های جدید خودکار ایجاد می‌شوند
- دسته‌بندی‌های موجود استفاده مجدد می‌شوند
- ارتباط many-to-many به درستی کار می‌کند

## ساختار نهایی دیتابیس

### جدول `provider_application`
```sql
- id (INTEGER, PRIMARY KEY)
- company_name (VARCHAR(255))
- representative_first_name (VARCHAR(100))
- representative_last_name (VARCHAR(100))
- address (TEXT)
- phone_mobile (VARCHAR(20))
- phone_landline (VARCHAR(20))
- latitude (FLOAT)
- longitude (FLOAT)
- status (VARCHAR(50))
- created_at (TIMESTAMP)
- reviewed_by (INTEGER, FK -> users.id)
- reviewed_at (TIMESTAMP)
- review_notes (TEXT)
- is_approved (BOOLEAN)
```

### جدول `category`
```sql
- id (INTEGER, PRIMARY KEY)
- name (VARCHAR(100), UNIQUE)
- icon (VARCHAR(50))
- description (TEXT)
- is_active (BOOLEAN)
```

### جدول رابط `provider_application_category`
```sql
- application_id (INTEGER, FK -> provider_application.id)
- category_id (INTEGER, FK -> category.id)
- PRIMARY KEY (application_id, category_id)
```

## نتیجه نهایی

✅ **همه تست‌ها با موفقیت انجام شد:**
- ثبت نام ارائه‌دهندگان کار می‌کند
- داده‌ها در دیتابیس ذخیره می‌شوند
- دسته‌بندی‌های خدماتی به درستی مدیریت می‌شوند
- ارتباط many-to-many به درستی عمل می‌کند

## فایل‌های تغییر یافته

1. `migrations/versions/add_application_categories.py` - اصلاح و بهبود migration
2. `backend/models/provider_application.py` - بدون تغییر (قبلاً درست بود)
3. `backend/routes/provider_applications.py` - بدون تغییر (قبلاً درست بود)

## توصیه‌ها

1. ✅ Migration با موفقیت اجرا شده و نیازی به کار دیگری نیست
2. 🗑️ جدول قدیمی `provider_applications` (plural) می‌تواند حذف شود (خالی است)
3. 📝 در صورت نیاز به تغییرات آینده، migration های جدید باید از `add_application_categories` به عنوان parent استفاده کنند

## نمونه درخواست ثبت نام

```json
POST /api/provider-applications
{
  "companyName": "شرکت حمل و نقل",
  "representativeFirstName": "علی",
  "representativeLastName": "محمدی",
  "address": "تهران، خیابان ولیعصر",
  "phoneMobile": "09123456789",
  "phoneLandline": "02112345678",
  "serviceCategories": ["حمل بار", "تعمیرات"],
  "latitude": 35.6892,
  "longitude": 51.3890
}
```

**پاسخ موفق:**
```json
{
  "success": true,
  "message": "درخواست شما با موفقیت ثبت شد",
  "data": {
    "id": 74,
    "status": "pending"
  }
}
```

