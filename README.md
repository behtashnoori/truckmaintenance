# Truck Maintenance Backend & Frontend

This project delivers a two-part system for locating and registering heavy vehicle service providers:

1. **Flask backend** – Minimal REST API for registering companies.
2. **React frontend** – PWA built with Vite, Tailwind and shadcn/ui for drivers and service providers.

---

## Tech Stack

- Python 3
- Flask & Flask-CORS
- File-based JSON storage (no external database required)
- React + TypeScript + Vite
- Tailwind CSS & shadcn/ui

---

## Repository Layout

```
backend/            # Flask application (app factory, routes, storage helpers)
  app/              # app factory package
  config.py         # basic configuration
  routes/           # API routes
  storage/          # JSON storage utilities
migrations/         # Legacy database migrations (unused)
src/                # React frontend
```

---

## Backend Setup

```bash
# داخل venv
pip install -r requirements.txt

# اجرای توسعه (قابل دسترسی از شبکه)
flask run
# یا
python -m flask run
```

The repository ships with a [`.flaskenv`](./.flaskenv) file so that the
development server automatically binds to `0.0.0.0:5000`. این کار باعث می‌شود
در مرورگری که روی سیستم دیگری باز شده هم بتوانید دکمه «ادامه» را بزنید و
درخواست به سرور برسد.

Data submitted through the API is persisted inside `backend/storage/companies.json`.

Check health:

```bash
curl -X POST http://localhost:5000/company \
  -H 'Content-Type: application/json' \
  -d '{"name": "نمونه", "phone": "09120000000"}'
# {"id": 1, "message": "company created"}
```

---

## Frontend Setup

```bash
npm install
npm run dev
```

The development server runs on `http://localhost:1743`.

The frontend expects the backend on `http://localhost:5000`.

---

## License

MIT
