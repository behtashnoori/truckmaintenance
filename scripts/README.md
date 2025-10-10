# Scripts - Truck Maintenance

این پوشه شامل اسکریپت‌های کاربردی و ابزارهای مدیریتی پروژه است.

## 📜 فایل‌های موجود

### 👨‍💼 مدیریت کاربران
- **`create_admin.py`** - ایجاد کاربر ادمین جدید
- **`create_business_expert.py`** - ایجاد کاربر کارشناس تجاری
- **`reset_admin_password.py`** - بازنشانی رمز عبور ادمین

### 🚀 اجرا و استقرار
- **`run_backend.py`** - اجرای سرور backend
- **`celery_worker.py`** - اجرای Celery worker برای پردازش task های پس‌زمینه
- **`celery_beat.py`** - اجرای Celery beat scheduler برای task های زمان‌بندی شده

---

## 🔧 نحوه استفاده

### ایجاد کاربر ادمین
```bash
python scripts/create_admin.py
```

این اسکریپت از شما اطلاعات زیر را می‌پرسد:
- نام کاربری (username)
- ایمیل
- رمز عبور
- نام کامل

### ایجاد کاربر کارشناس تجاری
```bash
python scripts/create_business_expert.py
```

مشابه create_admin، اما با نقش Business Expert.

### بازنشانی رمز عبور ادمین
```bash
python scripts/reset_admin_password.py
```

برای بازیابی دسترسی در صورت فراموشی رمز عبور ادمین.

### اجرای Backend
```bash
python scripts/run_backend.py
```

یا به صورت مستقیم:
```bash
flask --app backend.app run
```

### اجرای Celery Worker
```bash
python scripts/celery_worker.py
```

یا:
```bash
celery -A backend.celery_app worker --loglevel=info
```

### اجرای Celery Beat
```bash
python scripts/celery_beat.py
```

یا:
```bash
celery -A backend.celery_app beat --loglevel=info
```

---

## 📋 پیش‌نیازها

1. **نصب وابستگی‌ها:**
```bash
pip install -r requirements.txt
```

2. **تنظیم دیتابیس:**
   - اطمینان از وجود فایل `backend/db_credentials.py`
   - یا تنظیم متغیر محیطی `SQLALCHEMY_DATABASE_URI`

3. **اعمال مایگریشن‌ها:**
```bash
flask --app backend.app db upgrade
```

---

## ⚙️ تنظیمات محیطی

برخی اسکریپت‌ها ممکن است نیاز به متغیرهای محیطی داشته باشند:

- `FLASK_APP` - مسیر اپلیکیشن Flask
- `FLASK_ENV` - محیط اجرا (development/production)
- `SQLALCHEMY_DATABASE_URI` - اتصال به دیتابیس
- `CELERY_BROKER_URL` - آدرس Redis/RabbitMQ برای Celery
- `CELERY_RESULT_BACKEND` - ذخیره‌سازی نتایج Celery

### مثال (PowerShell):
```powershell
$env:FLASK_APP="backend.app"
$env:FLASK_ENV="development"
```

---

## 🔐 امنیت

- **هرگز** رمزهای عبور را در کد hardcode نکنید
- از متغیرهای محیطی برای اطلاعات حساس استفاده کنید
- فایل `.env` را به `.gitignore` اضافه کنید
- رمزهای عبور قوی برای حساب‌های ادمین استفاده کنید

---

## 📝 نکات

- اسکریپت‌های مدیریت کاربر نیاز به دسترسی مستقیم به دیتابیس دارند
- Celery worker باید همزمان با backend اجرا شود
- برای production، از supervisor یا systemd برای مدیریت process ها استفاده کنید

---

**تاریخ ایجاد:** اکتبر 2025

