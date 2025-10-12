# گزارش اصلاحات گردش کار ثبت‌نام ارائه‌دهنده

## خلاصه مشکل

کاربر گزارش داد که پس از تایید درخواست‌ها در پنل کارشناس:
- ✅ صفحه اصلی تعداد ارائه‌دهندگان را نشان می‌دهد (مثلاً "1 ارائه‌دهنده")
- ❌ اما با کلیک روی دسته‌بندی، پیام "ثبت‌نامی در این حوزه انجام نشده" نمایش داده می‌شود

## مشکلات شناسایی شده

### 1. Route Confusion (مسیرهای مخلوط شده)
- دو route مختلف برای نمایش دسته‌بندی: `/c/:slug` و `/category/:slug`
- `SearchPage` به مسیر اشتباه navigate می‌کرد
- تبدیل slug برای متن فارسی مشکل داشت

### 2. Distance Filtering (فیلتر فاصله)
- Backend فقط شرکت‌های در شعاع `service_radius_km` را برمی‌گرداند
- برای صفحه لیست دسته‌بندی، باید تمام شرکت‌ها نمایش داده شوند
- مختصات hardcoded در frontend باعث می‌شد شرکت‌های خارج از محدوده نمایش داده نشوند

### 3. Company Name Fields
- Model دارای دو فیلد `name` و `company_name` بود
- ممکن بود یکی null باشد و در نمایش مشکل ایجاد کند

## اصلاحات انجام شده

### 1. ابزارهای تشخیصی ✅

#### `diagnose_workflow.py`
اسکریپت جامع برای بررسی:
- وضعیت Applications (pending/approved/rejected)
- وضعیت Companies (active/inactive)
- لینک Categories با Companies  
- هماهنگی فیلدهای name/company_name
- شبیه‌سازی کوئری API

**اجرا:**
```bash
python diagnose_workflow.py
```

#### `test_complete_workflow.py`
تست خودکار کل گردش کار:
1. ثبت‌نام ارائه‌دهنده
2. ورود کارشناس
3. مشاهده درخواست‌های pending
4. تایید درخواست
5. بررسی شمارش دسته‌بندی‌ها
6. مشاهده لیست ارائه‌دهندگان در دسته
7. مشاهده جزئیات ارائه‌دهنده

**اجرا:**
```bash
python test_complete_workflow.py
```

### 2. اصلاحات Frontend ✅

#### `src/pages/SearchPage.tsx`
```typescript
// قبل:
navigate(`/c/${category}`);  // مسیر اشتباه

// بعد:
const slug = category.replace(/\s+/g, '-');
navigate(`/category/${slug}`);  // مسیر صحیح
```

#### `src/pages/CategoryProvidersPage.tsx`
```typescript
// قبل:
const params = new URLSearchParams({
  lat: '35.6892',  // مختصات ثابت تهران
  lon: '51.3890',
  category: categoryName
});

// بعد:
const params = new URLSearchParams({
  category: categoryName  // فقط دسته‌بندی، بدون مختصات
});
```

### 3. اصلاحات Backend ✅

#### `backend/routes/public.py` - تابع `get_providers()`

تغییرات کلیدی:
1. اگر فقط `category` ارسال شود (بدون lat/lon)، فیلتر فاصله غیرفعال می‌شود
2. از مختصات dummy برای محاسبه فاصله استفاده می‌کند
3. فیلد `name` به `company_name or company.name` تغییر یافت

```python
# اضافه شد:
ignore_distance = request.args.get('ignore_distance', 'false').lower() == 'true'

# اگر category داده شد ولی location نه:
if category and (not lat or not lon):
    ignore_distance = True
    lat = lat or 35.6892
    lon = lon or 51.3890
elif not lat or not lon:
    return jsonify({'success': False, 'error': '...'})

# در حلقه companies:
if not ignore_distance and distance_km > company.service_radius_km:
    continue  # Skip
```

## فایل‌های تغییر یافته

### اسکریپت‌های جدید:
- ✅ `diagnose_workflow.py` - اسکریپت تشخیصی دیتابیس
- ✅ `test_complete_workflow.py` - تست خودکار
- ✅ `WORKFLOW_TESTING_GUIDE.md` - راهنمای تست دستی
- ✅ `WORKFLOW_FIX_SUMMARY.md` - این فایل

### فایل‌های اصلاح شده:
- ✅ `src/pages/SearchPage.tsx` - navigation اصلاح شد
- ✅ `src/pages/CategoryProvidersPage.tsx` - query parameters اصلاح شد
- ✅ `backend/routes/public.py` - لاجیک فیلتر فاصله اصلاح شد

## دستورالعمل اجرا

### مرحله 1: Restart Backend ⚠️ **مهم**
```bash
# Backend را متوقف کنید (Ctrl+C)
# سپس دوباره اجرا کنید:
python scripts/run_backend.py
```

**یا از PowerShell اصلی:**
```powershell
.\start_servers.ps1
```

### مرحله 2: اجرای تست خودکار
```bash
python test_complete_workflow.py
```

**نتیجه مورد انتظار:**
```
✅ ALL TESTS PASSED!

The complete workflow is working correctly:
  1. Provider can submit application ✓
  2. Business expert can log in ✓
  3. Business expert can view pending applications ✓
  4. Business expert can approve applications ✓
  5. Categories show correct company counts ✓
  6. Providers appear in category listings ✓
  7. Provider detail page displays correctly ✓
```

### مرحله 3: تست دستی در مرورگر

1. **ثبت‌نام ارائه‌دهنده:**
   - به `http://localhost:5173/` بروید
   - خدمات → ثبت‌نام ارائه‌دهنده
   - فرم را پر کنید و ارسال کنید

2. **تایید در پنل کارشناس:**
   - دکمه "کارشناس" در گوشه بالا
   - ورود با `business_expert` / `expert123`
   - درخواست‌های در انتظار → بررسی → تایید

3. **بررسی نمایش عمومی:**
   - برگشت به صفحه اصلی
   - خدمات → کلیک روی دسته‌بندی
   - باید لیست ارائه‌دهندگان نمایش داده شود ✅

## بررسی دیتابیس

### اجرای اسکریپت تشخیصی:
```bash
python diagnose_workflow.py
```

### خروجی مورد انتظار:
```
✅ All companies have consistent name fields
✅ No issues found! Database is consistent.

API Query Simulation:
  Category 'تعویض روغن':
    Query returned: 2 companies
      • تعمیرگاه جامع امین (ID: 92)
      • شرکت تست 044046 (ID: 97)
```

## عیب‌یابی

### اگر تست خودکار در Step 6 با خطای "موقعیت جغرافیایی الزامی است" fail شد:

❌ Backend با کد جدید restart نشده است

**راه حل:**
1. Backend را متوقف کنید
2. مطمئن شوید فایل `backend/routes/public.py` تغییرات را دارد
3. Backend را دوباره اجرا کنید
4. تست را دوباره اجرا کنید

### اگر در مرورگر شرکت‌ها نمایش داده نشدند:

1. **Console Browser را بررسی کنید** (F12 → Console)
   - خطای JavaScript؟
   
2. **Network tab را بررسی کنید** (F12 → Network)
   - درخواست به `/api/public/providers?category=...` را پیدا کنید
   - Response چیست؟
   - آیا `data` خالی است یا دارای شرکت‌ها؟

3. **Backend logs را بررسی کنید**
   - خطایی در console backend چاپ شده؟

### اگر درخواست تایید شد ولی Company ایجاد نشد:

```bash
python diagnose_workflow.py
```

بخش "Approved Applications → Company Mapping" را بررسی کنید.
اگر "NO COMPANY FOUND" نمایش داده شد، مشکل در `backend/routes/provider_applications.py` خط 230-254 است.

## نتیجه‌گیری

با این اصلاحات، گردش کار کامل ثبت‌نام باید بدون مشکل کار کند:

1. ✅ ارائه‌دهنده فرم ثبت‌نام را پر می‌کند
2. ✅ کارشناس درخواست را می‌بیند و تایید می‌کند
3. ✅ Company با تمام categories ایجاد می‌شود
4. ✅ صفحه اصلی تعداد صحیح ارائه‌دهندگان را نشان می‌دهد
5. ✅ با کلیک روی دسته، لیست ارائه‌دهندگان نمایش داده می‌شود
6. ✅ با کلیک روی ارائه‌دهنده، جزئیات نمایش داده می‌شود

## بعد از تایید عملکرد

اگر همه چیز کار کرد، فایل‌های test و diagnostic را می‌توانید نگه دارید برای:
- تست regression در آینده
- عیب‌یابی مشکلات جدید
- CI/CD pipeline

