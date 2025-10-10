# ساختار پروژه Truck Maintenance

این سند نمای کلی از ساختار و سازماندهی پروژه را ارائه می‌دهد.

## 📁 ساختار کلی

```
truckmaintenance/
├── backend/                    # Flask Backend Application
│   ├── app/                    # App factory package
│   ├── config.py              # تنظیمات و پیکربندی
│   ├── middleware/            # Middleware ها (logging, rate limiting, security)
│   ├── models/                # SQLAlchemy Models
│   ├── routes/                # API Routes (Blueprints)
│   ├── schemas/               # Validation Schemas
│   └── services/              # Business Logic Layer
│
├── src/                       # React Frontend Application
│   ├── components/            # React Components (65+ components)
│   ├── contexts/              # React Contexts
│   ├── hooks/                 # Custom Hooks
│   ├── pages/                 # Page Components (21 pages)
│   ├── services/              # API Services
│   └── utils/                 # Utility Functions
│
├── scripts/                   # 🆕 Utility Scripts & CLI Tools
│   ├── create_admin.py        # ایجاد کاربر ادمین
│   ├── create_business_expert.py  # ایجاد کاربر کارشناس
│   ├── reset_admin_password.py    # بازنشانی رمز عبور
│   ├── run_backend.py         # اجرای Backend
│   ├── celery_worker.py       # Celery Worker
│   ├── celery_beat.py         # Celery Beat Scheduler
│   └── README.md              # راهنمای Scripts
│
├── tests/                     # 🆕 Test Suite (18 فایل تست)
│   ├── api/                   # API Endpoint Tests (5 فایل)
│   │   ├── test_api_integration.py
│   │   ├── test_auth_api.py
│   │   ├── test_backend_api.py
│   │   ├── test_business_expert_api.py
│   │   └── test_public_routes.py
│   │
│   ├── admin/                 # Admin Panel Tests (2 فایل)
│   │   ├── test_admin_comprehensive.py
│   │   └── test_admin_panel.py
│   │
│   ├── performance/           # Performance Tests (2 فایل)
│   │   ├── test_performance.py
│   │   └── test_performance_optimized.py
│   │
│   ├── unit/                  # Unit Tests (2 فایل)
│   │   ├── test_edge_cases_unit.py
│   │   └── test_service_layer.py
│   │
│   ├── integration/           # Integration Tests (6 فایل)
│   │   ├── test_backward_compatibility.py
│   │   ├── test_company_management.py
│   │   ├── test_edge_cases.py
│   │   ├── test_error_handling.py
│   │   ├── test_pagination.py
│   │   └── test_schema_validation.py
│   │
│   ├── conftest.py            # Pytest Configuration & Fixtures
│   ├── test_debug.py          # Debug Tests
│   └── README.md              # راهنمای تست‌ها
│
├── docs/                      # 🆕 Documentation & Reports (33 فایل)
│   ├── test-reports/          # گزارش‌های تست (19 فایل)
│   │   ├── ADMIN_PANEL_TEST_REPORT.md
│   │   ├── API_INTEGRATION_TEST_REPORT.md
│   │   ├── AUTH_TEST_REPORT.md
│   │   ├── PERFORMANCE_TEST_REPORT.md
│   │   ├── FINAL_TEST_REPORT.md
│   │   └── ... (و 14 فایل دیگر)
│   │
│   ├── improvements/          # گزارش بهبودها (6 فایل)
│   │   ├── BACKWARD_COMPATIBILITY_IMPROVEMENTS.md
│   │   ├── REDIS_FALLBACK_IMPROVEMENTS.md
│   │   ├── IMPROVEMENTS_REPORT.md
│   │   └── ... (و 3 فایل دیگر)
│   │
│   ├── api/                   # مستندات API (8 فایل)
│   │   ├── API_COMPANY_MANAGEMENT.md
│   │   ├── API_INTEGRATION_COMPLETE_REPORT.md
│   │   ├── BUSINESS_EXPERT_PANEL_FINAL_REPORT.md
│   │   └── ... (و 5 فایل دیگر)
│   │
│   └── README.md              # راهنمای مستندات
│
├── migrations/                # Database Migrations (Alembic/Flask-Migrate)
│   └── versions/              # Migration Files
│
├── dist/                      # Production Build Output
├── public/                    # Static Assets
├── instance/                  # Instance-specific files (DB, etc.)
│
├── README.md                  # 📘 راهنمای اصلی پروژه
├── SECURITY.md                # 🔒 راهنمای امنیتی
├── PROJECT_STRUCTURE.md       # 📋 این فایل
├── pytest.ini                 # تنظیمات Pytest
├── requirements.txt           # Python Dependencies
├── package.json               # Node.js Dependencies
└── vite.config.ts            # Vite Configuration

```

## 📊 آمار پروژه

### Backend
- **Models:** 3+ فایل (User, Company, Provider Application)
- **Routes:** 6+ فایل (Auth, Admin, Company, Provider, Public)
- **Middleware:** 4 فایل (Logging, Rate Limiting, Security)
- **Services:** 4 فایل (Business Logic Layer)
- **Schemas:** 6 فایل (Validation)

### Frontend
- **Components:** 65+ کامپوننت React
- **Pages:** 21 صفحه
- **Hooks:** 2 custom hook
- **Services:** API integration layer

### Tests
- **API Tests:** 5 فایل
- **Admin Tests:** 2 فایل
- **Performance Tests:** 2 فایل
- **Unit Tests:** 2 فایل
- **Integration Tests:** 6 فایل
- **جمع:** 18 فایل تست

### Documentation
- **Test Reports:** 19 گزارش
- **Improvements:** 6 سند
- **API Docs:** 8 سند
- **جمع:** 33+ سند

### Scripts
- **Admin Tools:** 3 فایل
- **Runtime Scripts:** 3 فایل
- **جمع:** 6 فایل utility

## 🎯 اهداف سازماندهی

✅ **تمیز و منظم:** همه فایل‌ها در پوشه‌های مناسب دسته‌بندی شده‌اند

✅ **قابل یافتن:** هر نوع فایل جای مشخصی دارد

✅ **مستندسازی شده:** هر پوشه یک README دارد

✅ **حرفه‌ای:** ساختار استاندارد و قابل نگهداری

## 📚 راهنماهای بیشتر

برای اطلاعات بیشتر هر بخش، به فایل‌های README مربوطه مراجعه کنید:

- [راهنمای اصلی پروژه](README.md)
- [راهنمای تست‌ها](tests/README.md)
- [راهنمای Scripts](scripts/README.md)
- [راهنمای مستندات](docs/README.md)
- [راهنمای امنیتی](SECURITY.md)

---

**تاریخ سازماندهی:** اکتبر 2025  
**نسخه:** 2.0 - Organized Structure

