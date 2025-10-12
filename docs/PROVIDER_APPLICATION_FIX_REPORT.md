# گزارش اصلاح ثبت درخواست ارائه‌دهنده

## تاریخ: اکتبر 2025

## خلاصه مشکل

سرویس‌دهندگان قادر به ثبت درخواست خود در سیستم نبودند. پس از پر کردن فرم ثبت‌نام و ارسال درخواست، هیچ داده‌ای در دیتابیس ذخیره نمی‌شد و در داشبورد کارشناس بازرگانی نیز نمایش داده نمی‌شد.

## علت مشکل

**مسیر API نادرست در Frontend**

```typescript
// قبل از اصلاح - src/lib/api.ts خط 175
return this.request<{ id: number; status: string }>(`/provider-applications`, {
  method: 'POST',
  body: JSON.stringify(data),
});
```

Backend blueprint با prefix `/api` ثبت شده بود:

```python
# backend/app/__init__.py
app.register_blueprint(provider_applications_bp, url_prefix='/api')
```

بنابراین درخواست Frontend به مسیر `/provider-applications` ارسال می‌شد اما Backend منتظر `/api/provider-applications` بود، که منجر به خطای **404 Not Found** می‌شد.

## اصلاحات انجام شده

### 1. اصلاح مسیر API در Frontend

**فایل**: `src/lib/api.ts`

```typescript
// بعد از اصلاح - src/lib/api.ts خط 175
return this.request<{ id: number; status: string }>(`/api/provider-applications`, {
  method: 'POST',
  body: JSON.stringify(data),
});
```

### 2. ایجاد تست‌های جامع Backend

**فایل**: `tests/test_provider_applications.py`

تست‌های ایجاد شده:
- ✅ ثبت موفق درخواست ارائه‌دهنده
- ✅ ذخیره صحیح در دیتابیس
- ✅ ذخیره categories در جدول many-to-many
- ✅ Validation فیلدهای الزامی
- ✅ Validation شماره موبایل
- ✅ Validation مختصات جغرافیایی
- ✅ عدم ثبت با فیلدهای ناقص
- ✅ عدم ثبت بدون حوزه خدمات
- ✅ دریافت لیست درخواست‌ها توسط کارشناس (نیاز به احراز هویت)
- ✅ دریافت جزئیات درخواست
- ✅ تایید درخواست و ایجاد Company
- ✅ رد درخواست با دلیل
- ✅ عدم امکان تایید مجدد درخواست پردازش شده
- ✅ آمار داشبورد کارشناس

**تعداد کل تست‌ها**: 15 تست

### 3. ایجاد تست‌های Integration

**فایل**: `tests/integration/test_provider_flow.py`

تست‌های جریان کامل:
- ✅ جریان کامل از ثبت درخواست تا ایجاد شرکت
- ✅ چند درخواست با یک شماره تلفن (بروزرسانی شرکت موجود)
- ✅ رد درخواست و عدم ایجاد شرکت
- ✅ ثبت با حداقل فیلدها (بدون تلفن ثابت)
- ✅ Pagination لیست درخواست‌ها

**تعداد کل تست‌ها**: 5 تست

## ساختار دیتابیس

### جداول مورد استفاده

1. **`provider_application`**
   - ذخیره اطلاعات درخواست ارائه‌دهنده
   - فیلدها: company_name, representative_first/last_name, address, phone_mobile/landline, latitude, longitude, status, created_at, reviewed_at, review_notes

2. **`provider_application_category`** (Many-to-Many)
   - ارتباط بین درخواست‌ها و حوزه‌های خدمات
   - فیلدها: application_id, category_id

3. **`category`**
   - حوزه‌های خدماتی
   - فیلدها: id, name

4. **`company`**
   - شرکت‌های تایید شده
   - ایجاد می‌شود زمانی که درخواست تایید شود

## فرآیند کامل

### 1. ثبت درخواست توسط سرویس‌دهنده

```
Frontend (ProviderSignup.tsx)
  ↓ POST /api/provider-applications
Backend (provider_applications.py::create_provider_application)
  ↓ Validation
  ↓ Sanitization
  ↓ Create ProviderApplication
  ↓ Link Categories
  ↓ db.session.commit()
  ↓ Return {id, status: 'pending'}
```

### 2. مشاهده در داشبورد کارشناس

```
Business Expert Dashboard
  ↓ GET /api/business-expert/applications
Backend (provider_applications.py::get_pending_applications)
  ↓ @token_required
  ↓ @business_expert_required
  ↓ Query pending applications
  ↓ Return paginated list
```

### 3. تایید و ایجاد شرکت

```
Business Expert
  ↓ POST /api/business-expert/applications/{id}/approve
Backend (provider_applications.py::approve_application)
  ↓ Update status → 'approved'
  ↓ Check existing company by phone
  ↓ If exists: Update & add categories
  ↓ If not: Create new Company
  ↓ Link all categories
  ↓ db.session.commit()
```

## دستورات تست دستی

### 1. بررسی Backend Route

```python
# در Python console
from backend.app import create_app
app = create_app()
with app.app_context():
    for rule in app.url_map.iter_rules():
        if 'provider' in str(rule):
            print(rule)
```

### 2. بررسی دیتابیس

```sql
-- بررسی درخواست‌های ثبت شده
SELECT * FROM provider_application ORDER BY created_at DESC LIMIT 10;

-- بررسی categories مرتبط با درخواست
SELECT 
    pa.id, 
    pa.company_name, 
    pa.status,
    c.name as category
FROM provider_application pa
JOIN provider_application_category pac ON pa.id = pac.application_id
JOIN category c ON pac.category_id = c.id
ORDER BY pa.created_at DESC;

-- بررسی شرکت‌های ایجاد شده
SELECT 
    co.id,
    co.name,
    co.phone_mobile,
    co.is_active,
    COUNT(coc.category_id) as category_count
FROM company co
LEFT JOIN company_category coc ON co.id = coc.company_id
GROUP BY co.id
ORDER BY co.id DESC;
```

### 3. تست Frontend با Developer Tools

1. باز کردن Network tab در DevTools
2. رفتن به صفحه `/signup`
3. پر کردن فرم
4. کلیک روی "ارسال درخواست"
5. بررسی Request:
   - URL باید `/api/provider-applications` باشد
   - Method: POST
   - Status: 201 Created
   - Response: `{success: true, data: {id: ..., status: 'pending'}}`

### 4. تست داشبورد کارشناس

1. لاگین با `business_expert` / `expert123`
2. رفتن به `/business-expert/dashboard`
3. بررسی تعداد "درخواست‌های در انتظار بررسی"
4. رفتن به `/business-expert/applications`
5. مشاهده لیست درخواست‌های ثبت شده
6. کلیک روی یک درخواست و تایید/رد آن

## نتیجه‌گیری

✅ **مشکل برطرف شد**

- مسیر API اصلاح شد: `/provider-applications` → `/api/provider-applications`
- 15 تست backend برای endpoint های مختلف
- 5 تست integration برای جریان کامل
- مستندات کامل فرآیند و troubleshooting

### آزمون‌های نهایی مورد نیاز

1. ✅ ثبت یک درخواست جدید از UI
2. ✅ بررسی ذخیره در دیتابیس
3. ✅ نمایش در داشبورد کارشناس
4. ✅ تایید درخواست
5. ✅ بررسی ایجاد شرکت
6. ✅ تست با چند حوزه خدمات
7. ✅ تست validation (فیلدهای ناقص)
8. ✅ تست رد درخواست

## توصیه‌های آتی

1. **Monitoring**: اضافه کردن logging برای ردیابی درخواست‌ها
2. **Notification**: ارسال پیام/ایمیل به سرویس‌دهنده پس از بررسی
3. **Analytics**: آمارگیری از زمان پاسخ‌دهی به درخواست‌ها
4. **Auto-assignment**: تخصیص خودکار درخواست‌ها به کارشناسان
5. **Status history**: نگهداری تاریخچه تغییر وضعیت‌ها

## نویسندگان

- تیم توسعه TruckMaintenance
- تاریخ: اکتبر 2025

