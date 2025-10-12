# مراحل عیب‌یابی ثبت درخواست ارائه‌دهنده

## مرحله 1: بررسی سرور Backend

### 1.1 آیا سرور در حال اجرا است؟

```bash
# در یک terminal:
python scripts/run_backend.py
```

باید پیام‌های زیر را ببینید:
```
* Running on http://127.0.0.1:5000
* Running on http://[::]:5000
```

### 1.2 تست مستقیم Endpoint

```bash
# در terminal دیگر:
python debug_provider_endpoint.py
```

اگر خطای "CONNECTION ERROR" دیدید → سرور backend اجرا نیست

## مرحله 2: بررسی Frontend

### 2.1 آیا تغییرات build شده‌اند؟

```bash
# اگر از build استفاده می‌کنید:
npm run build

# اگر از dev server استفاده می‌کنید، آن را restart کنید:
# Ctrl+C و سپس:
npm run dev
```

### 2.2 Clear Cache مرورگر

1. F12 → Network tab را باز کنید
2. "Disable cache" را فعال کنید
3. صفحه را Refresh کنید (Ctrl+F5)

## مرحله 3: تست از طریق UI

### 3.1 باز کردن Developer Tools

1. F12 در مرورگر
2. به تب Network بروید
3. فیلتر را روی "Fetch/XHR" بگذارید

### 3.2 ثبت درخواست

1. به `/signup` بروید
2. فرم را پر کنید
3. کلیک روی "ارسال درخواست"
4. در Network tab دنبال این موارد بگردید:
   - نام: `provider-applications`
   - Method: `POST`
   - Status: `201` (موفق) یا `4xx/5xx` (خطا)

### 3.3 بررسی Response

اگر Status Code قرمز است (404, 500, etc.):
- روی request کلیک کنید
- تب "Response" را ببینید
- پیام خطا را کپی کنید

## مرحله 4: چک کردن Console Errors

در Developer Tools → Console:
- آیا خطای قرمزی هست؟
- متن خطا را کپی کنید

## مرحله 5: بررسی دیتابیس

```sql
-- باز کردن دیتابیس
# اگر SQLite:
sqlite3 instance/truckmaintenance.db

# اگر PostgreSQL:
psql -U your_username -d truckmaintenance

-- بررسی جداول
.tables  -- (در SQLite)
\dt      -- (در PostgreSQL)

-- آیا جدول provider_application وجود دارد؟
SELECT * FROM provider_application LIMIT 5;

-- بررسی آخرین رکوردها
SELECT id, company_name, phone_mobile, status, created_at 
FROM provider_application 
ORDER BY created_at DESC 
LIMIT 10;
```

## مرحله 6: بررسی Logs

### Backend Logs

در terminal که backend را اجرا کرده‌اید، دنبال این موارد بگردید:

```
# درخواست موفق:
127.0.0.1 - - [date] "POST /api/provider-applications HTTP/1.1" 201 -

# خطا:
127.0.0.1 - - [date] "POST /api/provider-applications HTTP/1.1" 500 -
ERROR in app: ...
```

## حالت‌های مختلف خطا و راه‌حل

### خطا 404 Not Found

**علت**: مسیر API اشتباه است

**راه‌حل**:
1. بررسی کنید URL در Network tab دقیقاً `/api/provider-applications` است
2. بررسی کنید که `src/lib/api.ts` خط 175 شامل `/api/` است

### خطا 400 Bad Request

**علت**: داده‌های ارسالی نامعتبر هستند

**راه‌حل**:
1. بررسی Response body در Network tab
2. مطمئن شوید همه فیلدهای الزامی پر شده‌اند:
   - companyName
   - representativeFirstName
   - representativeLastName
   - address
   - phoneMobile
   - serviceCategories (حداقل 1 آیتم)
   - latitude
   - longitude

### خطا 500 Internal Server Error

**علت**: خطا در سمت backend

**راه‌حل**:
1. بررسی backend logs
2. بررسی کنید دیتابیس در دسترس است
3. بررسی کنید migrations اجرا شده‌اند:
   ```bash
   flask db upgrade
   # یا
   python -m flask db upgrade
   ```

### خطا CORS

**علت**: مشکل Cross-Origin

**بررسی**:
```
Access to fetch at 'http://localhost:5000/api/provider-applications' from origin 
'http://localhost:5173' has been blocked by CORS policy
```

**راه‌حل**:
- در `backend/app/__init__.py` CORS درست تنظیم شده است
- سرور را restart کنید

## چک‌لیست سریع

- [ ] Backend server در حال اجرا است؟
- [ ] Frontend dev server/build در حال اجرا است؟
- [ ] Cache مرورگر clear شده؟
- [ ] Network tab باز است و request را نشان می‌دهد؟
- [ ] Status code درخواست چیست؟
- [ ] جدول provider_application در دیتابیس وجود دارد؟
- [ ] Migrations اجرا شده‌اند؟

## دستور خلاصه برای تست سریع

```bash
# Terminal 1: Backend
python scripts/run_backend.py

# Terminal 2: تست endpoint
python debug_provider_endpoint.py

# Terminal 3: Frontend (اختیاری)
npm run dev
```

## اگر همه چیز OK بود اما هنوز کار نمی‌کند

لطفاً موارد زیر را به من بدهید:

1. Output از `python debug_provider_endpoint.py`
2. Screenshot از Network tab (درخواست provider-applications)
3. Screenshot از Console errors
4. Output از backend logs (چند خط آخر)
5. نتیجه SQL query: `SELECT COUNT(*) FROM provider_application;`

با این اطلاعات می‌توانم دقیقاً بگویم مشکل کجاست.

