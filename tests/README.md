# Test Suite - Truck Maintenance

این پوشه شامل تمام تست‌های پروژه است که به صورت منظم دسته‌بندی شده‌اند.

## 📂 ساختار تست‌ها

### 🔌 api/
تست‌های API endpoint ها و درخواست‌های HTTP:
- `test_api_integration.py` - تست یکپارچه‌سازی API
- `test_auth_api.py` - تست احراز هویت و OTP
- `test_backend_api.py` - تست‌های عمومی backend API
- `test_business_expert_api.py` - تست API کارشناسان تجاری
- `test_public_routes.py` - تست مسیرهای عمومی

**تعداد:** 5 فایل تست

### 👨‍💼 admin/
تست‌های پنل مدیریت و عملکرد ادمین:
- `test_admin_comprehensive.py` - تست جامع پنل ادمین
- `test_admin_panel.py` - تست عملکرد پنل ادمین

**تعداد:** 2 فایل تست

### ⚡ performance/
تست‌های عملکرد، سرعت و بار سیستم:
- `test_performance.py` - تست‌های عملکرد پایه
- `test_performance_optimized.py` - تست‌های عملکرد بهینه‌شده

**تعداد:** 2 فایل تست

### 🧪 unit/
تست‌های واحد برای کامپوننت‌های مجزا:
- `test_edge_cases_unit.py` - تست موارد خاص و Edge Cases
- `test_service_layer.py` - تست لایه سرویس

**تعداد:** 2 فایل تست

### 🔗 integration/
تست‌های یکپارچه‌سازی و workflow های کامل:
- `test_backward_compatibility.py` - تست سازگاری با نسخه‌های قبلی
- `test_company_management.py` - تست مدیریت شرکت‌ها
- `test_edge_cases.py` - تست موارد خاص یکپارچه
- `test_error_handling.py` - تست مدیریت خطاها
- `test_pagination.py` - تست صفحه‌بندی
- `test_schema_validation.py` - تست اعتبارسنجی Schema

**تعداد:** 6 فایل تست

### 🐛 root/
- `test_debug.py` - تست‌های دیباگ و توسعه

---

## 🚀 اجرای تست‌ها

### اجرای همه تست‌ها
```bash
pytest tests/
```

### اجرای تست‌های یک دسته خاص
```bash
# تست‌های API
pytest tests/api/

# تست‌های پنل ادمین
pytest tests/admin/

# تست‌های عملکرد
pytest tests/performance/

# تست‌های واحد
pytest tests/unit/

# تست‌های یکپارچه‌سازی
pytest tests/integration/
```

### اجرای یک فایل تست خاص
```bash
pytest tests/api/test_auth_api.py
```

### اجرای با verbose و coverage
```bash
pytest tests/ -v --cov=backend --cov-report=html
```

---

## 📊 آمار تست‌ها

- **مجموع فایل‌های تست:** 18 فایل
- **دسته‌بندی:** 5 دسته اصلی + 1 فایل debug
- **پوشش:** API, Admin, Performance, Unit, Integration

---

## 🔧 پیش‌نیازها

برای اجرای تست‌ها نیاز است که:

1. وابستگی‌ها نصب شده باشند:
```bash
pip install -r requirements.txt
```

2. دیتابیس تست راه‌اندازی شده باشد

3. متغیرهای محیطی لازم تنظیم شده باشند

---

## 📝 نکات

- تست‌های performance ممکن است زمان‌بر باشند
- برای تست‌های API، مطمئن شوید backend در حال اجرا است
- فایل `conftest.py` شامل fixture های مشترک است (در صورت وجود)
- گزارش‌های تست در پوشه `docs/test-reports/` قرار دارند

---

**آخرین به‌روزرسانی:** اکتبر 2025

