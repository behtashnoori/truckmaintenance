# 📚 راهنمای جامع پروژه Truck Maintenance

**تاریخ به‌روزرسانی:** 2025-10-10  
**نسخه:** 2.0 - Complete Implementation

---

## 🎯 خلاصه پروژه

پروژه Truck Maintenance یک سیستم جامع برای مدیریت خدمات اضطراری و تعمیرات خودروهای سنگین است که شامل:

- **Frontend:** React + TypeScript + Vite + Tailwind CSS
- **Backend:** Flask + SQLAlchemy + PostgreSQL
- **Authentication:** JWT-based با Session Management
- **Features:** Admin Panel, Business Expert Panel, Public Pages

---

## 🔐 اطلاعات ورود

### Admin User:
- **Username:** `admin`
- **Password:** `admin123`
- **Role:** `admin`
- **Access:** مدیریت کامل سیستم

### Business Expert User:
- **Username:** `business_expert`
- **Password:** `expert123`
- **Role:** `business_expert`
- **Access:** مدیریت ارائه‌دهندگان و بررسی درخواست‌ها

---

## 🚀 راه‌اندازی سریع

### 1. Backend Setup
```bash
# نصب dependencies
pip install -r requirements.txt

# تنظیم متغیرهای محیطی
$env:FLASK_APP="backend.app:create_app()"
$env:FLASK_ENV="development"

# اجرای migrations
python -m flask db upgrade

# ایجاد کاربران تست
python scripts/create_admin.py
python scripts/create_business_expert.py
python scripts/create_test_data.py

# اجرای سرور
python -m flask run --port 5000
```

### 2. Frontend Setup
```bash
# نصب dependencies
npm install

# اجرای سرور توسعه
npm run frontend
```

### 3. دسترسی
- **Frontend:** http://127.0.0.1:5173
- **Backend:** http://127.0.0.1:5000
- **Admin Panel:** http://127.0.0.1:5173/admin/dashboard
- **Business Expert:** http://127.0.0.1:5173/business-expert/dashboard

---

## 📁 ساختار پروژه

```
truckmaintenance/
├── backend/                    # Flask Backend
│   ├── app/                   # App factory
│   ├── models/                # SQLAlchemy Models
│   ├── routes/                # API Routes
│   ├── middleware/            # Security & Logging
│   ├── services/              # Business Logic
│   └── schemas/               # Validation
│
├── src/                       # React Frontend
│   ├── components/            # 65+ Components
│   ├── pages/                 # 21 Pages
│   ├── services/              # API Services
│   ├── contexts/              # React Contexts
│   └── hooks/                 # Custom Hooks
│
├── scripts/                   # Utility Scripts
│   ├── create_admin.py        # ایجاد ادمین
│   ├── create_business_expert.py  # ایجاد کارشناس
│   └── create_test_data.py    # داده‌های تست
│
├── tests/                     # Test Suite
│   ├── api/                   # API Tests
│   ├── admin/                 # Admin Tests
│   ├── performance/           # Performance Tests
│   └── integration/           # Integration Tests
│
└── docs/                      # Documentation
    ├── test-reports/          # گزارش‌های تست
    ├── improvements/          # بهبودها
    └── api/                   # مستندات API
```

---

## 🎯 ویژگی‌های کلیدی

### ✅ Session Management
- **Auto-logout:** بعد از 30 دقیقه عدم فعالیت
- **Activity tracking:** ردیابی ماوس، کیبورد، تاچ
- **Warning modal:** هشدار 5 دقیقه قبل از انقضا
- **Session extension:** امکان تمدید جلسه
- **Real-time status:** نمایش زمان باقی‌مانده

### ✅ Authentication & Authorization
- **JWT-based:** Token-based authentication
- **Role-based access:** Admin, Business Expert, Public
- **Protected routes:** کنترل دسترسی به صفحات
- **Secure logout:** پاک‌سازی کامل session

### ✅ Admin Panel
- **Dashboard:** آمار و گزارش‌های کلی
- **User Management:** مدیریت کاربران
- **Category Management:** مدیریت دسته‌بندی‌ها
- **Location Management:** مدیریت موقعیت‌ها
- **Vehicle Types:** مدیریت انواع وسایل نقلیه

### ✅ Business Expert Panel
- **Application Review:** بررسی درخواست‌های ثبت‌نام
- **Provider Management:** مدیریت ارائه‌دهندگان
- **Add Provider:** اضافه کردن دستی ارائه‌دهنده
- **Bulk Upload:** آپلود انبوه از Excel
- **Dashboard:** آمار و فعالیت‌های اخیر

### ✅ Public Pages
- **Service Search:** جستجوی خدمات
- **Category Browsing:** مرور دسته‌بندی‌ها
- **Provider Details:** جزئیات ارائه‌دهندگان
- **Provider Registration:** ثبت‌نام ارائه‌دهندگان
- **Location-based Search:** جستجو بر اساس موقعیت

---

## 🧪 راهنمای تست

### تست Session Management
1. **ورود:** با کارشناس وارد شوید
2. **SessionStatus:** badge در sidebar را بررسی کنید
3. **Activity:** ماوس را حرکت دهید
4. **Warning:** منتظر هشدار باشید (یا timeout را کاهش دهید)
5. **Extension:** روی "ادامه کار" کلیک کنید
6. **Logout:** از dropdown menu خروج کنید

### تست Business Expert Panel
1. **Login:** `business_expert` / `expert123`
2. **Dashboard:** آمار و فعالیت‌ها را بررسی کنید
3. **Applications:** درخواست‌های pending را بررسی کنید
4. **Providers:** لیست ارائه‌دهندگان را مدیریت کنید
5. **Add Provider:** ارائه‌دهنده جدید اضافه کنید
6. **Bulk Upload:** فایل Excel آپلود کنید

### تست Public Pages
1. **Services:** دسته‌بندی‌ها را مرور کنید
2. **Search:** خدمات جستجو کنید
3. **Provider Details:** جزئیات ارائه‌دهندگان را ببینید
4. **Registration:** ثبت‌نام جدید انجام دهید

---

## 🔧 اسکریپت‌های مفید

### ایجاد کاربران
```bash
# ایجاد ادمین
python scripts/create_admin.py

# ایجاد کارشناس
python scripts/create_business_expert.py

# ایجاد داده‌های تست
python scripts/create_test_data.py
```

### تست‌ها
```bash
# اجرای همه تست‌ها
pytest tests/

# تست‌های API
pytest tests/api/

# تست‌های عملکرد
pytest tests/performance/

# تست با coverage
pytest tests/ --cov=backend --cov-report=html
```

---

## 📊 آمار پروژه

### Backend
- **Models:** 3+ فایل
- **Routes:** 6+ فایل
- **Middleware:** 4 فایل
- **Services:** 4 فایل
- **Schemas:** 6 فایل

### Frontend
- **Components:** 65+ کامپوننت
- **Pages:** 21 صفحه
- **Hooks:** 2 custom hook
- **Services:** API integration layer

### Tests
- **API Tests:** 5 فایل
- **Admin Tests:** 2 فایل
- **Performance Tests:** 2 فایل
- **Unit Tests:** 2 فایل
- **Integration Tests:** 6 فایل

### Documentation
- **Test Reports:** 19 گزارش
- **Improvements:** 6 سند
- **API Docs:** 8 سند

---

## 🐛 رفع باگ‌های مهم

### ✅ Session Management
- **مشکل:** Router context error
- **راه‌حل:** SessionProvider داخل BrowserRouter قرار گرفت

### ✅ Dropdown Menu
- **مشکل:** دکمه‌های پروفایل، تنظیمات، خروج کار نمی‌کردند
- **راه‌حل:** onClick handlers اضافه شدند

### ✅ Public Pages
- **مشکل:** CategoryProvidersPage کرش می‌کرد
- **راه‌حل:** AdminExpertButtons حذف شد

### ✅ Navigation
- **مشکل:** دکمه‌های بازگشت نامنظم بودند
- **راه‌حل:** Header component بهبود یافت

### ✅ API Endpoints
- **مشکل:** Double-prefixing در public routes
- **راه‌حل:** URL prefixes اصلاح شدند

---

## 🔒 امنیت

### Authentication
- **JWT Tokens:** 24 ساعت اعتبار
- **Session Management:** Auto-logout بعد از عدم فعالیت
- **Role-based Access:** کنترل دسترسی بر اساس نقش
- **Protected Routes:** محافظت از صفحات حساس

### Security Features
- **Rate Limiting:** محدودیت درخواست‌ها
- **Input Validation:** اعتبارسنجی ورودی‌ها
- **SQL Injection Protection:** محافظت از SQL injection
- **XSS Protection:** محافظت از XSS attacks

---

## 📈 Performance

### Frontend
- **Code Splitting:** تقسیم کد برای بارگذاری سریع‌تر
- **Lazy Loading:** بارگذاری تنبل کامپوننت‌ها
- **Optimized Images:** بهینه‌سازی تصاویر
- **Caching:** کش کردن منابع استاتیک

### Backend
- **Database Indexing:** ایندکس‌گذاری جداول
- **Query Optimization:** بهینه‌سازی کوئری‌ها
- **Connection Pooling:** مدیریت اتصالات
- **Caching:** کش کردن نتایج

---

## 🚀 Deployment

### Production Checklist
- [ ] Environment variables تنظیم شوند
- [ ] Database migrations اجرا شوند
- [ ] SSL certificate نصب شود
- [ ] Rate limiting فعال شود
- [ ] Logging پیکربندی شود
- [ ] Monitoring راه‌اندازی شود

### Environment Variables
```env
# Database
SQLALCHEMY_DATABASE_URI=postgresql://user:pass@host:port/db

# Security
SECRET_KEY=your-secret-key
JWT_EXPIRATION_HOURS=24

# Session Management
VITE_SESSION_TIMEOUT_MINUTES=30
VITE_SESSION_WARNING_MINUTES=5

# API
VITE_API_BASE_URL=https://your-api-domain.com
```

---

## 📞 پشتیبانی

### Troubleshooting
1. **Backend Issues:** Log های Flask را بررسی کنید
2. **Frontend Issues:** Console مرورگر را چک کنید
3. **Database Issues:** Connection string را بررسی کنید
4. **Session Issues:** localStorage را پاک کنید

### Common Issues
- **CORS Errors:** Backend CORS settings را بررسی کنید
- **Token Expired:** دوباره login کنید
- **API 404:** URL endpoints را بررسی کنید
- **Database Connection:** Credentials را چک کنید

---

## 📚 منابع بیشتر

### مستندات
- [راهنمای اصلی](README.md)
- [ساختار پروژه](PROJECT_STRUCTURE.md)
- [خلاصه پیاده‌سازی](IMPLEMENTATION_SUMMARY.md)
- [راهنمای امنیتی](SECURITY.md)

### تست‌ها
- [راهنمای تست‌ها](tests/README.md)
- [گزارش‌های تست](docs/test-reports/)
- [بهبودها](docs/improvements/)

### API
- [مستندات API](docs/api/)
- [Schema Validation](docs/api/SCHEMA_VALIDATION_SUMMARY.md)
- [Integration Reports](docs/api/API_INTEGRATION_COMPLETE_REPORT.md)

---

## 🎉 نتیجه‌گیری

پروژه Truck Maintenance با موفقیت پیاده‌سازی شده و آماده استفاده است. تمام ویژگی‌های کلیدی کار می‌کنند و سیستم Session Management برای امنیت بیشتر اضافه شده است.

**وضعیت:** ✅ آماده Production  
**تاریخ:** 2025-10-10  
**نسخه:** 2.0 - Complete Implementation

---

**برای شروع، فایل‌های README مربوطه را مطالعه کنید و سپس با راه‌اندازی سریع شروع کنید.**
