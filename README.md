# Truck Maintenance Backend & Frontend

This project delivers a two-part system for locating and registering heavy vehicle service providers:

1. **Flask backend** – REST API for OTP authentication, provider registration and nearby search.
2. **React frontend** – PWA built with Vite, Tailwind and shadcn/ui for drivers and service providers.

---

## Tech Stack

- Python 3
- Flask, Flask-CORS
- SQLAlchemy 2 (SQL Server via pyodbc)
- Alembic (Flask-Migrate)
- React + TypeScript + Vite
- Tailwind CSS & shadcn/ui
- Neshan Maps API (Navigation & Routing)

---

## Key Features

### 🗺️ Neshan Navigation Integration
- **Smart Device Detection**: Automatically detects mobile/desktop devices
- **Deep Links Support**: Opens Neshan app on mobile (Android/iOS) if installed
- **Automatic Fallback**: Falls back to web version if app is not installed
- **Real-time Routing**: Calculates actual route distance and duration using Neshan API
- **User Location**: Gets user's current location for accurate navigation
- **Cross-platform**: Works seamlessly on mobile (iOS/Android) and desktop

📖 **Documentation**: 
- [Neshan Setup Guide](NESHAN_SETUP.md) - Complete setup and API documentation
- [User Guide](docs/NAVIGATION_USER_GUIDE.md) - Step-by-step navigation guide
- [Test Navigation](test_navigation.html) - Interactive testing page

---

## Repository Layout

```
backend/            # Flask application (app factory, models, routes)
  app/              # app factory package
  config.py         # environment variables
  models/           # SQLAlchemy models
  routes/           # API routes (blueprints)
migrations/         # Flask-Migrate files
src/                # React frontend
scripts/            # Utility scripts and CLI tools
  create_admin.py   # Create admin user
  celery_worker.py  # Celery background worker
  run_backend.py    # Run backend server
tests/              # Test suite (organized by type)
  api/              # API endpoint tests
  admin/            # Admin panel tests
  performance/      # Performance tests
  unit/             # Unit tests
  integration/      # Integration tests
docs/               # Documentation and reports
  test-reports/     # Test reports
  improvements/     # Improvement documentation
  api/              # API documentation
```

---

## Quick Start

```bash
# 1. کلون کردن پروژه و ورود به فولدر
git clone <repository-url>
cd truckmaintenance

# 2. نصب dependencies
pip install -r requirements.txt
npm install

# 3. تنظیم دیتابیس (اختیاری)
# cp backend/db_credentials.example.py backend/db_credentials.py
# ویرایش فایل db_credentials.py با اطلاعات دیتابیس خود

# 4. اعمال migrations
python -m flask --app backend.app db upgrade

# 5. ایجاد کاربر ادمین
python scripts/create_admin.py

# 6. اجرای پروژه (دو ترمینال)
# ترمینال 1 - Frontend:
npm run frontend

# ترمینال 2 - Backend:
npm run backend
```

---

## Backend Setup

```bash
# ابتدا وارد فولدر پروژه شوید
cd truckmaintenance

# داخل venv
pip install -r requirements.txt

# تنظیم دیتابیس PostgreSQL (اختیاری)
# مشخصات دیتابیس در backend/db_credentials.py قابل تغییر است
# ابتدا فایل نمونه را کپی کنید:
# cp backend/db_credentials.example.py backend/db_credentials.py
# سپس اطلاعات دیتابیس خود را در آن وارد کنید
# یا از متغیرهای محیطی استفاده کنید:
# $env:SQLALCHEMY_DATABASE_URI="postgresql://user:pass@host:port/Marketplace"

# اعمال مایگریشن‌ها (اگر migrations موجود است)
python -m flask --app backend.app db upgrade

# اگر بار اول است:
# python -m flask --app backend.app db init
# python -m flask --app backend.app db migrate -m "baseline"
# python -m flask --app backend.app db upgrade

# اجرا (پورت قابل‌تغییر با FLASK_RUN_PORT)
# مثال: در PowerShell
# $env:FLASK_RUN_PORT=5001
python -m flask --app backend.app run
# یا
flask --app backend.app run
```

Check health:

```bash
curl http://localhost:5000/
# {"status": "ok"}
```

### Available API (current)

| Method & Path     | Description            |
|-------------------|------------------------|
| `POST /company`   | Create a company       |

### Error Format

Errors generally follow:

```json
{ "error": "message" }
```

### Pagination

If the `page` query parameter is supplied to `/providers`, results are wrapped as:

```json
{
  "items": [ ... ],
  "page": 1,
  "page_size": 20,
  "total": 123
}
```

---

## Frontend Setup (separate terminal)

```bash
# ابتدا وارد فولدر پروژه شوید
cd truckmaintenance

npm install

# تنظیم متغیرها (اختیاری)
# پورت و هاست فرانت (پیش‌فرض: 127.0.0.1:5173)
# PowerShell:
#   $env:VITE_HOST="127.0.0.1"; $env:VITE_PORT="5174"
# URL بکند برای فرانت (پیش‌فرض: http://localhost:5000)
#   $env:VITE_API_BASE_URL="http://localhost:5000"

# اجرای فرانت (ترمینال 1)
npm run frontend

# اجرای بکند (ترمینال 2)
# (برای تغییر پورت بکند: $env:FLASK_RUN_PORT="5001")
npm run backend
```

The Vite development server defaults to `http://127.0.0.1:5173` (auto-fallback if busy). The Flask backend defaults to `http://localhost:5000`.

---

## Utility Scripts

The project includes several utility scripts for common tasks. See [scripts/README.md](scripts/README.md) for details.

### Create Admin User
```bash
cd truckmaintenance
python scripts/create_admin.py
```

### Create Business Expert User
```bash
cd truckmaintenance
python scripts/create_business_expert.py
```

### Reset Admin Password
```bash
cd truckmaintenance
python scripts/reset_admin_password.py
```

### Run Celery Worker
```bash
cd truckmaintenance
python scripts/celery_worker.py
```

---

## Testing

The project includes a comprehensive test suite organized by test type. See [tests/README.md](tests/README.md) for details.

### Run All Tests
```bash
cd truckmaintenance
pytest tests/
```

### Run Specific Test Categories
```bash
cd truckmaintenance
pytest tests/api/          # API tests
pytest tests/admin/        # Admin panel tests
pytest tests/performance/  # Performance tests
pytest tests/unit/         # Unit tests
pytest tests/integration/  # Integration tests
```

### Run with Coverage
```bash
cd truckmaintenance
pytest tests/ --cov=backend --cov-report=html
```

---

## Documentation

All project documentation, test reports, and improvement documents are organized in the `docs/` directory:

- **docs/test-reports/** - Test reports (API, Authentication, Performance, etc.)
- **docs/improvements/** - Improvement and enhancement documentation
- **docs/api/** - API integration and feature documentation

For more details, see [docs/README.md](docs/README.md).

---

## Notes

- Database credentials are stored in `backend/db_credentials.py` and can be overridden with environment variables like `SQLALCHEMY_DATABASE_URI`.
- Ports are configurable via env:
  - Frontend: `VITE_HOST`, `VITE_PORT`, `VITE_API_BASE_URL`
  - Backend: `FLASK_RUN_PORT` (or pass `--port` to flask run)
- Ensure `VITE_API_BASE_URL` points to the backend URL/port you run.

---

## License

MIT
