# Truck Maintenance Backend & Frontend

This project delivers a two-part system for locating and registering heavy vehicle service providers:

1. **Flask backend** – REST API for OTP authentication, provider registration and nearby search.
2. **React frontend** – PWA built with Vite, Tailwind and shadcn/ui for drivers and service providers.

---

## Tech Stack

- Python 3
- Flask, Flask-CORS
- SQLAlchemy 2 with GeoAlchemy2 (SQL Server)
- PyJWT for development JWTs
- Alembic migrations
- React + TypeScript + Vite
- Tailwind CSS & shadcn/ui

---

## Repository Layout

```
app/                # Flask application
  api/              # auth & provider endpoints
  utils/            # aliases, errors, geo helpers
  models.py         # SQLAlchemy models
  config.py         # environment variables
  db.py             # DB session handling
migrations/         # Alembic migration files
scripts/            # seed script
src/                # React frontend
```

---

## Backend Setup

```bash
# داخل venv
pip install -r requirements.txt

# اگر migrations داری:
python -m flask --app backend.app db upgrade

# اگر تازه‌سازی لازم بود (فقط بار اول):
# python -m flask --app backend.app db init
# python -m flask --app backend.app db migrate -m "baseline"
# python -m flask --app backend.app db upgrade

# اجرا
python -m flask --app backend.app run
# یا
flask --app backend.app run
```

Check health:

```bash
curl http://localhost:5000/
# {"status": "ok"}
```

### Seeding Demo Data

Populate example providers for Tehran, Isfahan and Tabriz:

```bash
python -m scripts.seed
```

Example search after seeding:

```bash
http :5000/providers lat==35.72 lon==51.41 category==tyre-wheel vehicleType==semi only24_7==true
```

### OTP Development Flow

```bash
# request a one-time code
curl -X POST /auth/request-otp -d '{"phone":"+98912..."}'

# verify and obtain JWT
dev_code=123456
curl -X POST /auth/verify-otp -d '{"phone":"+98912...","code":"123456"}'

# register provider with the JWT
curl -H 'Authorization: Bearer <token>' -X POST /providers -d '{"name":"...","phone":"+98912...",...}'
```
Each phone can request a new code only every 30 seconds. Codes are valid for five minutes.

### API Overview

| Method & Path                | Description |
|-----------------------------|-------------|
| `POST /auth/request-otp`    | issue development OTP |
| `POST /auth/verify-otp`     | verify OTP and receive JWT |
| `POST /providers`           | register new provider (requires JWT) |
| `GET /providers`            | search nearby providers with optional filters |
| `GET /providers/<id>`       | provider details (optionally include `lat`/`lon` to get `distance_km`) |
| `GET /health`               | service health check |

### Error Format

All errors follow the structure:

```json
{ "error": { "code": "invalid_request", "message": "lat and lon required" } }
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

### Docker

Run the API together with SQL Server Express:

```bash
docker compose up --build
```

Environment variables (`MSSQL_URI`, `JWT_SECRET`, `FRONTEND_ORIGINS`) can be adjusted in `docker-compose.yml`.

---

## Frontend Setup

```bash
npm install
npm run dev
```

The frontend expects the backend on `http://localhost:5000`.

---

## License

MIT
